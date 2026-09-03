"""串联旅行内容、地图事实和规划模型，生成可持久化的完整行程。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
import json
import math
from typing import Any

from loguru import logger

from app.models.hotel import Hotel, HotelSearchCriteria
from app.models.route import RouteQuery
from app.models.trip import (
    TripBudget,
    TripDay,
    TripMeal,
    TripPlan,
    TripPlanningRequest,
    TripRouteSegment,
)
from app.models.weather import WeatherForecast
from app.models.xhs import AttractionCandidate, XHSExtraction
from app.services.attraction_extractor import (
    AttractionAuthenticationRequiredError,
    AttractionExtractionError,
    extract_attractions_with_metadata,
)
from app.services.hotel_service import HotelService, HotelServiceError
from app.services.llm_service import LLMService, LLMServiceError, parse_json_object
from app.services.route_service import RouteService, RouteServiceError
from app.services.weather_service import WeatherService, WeatherServiceError
from app.storage.trip_repository import TripRepository, TripRepositoryError


class TripPlanningError(RuntimeError):
    """主流程无法继续时返回的稳定业务异常。"""

    error_code = "TRIP_PLANNING_FAILED"


class TripPlanningAuthenticationRequiredError(TripPlanningError):
    """系统内容账号失效，需要管理员恢复登录态。"""

    error_code = "XHS_AUTH_REQUIRED"


class TripPlanningModelError(TripPlanningError):
    """规划模型不可用或连续返回无效结构。"""

    error_code = "TRIP_LLM_ERROR"


class TripPlanningValidationError(TripPlanningError):
    """生成结果未通过日期、地点、路线或预算校验。"""

    error_code = "TRIP_VALIDATION_ERROR"


@dataclass
class CityPlanningFacts:
    """一个城市进入行程编排前已经确认的旅行事实。"""

    extraction: XHSExtraction
    weather: list[WeatherForecast]
    hotels: list[Hotel]


def _text(value: Any, default: str, max_length: int = 1000) -> str:
    """把模型文本限制在业务字段允许的长度内。"""
    normalized = str(value or "").strip()
    return (normalized or default)[:max_length]


def _cost(value: Any) -> float:
    """把模型提供的餐饮预算限制为可接受的非负金额。"""
    try:
        return min(5000, max(0, round(float(value or 0), 2)))
    except (TypeError, ValueError):
        return 0


class TripPlanComposer:
    """让模型决定每日顺序和建议，再用已确认事实重建结果。"""

    def __init__(self, llm: LLMService | None = None):
        """允许测试注入固定模型响应；真实客户端延迟到首次规划时创建。"""
        self.llm = llm

    def compose(
        self,
        request: TripPlanningRequest,
        facts: dict[str, CityPlanningFacts],
        *,
        plan_id: str,
        warnings: list[str],
    ) -> TripPlan:
        """生成模型草案，并在一次重试后返回经过来源约束的行程。"""
        prompt = self._prompt(request, facts)
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                llm = self.llm or LLMService()
                raw = parse_json_object(llm.complete(prompt))
                return self._normalize(raw, request, facts, plan_id, warnings)
            except (LLMServiceError, TripPlanningValidationError) as exc:
                last_error = exc
                if attempt == 0:
                    logger.warning("行程草案未通过结构校验，正在请求模型重新生成")
                    prompt += (
                        "\n上一次结果无法通过结构校验。请严格使用给定 attraction_names 和 hotel_id，"
                        "保持日期、城市和天数完全一致，只返回完整 JSON。"
                    )
        raise TripPlanningModelError("行程规划模型连续返回无效结果") from last_error

    def _prompt(
        self,
        request: TripPlanningRequest,
        facts: dict[str, CityPlanningFacts],
    ) -> str:
        """将经过清洗的景点、天气和酒店事实整理为规划模型输入。"""
        schedule = []
        current_date = request.start_date
        for city_position, stay in enumerate(request.cities):
            for city_day in range(stay.days):
                schedule.append(
                    {
                        "day_index": len(schedule) + 1,
                        "date": current_date.isoformat(),
                        "city": stay.city,
                        "is_transfer_day": city_position > 0 and city_day == 0,
                    }
                )
                current_date += timedelta(days=1)

        city_facts: dict[str, Any] = {}
        for city, city_data in facts.items():
            city_facts[city] = {
                "attractions": [
                    {
                        "name": item.name,
                        "name_zh": item.name_zh,
                        "reason": item.reason,
                        "duration": item.duration,
                        "address": item.address,
                        "rating": item.rating,
                    }
                    for item in city_data.extraction.attractions
                ],
                "weather": [item.model_dump(mode="json") for item in city_data.weather],
                "hotels": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "address": item.address,
                        "rating": item.rating,
                        "average_price": item.average_price,
                    }
                    for item in city_data.hotels
                ],
            }

        payload = {
            "schedule": schedule,
            "transportation": request.transportation,
            "accommodation": request.accommodation,
            "preferences": request.preferences,
            "extra_requirements": request.extra_requirements,
            "language": request.language,
            "travelers": request.travelers,
            "city_facts": city_facts,
        }
        return f"""请根据以下真实旅行资料生成逐日行程草案：
{json.dumps(payload, ensure_ascii=False)}

