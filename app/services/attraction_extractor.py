"""小红书旅行笔记的景点候选提取、地图补全和持久化服务。"""
from __future__ import annotations

import re
import time
from typing import Any

from loguru import logger
from pydantic import ValidationError

from app.integrations.xhs import (
    XHSAuthenticationRequiredError,
    XHSProvider,
    XHSProviderError,
)
from app.models.poi import POI
from app.models.xhs import AttractionCandidate, XHSExtraction
from app.services.poi_service import POIService, POIServiceError
from app.storage.poi_repository import POIRepositoryError
from app.storage.xhs_repository import XHSRepository, XHSRepositoryError

from .llm_service import LLMService, LLMServiceError, parse_json_payload


class AttractionExtractionError(RuntimeError):
    """景点候选提取失败。"""


class AttractionAuthenticationRequiredError(AttractionExtractionError):
    """当前浏览器未登录小红书，需要登录后重新提取。"""


def _duration(value: Any) -> int:
    """将模型游玩时长转换为 1 到 1440 分钟。"""
    text = str(value or "").strip().lower()
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        return 120
    minutes = float(match.group())
    if any(unit in text for unit in ("小时", "小時", "hour", "hr")):
        minutes *= 60
    return max(1, min(1440, round(minutes)))


def _boolean(value: Any) -> bool:
    """把模型返回的预约标记转换为布尔值。"""
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"true", "1", "yes", "是", "需要"}


def _candidate(item: dict[str, Any]) -> AttractionCandidate | None:
    """校验并补全单个景点条目，无法满足接口约束时跳过该条目。"""
    name = str(item.get("name") or item.get("name_zh") or "").strip()
    if not name:
        return None
    name_zh = str(item.get("name_zh") or name).strip()
    name_en = str(item.get("name_en") or name_zh).strip()
    reason = str(item.get("reason") or "旅行笔记中提到的推荐景点").strip()
    try:
        return AttractionCandidate(
            name=name,
            name_zh=name_zh,
            name_en=name_en,
            reason=reason,
            duration=_duration(item.get("duration")),
            reservation_required=_boolean(item.get("reservation_required")),
            reservation_tips=str(item.get("reservation_tips") or "").strip(),
        )
    except ValidationError:
        return None


def _prompt(city: str, keywords: str, language: str, notes: list[dict[str, Any]]) -> str:
    """根据城市偏好和笔记正文生成景点提取提示词。"""
    note_text = "\n\n".join(
        f"【笔记 {index}】\n标题：{note['title']}\n正文：{note['content'][:8000]}"
        for index, note in enumerate(notes, 1)
    )
    return f"""请从以下关于{city}的旅行笔记中提取适合行程规划的景点候选。
偏好关键词：{keywords or '无'}
输出语言：{language}

要求：
1. 只提取真实景点、博物馆、公园、古镇等可游览地点，过滤餐厅、酒店、商场和泛化区域。
2. 合并同一景点的重复提及，最多返回 20 个景点。
3. duration 为建议游玩时长，单位为分钟；无法判断时填写 120。
4. reservation_required 只有在笔记明确提到预约、抢票或限流时才为 true。
5. 只返回 JSON 数组，不要 Markdown 或额外解释。每项字段必须为：
name, name_zh, name_en, reason, duration, reservation_required, reservation_tips。

旅行笔记：
{note_text}
"""


def _enrich_candidate(candidate: AttractionCandidate, poi: POI) -> AttractionCandidate:
    """将地图 POI 的标准地点信息补充到景点候选。"""
    return candidate.model_copy(
        update={
            "poi_id": poi.id,
            "address": poi.address,
            "location": poi.location,
            "rating": poi.rating,
            "photos": list(poi.photos),
        }
    )


