"""旅行规划主流程、持久化和 REST 边界测试。"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from pydantic import ValidationError

from app.models.hotel import Hotel, HotelSearchResult
from app.models.poi import POILocation
from app.models.route import RouteEndpoint, RoutePlan, RouteQueryResult, RouteStep
from app.models.trip import TripCityStay, TripPlanningRequest
from app.models.weather import WeatherForecast, WeatherQueryResult
from app.models.xhs import AttractionCandidate, XHSExtraction
from app.schemas.trip import TripPlanRequest
from app.services.attraction_extractor import AttractionAuthenticationRequiredError
from app.services.trip_planner_service import TripPlanComposer, TripPlannerService
from app.storage.trip_repository import TripRepository


def _attraction(index: int) -> AttractionCandidate:
    """生成带真实坐标形态的景点候选。"""
    return AttractionCandidate(
        name=f"景点{index}",
        name_zh=f"景点{index}",
        name_en=f"Place {index}",
        reason="来自旅行笔记的推荐",
        duration=120,
        poi_id=f"poi-{index}",
        address=f"示例路{index}号",
        location=POILocation(longitude=116.30 + index * 0.01, latitude=39.90),
    )


class FakeLLM:
    """返回固定两日安排的规划模型。"""

    def complete(self, prompt: str) -> str:
        """断言输入包含三类事实，并返回合法行程草案。"""
        assert "city_facts" in prompt
        return json.dumps(
            {
                "days": [
                    {
                        "day_index": 1,
                        "description": "先游览核心区域",
                        "attraction_names": ["景点2", "景点1"],
                        "hotel_id": "hotel-1",
                        "meals": [
                            {"type": "breakfast", "name": "早餐", "estimated_cost": 20},
                            {"type": "lunch", "name": "午餐", "estimated_cost": 20},
                            {"type": "dinner", "name": "晚餐", "estimated_cost": 20},
                        ],
                    },
                    {
                        "day_index": 2,
                        "description": "继续游览周边地点",
                        "attraction_names": ["景点4", "不存在的景点"],
                        "hotel_id": "hotel-1",
                        "meals": [
                            {"type": "breakfast", "name": "早餐", "estimated_cost": 20},
                            {"type": "lunch", "name": "午餐", "estimated_cost": 20},
                            {"type": "dinner", "name": "晚餐", "estimated_cost": 20},
                        ],
                    },
                ],
                "overall_suggestions": "提前确认预约和开放时间",
            },
            ensure_ascii=False,
        )


class FakeWeatherService:
    """返回与第一天匹配的天气事实。"""

    def query(self, city: str) -> WeatherQueryResult:
        """只提供供应商实际覆盖的一天预报。"""
        return WeatherQueryResult(
            provider="amap",
            city=city,
            forecasts=[
                WeatherForecast(
                    city=city,
                    date=date(2026, 9, 4),
                    day_weather="晴",
                    night_weather="多云",
                )
            ],
        )


class FakeHotelService:
    """返回一家具备参考价格的酒店。"""

    def search(self, criteria) -> HotelSearchResult:
        """保留编排服务传入的住宿查询条件。"""
        return HotelSearchResult(
            provider="amap",
            criteria=criteria,
            hotels=[
                Hotel(
                    id="hotel-1",
                    name="示例酒店",
                    city=criteria.city,
                    average_price=600,
                )
            ],
        )


class FakeRouteService:
    """按请求端点返回固定距离和耗时的路线。"""

    def query(self, query) -> RouteQueryResult:
        """复用景点坐标构造可校验的路线端点。"""
        origin = RouteEndpoint(
            name=query.origin_address,
            address=query.origin_address,
            city=query.origin_city,
            location=query.origin_location,
        )
        destination = RouteEndpoint(
            name=query.destination_address,
            address=query.destination_address,
            city=query.destination_city,
            location=query.destination_location,
        )
        route = RoutePlan(
            origin=origin,
            destination=destination,
            mode=query.route_type,
            distance_meters=1500,
            duration_seconds=900,
            steps=[
                RouteStep(
                    instruction="沿道路前往下一地点",
                    distance_meters=1500,
                    duration_seconds=900,
                )
            ],
        )
        return RouteQueryResult(provider="amap", query=query, route=route)


def _request() -> TripPlanningRequest:
    """生成覆盖两个自然日的单城市旅行需求。"""
    return TripPlanningRequest(
        cities=[TripCityStay(city="北京", days=2)],
        start_date=date(2026, 9, 4),
        end_date=date(2026, 9, 5),
        transportation="walking",
        preferences=["历史文化"],
        travelers=1,
        total_budget=2000,
        hotel_budget_max=800,
    )


def _extraction(**kwargs) -> XHSExtraction:
    """返回已经完成 POI 补全的景点提取记录。"""
    return XHSExtraction(
        extraction_id="extract-1",
        city=kwargs["city"],
        keywords=kwargs["keywords"],
        language=kwargs["language"],
        notes_count=4,
        attractions=[_attraction(index) for index in range(1, 5)],
    )


class TripPlannerFlowTest(unittest.TestCase):
    """验证景点、天气、酒店、路线、预算和任务状态形成一个闭环。"""

    def test_completed_task_persists_full_plan_days_routes_and_budget(self) -> None:
        """成功任务应保存每日安排、路线、预算并进入历史列表。"""
        with TemporaryDirectory() as directory:
            repository = TripRepository(Path(directory) / "trip.db")
            request = _request()
            repository.create_task("task-1", request)
            service = TripPlannerService(
                repository=repository,
                attraction_extractor=_extraction,
                weather_service=FakeWeatherService(),
                hotel_service=FakeHotelService(),
                route_service=FakeRouteService(),
                composer=TripPlanComposer(FakeLLM()),
            )
            service.run_task("task-1", request)

            task = repository.get_task("task-1")
            plan = repository.get_plan("task-1")
            history = repository.list_plans()

        self.assertIsNotNone(task)
        self.assertEqual(task.status, "completed")
        self.assertIsNotNone(plan)
        self.assertEqual([day.date.isoformat() for day in plan.days], ["2026-09-04", "2026-09-05"])
        self.assertEqual([item.name for item in plan.days[0].attractions[:2]], ["景点2", "景点1"])
        self.assertGreaterEqual(len(plan.days[0].routes), 1)
        self.assertEqual(plan.days[0].weather.day_weather, "晴")
        self.assertIsNone(plan.days[1].weather)
        self.assertEqual(plan.budget.hotels, 600)
        self.assertEqual(plan.budget.meals, 120)
        self.assertEqual(plan.budget.total, 720)
        self.assertEqual(history[0]["plan_id"], "task-1")

    def test_authentication_failure_is_persisted_with_stable_code(self) -> None:
        """内容账号失效后，状态接口所需错误码必须保留在任务中。"""
        def fail_extraction(**kwargs):
            raise AttractionAuthenticationRequiredError("系统账号未登录")

        with TemporaryDirectory() as directory:
            repository = TripRepository(Path(directory) / "trip.db")
            request = _request()
            repository.create_task("task-auth", request)
            TripPlannerService(
                repository=repository,
                attraction_extractor=fail_extraction,
            ).run_task("task-auth", request)
            task = repository.get_task("task-auth")

        self.assertEqual(task.status, "failed")
        self.assertEqual(task.error_code, "XHS_AUTH_REQUIRED")
        self.assertIsNone(task.plan_id)


class TripPlanningBoundaryTest(unittest.TestCase):
    """验证请求约束以及领域模型和 REST 模型的独立性。"""

    def test_city_days_must_match_inclusive_date_range(self) -> None:
        """城市天数与日期不一致时应在编排开始前拒绝。"""
        with self.assertRaisesRegex(ValidationError, "停留天数"):
            TripPlanningRequest(
                cities=[TripCityStay(city="北京", days=2)],
                start_date=date(2026, 9, 4),
                end_date=date(2026, 9, 6),
            )

    def test_rest_request_is_independent_from_domain_request(self) -> None:
        """旅行 REST DTO 不应继承旅行领域模型。"""
        self.assertFalse(issubclass(TripPlanRequest, TripPlanningRequest))

    def test_trip_routes_are_registered(self) -> None:
        """主流程提交、状态、历史和计划查询都应出现在 OpenAPI。"""
        from main import app

        paths = app.openapi()["paths"]
        self.assertIn("/api/trip/plan", paths)
        self.assertIn("/api/trip/status/{task_id}", paths)
        self.assertIn("/api/trip/history", paths)
        self.assertIn("/api/trip/plan/{plan_id}", paths)


if __name__ == "__main__":
    unittest.main()