业务规则：
1. days 必须与 schedule 的日期、城市和数量完全一致。
2. 每天选择 2 到 3 个景点，移动日最多 2 个；attraction_names 必须原样使用 city_facts 中的景点名称。
3. 每天的景点顺序要兼顾游玩节奏和地点分布，不得编造坐标、评分、地址或天气。
4. hotel_id 只能选择当天城市 hotels 中的 id；没有酒店资料时填空字符串。
5. meals 是行程建议而非已核实商户，每天提供 breakfast、lunch、dinner，可给出保守的人均费用估算。
6. 所有说明文字使用 language 指定语言；JSON key 保持英文。
7. 只返回 JSON 对象，不要 Markdown。结构为：
{{
  "days": [{{
    "day_index": 1,
    "description": "当日安排说明",
    "attraction_names": ["景点原名"],
    "hotel_id": "酒店ID",
    "transfer_info": "移动日交通建议",
    "meals": [{{"type": "breakfast", "name": "餐饮建议", "description": "说明", "estimated_cost": 30}}]
  }}],
  "overall_suggestions": "总体出行建议"
}}
"""

    def _normalize(
        self,
        raw: dict[str, Any],
        request: TripPlanningRequest,
        facts: dict[str, CityPlanningFacts],
        plan_id: str,
        warnings: list[str],
    ) -> TripPlan:
        """只采纳能映射回真实来源的数据，并补齐每日必需结构。"""
        raw_days = raw.get("days")
        if not isinstance(raw_days, list) or len(raw_days) != self._day_count(request):
            raise TripPlanningValidationError("模型返回的每日行程数量与旅行日期不一致")

        raw_by_index = {
            int(item.get("day_index")): item
            for item in raw_days
            if isinstance(item, dict) and str(item.get("day_index", "")).isdigit()
        }
        city_offsets = {stay.city: 0 for stay in request.cities}
        used_attractions = {stay.city: set() for stay in request.cities}
        days: list[TripDay] = []
        current_date = request.start_date

        for city_position, stay in enumerate(request.cities):
            city_facts = facts[stay.city]
            candidates = city_facts.extraction.attractions
            candidate_map: dict[str, AttractionCandidate] = {}
            for candidate in candidates:
                for identity in (candidate.name, candidate.name_zh, candidate.name_en, candidate.poi_id):
                    if identity:
                        candidate_map[identity.casefold()] = candidate
            hotel_map = {hotel.id.casefold(): hotel for hotel in city_facts.hotels}
            hotel_map.update({hotel.name.casefold(): hotel for hotel in city_facts.hotels})

            for city_day in range(stay.days):
                day_index = len(days) + 1
                raw_day = raw_by_index.get(day_index)
                if raw_day is None and isinstance(raw_days[day_index - 1], dict):
                    raw_day = raw_days[day_index - 1]
                if raw_day is None:
                    raise TripPlanningValidationError("模型返回的每日行程缺少有效对象")
                is_transfer = city_position > 0 and city_day == 0
                attraction_limit = 2 if is_transfer else 3
                selected = self._select_attractions(
                    raw_day.get("attraction_names"),
                    candidates,
                    candidate_map,
                    used_attractions[stay.city],
                    city_offsets,
                    stay.city,
                    attraction_limit,
                )
                hotel_identity = str(raw_day.get("hotel_id") or "").strip().casefold()
                hotel = hotel_map.get(hotel_identity)
                if hotel is None and city_facts.hotels:
                    hotel = city_facts.hotels[0]
                meals = self._meals(raw_day.get("meals"), request.language)
                weather = next(
                    (item for item in city_facts.weather if item.date == current_date),
                    None,
                )
                days.append(
                    TripDay(
                        day_index=day_index,
                        date=current_date,
                        city=stay.city,
                        is_transfer_day=is_transfer,
                        transfer_info=_text(
                            raw_day.get("transfer_info"),
                            "建议预留充足的城市间移动和入住时间" if is_transfer else "",
                            500,
                        ) if is_transfer else "",
                        description=_text(
                            raw_day.get("description"),
                            f"按照地点顺序游览{stay.city}",
                            1000,
                        ),
                        transportation=request.transportation,
                        attractions=selected,
                        meals=meals,
                        hotel=hotel,
                        weather=weather,
                    )
                )
                current_date += timedelta(days=1)

        hotels = []
        seen_hotels: set[str] = set()
        for day in days:
            if day.hotel and day.hotel.id not in seen_hotels:
                hotels.append(day.hotel)
                seen_hotels.add(day.hotel.id)
        return TripPlan(
            plan_id=plan_id,
            cities=[stay.city for stay in request.cities],
            start_date=request.start_date,
            end_date=request.end_date,
            travelers=request.travelers,
            days=days,
            recommended_hotels=hotels,
            budget=TripBudget(target=request.total_budget),
            overall_suggestions=_text(
                raw.get("overall_suggestions"),
                "出发前请再次确认开放时间、预约要求和实时天气。",
                2000,
            ),
            warnings=list(warnings),
            source_extraction_ids=[
                facts[stay.city].extraction.extraction_id for stay in request.cities
            ],
        )

    @staticmethod
    def _day_count(request: TripPlanningRequest) -> int:
        """返回城市停留配置声明的总天数。"""
        return sum(stay.days for stay in request.cities)

    @staticmethod
    def _select_attractions(
        value: Any,
        candidates: list[AttractionCandidate],
        candidate_map: dict[str, AttractionCandidate],
        used: set[str],
        offsets: dict[str, int],
        city: str,
        limit: int,
    ) -> list[AttractionCandidate]:
        """保留模型排序，但过滤跨城市、未知和重复景点。"""
        requested = value if isinstance(value, list) else []
        selected: list[AttractionCandidate] = []
        for identity in requested:
            key = str(identity.get("name") if isinstance(identity, dict) else identity).casefold()
            candidate = candidate_map.get(key)
            if candidate is None or candidate.name.casefold() in used:
                continue
            selected.append(candidate)
            used.add(candidate.name.casefold())
            if len(selected) >= limit:
                return selected

        # NOTE: 模型漏选时按内容提取顺序补足，仍然只使用可追溯的景点候选。
        start = offsets[city]
        for position in range(start, len(candidates)):
            candidate = candidates[position]
            offsets[city] = position + 1
            if candidate.name.casefold() in used:
                continue
            selected.append(candidate)
            used.add(candidate.name.casefold())
            if len(selected) >= limit:
                break
        return selected

    @staticmethod
    def _meals(value: Any, language: str) -> list[TripMeal]:
        """保留合法餐饮建议，并补齐每日早中晚三种用餐类型。"""
        labels = {
            "zh": {"breakfast": "当地早餐", "lunch": "当地午餐", "dinner": "当地晚餐"},
            "en": {"breakfast": "Local breakfast", "lunch": "Local lunch", "dinner": "Local dinner"},
            "ja": {"breakfast": "現地の朝食", "lunch": "現地の昼食", "dinner": "現地の夕食"},
        }[language]
        raw_items = value if isinstance(value, list) else []
        by_type: dict[str, TripMeal] = {}
        for item in raw_items:
            if not isinstance(item, dict) or item.get("type") not in labels:
                continue
            meal_type = item["type"]
            by_type[meal_type] = TripMeal(
                type=meal_type,
                name=_text(item.get("name"), labels[meal_type], 120),
                description=_text(item.get("description"), "", 500),
                estimated_cost=_cost(item.get("estimated_cost")),
            )
        return [
            by_type.get(meal_type) or TripMeal(type=meal_type, name=label)
            for meal_type, label in labels.items()
        ]


class TripPlannerService:
    """协调资料采集、行程编排、路线计算、校验和持久化。"""

    def __init__(
        self,
        *,
        repository: TripRepository | None = None,
        attraction_extractor: Callable[..., XHSExtraction] | None = None,
        weather_service: WeatherService | None = None,
        hotel_service: HotelService | None = None,
        route_service: RouteService | None = None,
        composer: TripPlanComposer | None = None,
    ):
        """支持注入各业务依赖，线上默认使用项目现有实现。"""
        self.repository = repository or TripRepository()
        self.attraction_extractor = attraction_extractor or extract_attractions_with_metadata
        self.weather_service = weather_service
        self.hotel_service = hotel_service
        self.route_service = route_service
        self.composer = composer

    def run_task(self, task_id: str, request: TripPlanningRequest) -> None:
        """执行已提交任务，并保证成功或失败状态最终都会持久化。"""
        try:
            plan = self.plan(task_id, request)
            self.repository.complete_task(task_id, plan)
            logger.info("旅行规划任务完成：task_id={}，plan_id={}", task_id, plan.plan_id)
        except AttractionAuthenticationRequiredError as exc:
            self._fail(task_id, TripPlanningAuthenticationRequiredError.error_code, "小红书系统账号未登录，请管理员完成登录", exc)
        except TripPlanningError as exc:
            self._fail(task_id, exc.error_code, str(exc), exc)
        except (AttractionExtractionError, WeatherServiceError, HotelServiceError, RouteServiceError) as exc:
            self._fail(task_id, "TRIP_PROVIDER_ERROR", "旅行资料服务暂时不可用，请稍后重试", exc)
        except (TripRepositoryError, Exception) as exc:
            self._fail(task_id, "TRIP_PLANNING_FAILED", "旅行计划生成失败，请稍后重试", exc)

    def plan(self, task_id: str, request: TripPlanningRequest) -> TripPlan:
        """同步生成完整行程，供后台任务和集成测试复用。"""
        self._progress(task_id, "collecting_attractions", 10, "正在寻找目的地旅行灵感")
        facts, warnings = self._collect_facts(task_id, request)
        self._progress(task_id, "composing_itinerary", 72, "正在编排每日游玩顺序")
        composer = self.composer or TripPlanComposer()
        plan = composer.compose(
            request,
            facts,
            plan_id=task_id,
            warnings=warnings,
        )
        self._progress(task_id, "calculating_routes", 86, "正在计算每日地点之间的路线")
        self._attach_routes(plan)
        self._progress(task_id, "validating_plan", 95, "正在核对日期、路线和预算")
        plan.budget = self._budget(plan, request)
        self._validate(plan, request)
        return plan

    def _collect_facts(
        self,
        task_id: str,
        request: TripPlanningRequest,
    ) -> tuple[dict[str, CityPlanningFacts], list[str]]:
        """按城市汇总景点、天气和酒店，辅助信息失败时保留可见提示。"""
        result: dict[str, CityPlanningFacts] = {}
        warnings: list[str] = []
        total = len(request.cities)
        keywords = " ".join(request.preferences).strip() or request.extra_requirements[:100]
        for index, stay in enumerate(request.cities, 1):
            logger.info("旅行资料采集 [{}/{}]：城市={}", index, total, stay.city)
            progress_base = 10 + int((index - 1) / total * 55)
            self._progress(
                task_id,
                "collecting_attractions",
                progress_base,
                f"正在整理 {stay.city} 的推荐地点",
            )
            extraction = self.attraction_extractor(
                city=stay.city,
                keywords=keywords,
                language=request.language,
                note_limit=request.note_limit,
            )

            weather: list[WeatherForecast] = []
            self._progress(
                task_id,
                "collecting_weather",
                progress_base + 18,
                f"正在查询 {stay.city} 的天气",
            )
            try:
                weather_service = self.weather_service or WeatherService()
                weather = weather_service.query(stay.city).forecasts
            except WeatherServiceError:
                logger.warning("行程天气查询失败：城市={}，继续生成不含天气的行程", stay.city)
                warnings.append(f"{stay.city} 的天气信息暂时无法获取，请在出发前再次确认")

            hotels: list[Hotel] = []
            self._progress(
                task_id,
                "collecting_hotels",
                progress_base + 35,
                f"正在寻找 {stay.city} 的住宿选择",
            )
            try:
                hotel_service = self.hotel_service or HotelService()
                hotels = hotel_service.search(
                    HotelSearchCriteria(
                        city=stay.city,
                        accommodation=request.accommodation,
                        budget_max=request.hotel_budget_max,
                        limit=6,
                    )
                ).hotels
            except HotelServiceError:
                logger.warning("行程酒店查询失败：城市={}，继续生成不含酒店的行程", stay.city)
                warnings.append(f"{stay.city} 的住宿信息暂时无法获取，请单独确认住宿")
            result[stay.city] = CityPlanningFacts(extraction, weather, hotels)
        return result, warnings

    def _attach_routes(self, plan: TripPlan) -> None:
        """为每日相邻景点计算路线；缺少坐标或单段失败时记录行程提示。"""
        route_service = self.route_service
        for day in plan.days:
            for origin, destination in zip(day.attractions, day.attractions[1:]):
                if origin.location is None or destination.location is None:
                    plan.warnings.append(
                        f"第 {day.day_index} 天部分地点缺少坐标，未生成完整路线"
                    )
                    continue
                try:
                    route_service = route_service or RouteService()
                    result = route_service.query(
                        RouteQuery(
                            origin_address=origin.address or origin.name,
                            destination_address=destination.address or destination.name,
                            origin_city=day.city,
                            destination_city=day.city,
                            route_type=day.transportation,
                            origin_location=origin.location,
                            destination_location=destination.location,
                        )
                    )
                    day.routes.append(
                        TripRouteSegment(
                            origin_name=origin.name,
                            destination_name=destination.name,
                            route=result.route,
                        )
                    )
                except RouteServiceError:
                    logger.warning(
                        "行程路线计算失败：日期={}，起点={}，终点={}",
                        day.date,
                        origin.name,
                        destination.name,
                    )
                    plan.warnings.append(
                        f"第 {day.day_index} 天的部分路线暂时无法计算，请出发前确认"
                    )
        plan.warnings = list(dict.fromkeys(plan.warnings))

    @staticmethod
    def _budget(plan: TripPlan, request: TripPlanningRequest) -> TripBudget:
        """使用可追溯金额汇总预算，不为门票和交通编造价格。"""
        rooms = max(1, math.ceil(request.travelers / 2))
        hotel_total = sum(
            (day.hotel.average_price or 0) * rooms
            for day in plan.days[:-1]
            if day.hotel is not None
        )
        meal_total = sum(
            meal.estimated_cost * request.travelers
            for day in plan.days
            for meal in day.meals
        )
        total = round(hotel_total + meal_total, 2)
        if request.total_budget is not None and total > request.total_budget:
            plan.warnings.append("当前已知住宿和餐饮估算超过目标预算，可调整住宿或用餐选择")
        return TripBudget(
            hotels=round(hotel_total, 2),
            meals=round(meal_total, 2),
            total=total,
            target=request.total_budget,
        )

    @staticmethod
    def _validate(plan: TripPlan, request: TripPlanningRequest) -> None:
        """拒绝日期、城市、路线端点或预算汇总不一致的计划。"""
        expected_dates = [
            request.start_date + timedelta(days=offset)
            for offset in range((request.end_date - request.start_date).days + 1)
        ]
        if [day.date for day in plan.days] != expected_dates:
            raise TripPlanningValidationError("每日行程没有完整覆盖用户选择的日期")
        expected_cities = [
            stay.city
            for stay in request.cities
            for _ in range(stay.days)
        ]
        if [day.city for day in plan.days] != expected_cities:
            raise TripPlanningValidationError("每日行程城市与停留配置不一致")
        for day in plan.days:
            expected_pairs = [
                (origin.name, destination.name)
                for origin, destination in zip(day.attractions, day.attractions[1:])
            ]
            for segment in day.routes:
                if (segment.origin_name, segment.destination_name) not in expected_pairs:
                    raise TripPlanningValidationError("路线端点与当日景点顺序不一致")
                if segment.route.mode != day.transportation:
                    raise TripPlanningValidationError("路线交通方式与行程设置不一致")
        expected_total = round(
            plan.budget.attractions
            + plan.budget.hotels
            + plan.budget.meals
            + plan.budget.transportation,
            2,
        )
        if round(plan.budget.total, 2) != expected_total:
            raise TripPlanningValidationError("行程预算汇总不一致")

    def _progress(self, task_id: str, stage: str, progress: int, message: str) -> None:
        """同步记录终端进度和可供前端查询的任务状态。"""
        logger.info("旅行规划进度：task_id={}，进度={}%，{}", task_id, progress, message)
        self.repository.update_task(
            task_id,
            status="processing",
            stage=stage,
            progress=progress,
            message=message,
        )

    def _fail(self, task_id: str, code: str, message: str, exc: Exception) -> None:
        """保存不含上游敏感响应的失败状态。"""
        logger.error(
            "旅行规划任务失败：task_id={}，错误码={}，异常类型={}",
            task_id,
            code,
            type(exc).__name__,
        )
        try:
            self.repository.update_task(
                task_id,
                status="failed",
                stage="failed",
                progress=100,
                message=message,
                error_code=code,
                error=message,
            )
        except TripRepositoryError:
            logger.exception("旅行规划失败状态保存失败：task_id={}", task_id)