def _enrich_candidates_with_poi(
    candidates: list[AttractionCandidate],
    city: str,
    poi_service: POIService | None = None,
) -> list[AttractionCandidate]:
    """按城市和中文名称补全候选的 POI 标识、地址和坐标。"""
    if not candidates:
        return candidates
    if poi_service is None:
        try:
            poi_service = POIService()
        except (POIRepositoryError, XHSRepositoryError):
            logger.warning("POI 数据存储不可用，保留未补全的景点候选")
            return candidates

    enriched: list[AttractionCandidate] = []
    matched_count = 0
    logger.info("正在查询景点 POI：共 {} 个候选", len(candidates))
    for index, candidate in enumerate(candidates, 1):
        logger.info("POI 查询 [{}/{}]：{}", index, len(candidates), candidate.name_zh)
        try:
            pois = poi_service.search(candidate.name_zh or candidate.name, city, True, 5)
        except POIServiceError:
            logger.warning("POI 查询失败：{}，保留原始景点候选", candidate.name)
            enriched.append(candidate)
            continue
        if not pois:
            logger.warning("POI 未找到匹配结果：{}，保留原始景点候选", candidate.name)
            enriched.append(candidate)
            continue

        names = {candidate.name.casefold(), candidate.name_zh.casefold(), candidate.name_en.casefold()}
        # NOTE: 优先使用名称完全匹配的 POI，防止相近地点覆盖原始景点候选。
        matched = next((poi for poi in pois if poi.name.casefold() in names), pois[0])
        matched_count += 1
        logger.info("POI 已匹配：{} -> {}", candidate.name, matched.name)
        enriched.append(_enrich_candidate(candidate, matched))
    logger.info("POI 补全完成：成功 {}/{} 个候选", matched_count, len(candidates))
    return enriched


def _extract_attractions(
    city: str,
    keywords: str = "",
    language: str = "zh",
    note_limit: int = 4,
    *,
    provider: XHSProvider | None = None,
    llm: LLMService | None = None,
    repository: XHSRepository | None = None,
    poi_service: POIService | None = None,
) -> XHSExtraction:
    """搜索旅行笔记、提取候选、补全 POI 信息并保存完整结果。

    只有笔记和候选成功写入仓储后，才会返回提取记录 ID。
    """
    started_at = time.perf_counter()
    city = city.strip()
    keywords = keywords.strip()
    if not city:
        raise AttractionExtractionError("城市不能为空")
    logger.info(
        "开始提取旅行景点：城市={}，关键词={}，笔记数量上限={}",
        city,
        keywords or "无",
        note_limit,
    )
    keyword = " ".join(part for part in (city, keywords, "旅游", "景点攻略") if part)
    owns_provider = provider is None
    notes: list[dict[str, Any]] = []
    try:
        provider = provider or XHSProvider()
        # NOTE: note_limit 同时约束上游抓取规模和进入模型的笔记数量。
        logger.info("正在搜索小红书旅行笔记：{}", keyword)
        search_notes = provider.search_notes(keyword, limit=note_limit)
        logger.info("小红书搜索完成：获取 {} 条笔记", len(search_notes))
        for index, search_note in enumerate(search_notes, 1):
            note = search_note
            if search_note.note_id:
                logger.info("正在读取笔记详情 [{}/{}]", index, len(search_notes))
                try:
                    note = provider.get_note(
                        search_note.note_id,
                        xsec_token=search_note.xsec_token,
                        xsec_source=search_note.xsec_source,
                    )
                except XHSProviderError:
                    # WORKAROUND: 详情接口失败时使用搜索卡片正文，单篇失败不应中断整批提取。
                    logger.warning("笔记详情读取失败 [{}/{}]，使用搜索结果内容", index, len(search_notes))
                    note = search_note
            content = (note.content or search_note.content or "").strip()
            title = (note.title or search_note.title or "").strip()
            if title or content:
                notes.append(
                    {
                        "note_id": note.note_id or search_note.note_id,
                        "title": title,
                        "content": content,
                        "source_url": note.source_url or search_note.source_url,
                        "xsec_source": note.xsec_source or search_note.xsec_source,
                        "images": note.images or search_note.images,
                        "author": note.author or search_note.author,
                        "liked_count": note.liked_count or search_note.liked_count,
                    }
                )
    except XHSAuthenticationRequiredError as exc:
        # NOTE: 登录失效必须保留独立异常类型，REST 层据此返回 XHS_AUTH_REQUIRED。
        raise AttractionAuthenticationRequiredError("当前浏览器尚未登录小红书") from exc
    except XHSProviderError as exc:
        raise AttractionExtractionError(str(exc)) from exc
    finally:
        if owns_provider and provider is not None:
            provider.close()

    if not notes:
        raise AttractionExtractionError("没有获取到可用于提取的旅行笔记")
    logger.info("可用于景点提取的笔记：{} 篇", len(notes))
    try:
        llm = llm or LLMService()
        logger.info("正在调用大模型提取结构化景点")
        raw_items = parse_json_payload(llm.complete(_prompt(city, keywords, language, notes)))
    except LLMServiceError as exc:
        # NOTE: 日志只记录异常类型，不包含笔记正文和模型完整响应。
        logger.error("大模型景点提取失败，错误类型：{}", type(exc).__name__)
        raise AttractionExtractionError(str(exc)) from exc

    result: list[AttractionCandidate] = []
    seen: set[str] = set()
    for item in raw_items:
        candidate = _candidate(item)
        if candidate is None:
            continue
        identity = candidate.name.casefold()
        if identity in seen:
            continue
        seen.add(identity)
        result.append(candidate)
        if len(result) >= 20:
            break
    logger.info("大模型候选解析完成：原始 {} 条，有效去重后 {} 条", len(raw_items), len(result))
    result = _enrich_candidates_with_poi(result, city, poi_service)
    try:
        repository = repository or XHSRepository()
        extraction_id = repository.save_extraction(
            city=city,
            keywords=keywords,
            language=language,
            notes=notes,
            candidates=[candidate.model_dump() for candidate in result],
        )
    except XHSRepositoryError as exc:
        raise AttractionExtractionError(str(exc)) from exc
    logger.info(
        "景点提取完成：保存 {} 条候选，记录 ID={}，耗时 {:.2f}s",
        len(result),
        extraction_id,
        time.perf_counter() - started_at,
    )
    return XHSExtraction(
        attractions=result,
        notes_count=len(notes),
        extraction_id=extraction_id,
        city=city,
        keywords=keywords,
        language=language,
    )


def extract_attractions(
    city: str,
    keywords: str = "",
    language: str = "zh",
    note_limit: int = 4,
    *,
    provider: XHSProvider | None = None,
    llm: LLMService | None = None,
    repository: XHSRepository | None = None,
    poi_service: POIService | None = None,
) -> list[AttractionCandidate]:
    """返回已尝试补全 POI 信息的景点候选，调用方无需处理记录元数据。"""
    extraction = _extract_attractions(
        city,
        keywords,
        language,
        note_limit,
        provider=provider,
        llm=llm,
        repository=repository,
        poi_service=poi_service,
    )
    return extraction.attractions


def extract_attractions_with_count(
    city: str,
    keywords: str = "",
    language: str = "zh",
    note_limit: int = 4,
    *,
    provider: XHSProvider | None = None,
    llm: LLMService | None = None,
    repository: XHSRepository | None = None,
    poi_service: POIService | None = None,
) -> tuple[list[AttractionCandidate], int]:
    """返回已尝试补全 POI 信息的候选和实际参与提取的笔记数量。"""
    extraction = _extract_attractions(
        city,
        keywords,
        language,
        note_limit,
        provider=provider,
        llm=llm,
        repository=repository,
        poi_service=poi_service,
    )
    return extraction.attractions, extraction.notes_count


def extract_attractions_with_metadata(
    city: str,
    keywords: str = "",
    language: str = "zh",
    note_limit: int = 4,
    *,
    provider: XHSProvider | None = None,
    llm: LLMService | None = None,
    repository: XHSRepository | None = None,
    poi_service: POIService | None = None,
) -> XHSExtraction:
    """返回候选列表、笔记数量和持久化记录 ID，供接口读取完整保存结果。"""
    return _extract_attractions(
        city,
        keywords,
        language,
        note_limit,
        provider=provider,
        llm=llm,
        repository=repository,
        poi_service=poi_service,
    )
