"""把已生成的完整行程渲染为可下载的 PDF 文档。"""

from __future__ import annotations

import io
import os
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image as FlowableImage,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.models.trip import TripDay, TripPlan
from app.services.image_fetcher import fetch_attraction_image

_INK = colors.HexColor("#1f2a24")
_MUTED = colors.HexColor("#77867d")
_SOFT = colors.HexColor("#f2f5f2")
_LINE = colors.HexColor("#dbe3dc")
_FOREST = colors.HexColor("#2f6b4a")
_CORAL = colors.HexColor("#a9762c")
_WARN_BG = colors.HexColor("#fbf6ec")

_PAGE_SIZE = A4
_MARGIN = 16 * mm
_FRAME_WIDTH = _PAGE_SIZE[0] - 2 * _MARGIN

_THUMBNAIL_WIDTH = 40 * mm
_THUMBNAIL_HEIGHT = 30 * mm
# 单次导出最多下载的图片数量，用于限制最坏情况下的等待时间。
_MAX_IMAGES = 16
_IMAGE_WORKERS = 6

ImageProvider = Callable[[str], "bytes | None"]

_BODY_NAME = "TravelMindBody"
_BOLD_NAME = "TravelMindBold"

# reportlab 无法内嵌 CFF/OTF 轮廓，这里只登记 TrueType 字体作为可选项。
_EMBEDDED_FONT_CANDIDATES: tuple[tuple[str, int], ...] = (
    ("/System/Library/Fonts/STHeiti Light.ttc", 0),
    ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 0),
    ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0),
    ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
    ("/usr/share/fonts/truetype/arphic/uming.ttc", 0),
)

_EMBEDDED_BOLD_FONT_CANDIDATES: tuple[tuple[str, int], ...] = (
    ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0),
)

# 找不到可内嵌字体时退回 reportlab 自带 CID 字体，保证中日文仍可输出。
_CID_FONTS = {"zh": "STSong-Light", "ja": "HeiseiKakuGo-W5", "en": "STSong-Light"}

_font_lock = threading.Lock()
_embedded_ready = False
_embedded_fonts: tuple[str, str] | None = None
_cid_fonts: dict[str, tuple[str, str]] = {}

_LABELS: dict[str, dict[str, object]] = {
    "zh": {
        "doc_title": "{city}行程",
        "meta_travelers": "{count} 人出行",
        "meta_days": "共 {days} 天",
        "meta_range": "{start} 至 {end}",
        "plan_id": "行程编号 {plan_id}",
        "generated": "导出于 {time}",
        "budget": "费用估算",
        "budget_total": "合计",
        "budget_target": "预算目标",
        "categories": {
            "attractions": "景点",
            "hotels": "住宿",
            "meals": "餐饮",
            "transportation": "交通",
        },
        "warnings": "行程提醒",
        "day": "第 {day} 天",
        "transfer": "城市移动日",
        "attractions": "当天景点",
        "routes": "地点间路线",
        "meals": "用餐建议",
        "stay": "当晚住宿",
        "stay_empty": "当天未安排住宿信息",
        "advice": "行前建议",
        "rating": "评分 {rating}",
        "duration_minutes": "{minutes} 分钟",
        "duration_hours": "{hours} 小时",
        "duration_hours_minutes": "{hours} 小时 {minutes} 分钟",
        "reservation": "建议预约",
        "meal_types": {
            "breakfast": "早餐",
            "lunch": "午餐",
            "dinner": "晚餐",
            "snack": "加餐",
        },
        "transport": {"walking": "步行", "driving": "驾车", "transit": "公共交通"},
        "footer": "由 TravelMind-AI 生成 · 行程建议仅供参考",
        "page": "第 {page} 页",
        "empty": "这份行程暂时没有逐日安排。",
    },
    "en": {
        "doc_title": "{city} itinerary",
        "meta_travelers": "{count} travelers",
        "meta_days": "{days} days",
        "meta_range": "{start} to {end}",
        "plan_id": "Plan ID {plan_id}",
        "generated": "Exported {time}",
        "budget": "Cost estimate",
        "budget_total": "Total",
        "budget_target": "Budget target",
        "categories": {
            "attractions": "Attractions",
            "hotels": "Stays",
            "meals": "Meals",
            "transportation": "Transport",
        },
        "warnings": "Trip notes",
        "day": "Day {day}",
        "transfer": "Transfer day",
        "attractions": "Places today",
        "routes": "Routes between stops",
        "meals": "Meal ideas",
        "stay": "Tonight's stay",
        "stay_empty": "No stay is planned for this day",
        "advice": "Before you go",
        "rating": "Rating {rating}",
        "duration_minutes": "{minutes} min",
        "duration_hours": "{hours} h",
        "duration_hours_minutes": "{hours} h {minutes} min",
        "reservation": "Reservation suggested",
        "meal_types": {
            "breakfast": "Breakfast",
            "lunch": "Lunch",
            "dinner": "Dinner",
            "snack": "Snack",
        },
        "transport": {"walking": "Walking", "driving": "Driving", "transit": "Public transit"},
        "footer": "Generated by TravelMind-AI · Plans are suggestions only",
        "page": "Page {page}",
        "empty": "This plan does not have a daily itinerary yet.",
    },
    "ja": {
        "doc_title": "{city}の旅程",
        "meta_travelers": "{count} 名",
        "meta_days": "{days} 日間",
        "meta_range": "{start} から {end}",
        "plan_id": "旅程番号 {plan_id}",
        "generated": "{time} に出力",
        "budget": "費用の目安",
        "budget_total": "合計",
        "budget_target": "予算目標",
        "categories": {
            "attractions": "観光",
            "hotels": "宿泊",
            "meals": "食事",
            "transportation": "交通",
        },
        "warnings": "旅程のお知らせ",
        "day": "{day} 日目",
        "transfer": "都市移動日",
        "attractions": "その日の観光地",
        "routes": "場所間のルート",
        "meals": "食事の提案",
        "stay": "今夜の宿泊",
        "stay_empty": "この日の宿泊情報はありません",
        "advice": "出発前のアドバイス",
        "rating": "評価 {rating}",
        "duration_minutes": "{minutes} 分",
        "duration_hours": "{hours} 時間",
        "duration_hours_minutes": "{hours} 時間 {minutes} 分",
        "reservation": "予約推奨",
        "meal_types": {
            "breakfast": "朝食",
            "lunch": "昼食",
            "dinner": "夕食",
            "snack": "軽食",
        },
        "transport": {"walking": "徒歩", "driving": "車", "transit": "公共交通"},
        "footer": "TravelMind-AI が生成 · 旅程は参考情報です",
        "page": "{page} ページ",
        "empty": "この旅程には日別の予定がまだありません。",
    },
}


class PlanExportError(RuntimeError):
    """行程导出为 PDF 时渲染失败。"""


def _register_embedded(name: str, path: str, index: int) -> bool:
    """把磁盘上的 TrueType 字体登记为报告字体，失败时返回 False。"""
    if not Path(path).is_file():
        return False
    try:
        pdfmetrics.registerFont(TTFont(name, path, subfontIndex=index))
    except Exception:
        return False
    return True


def _discover_embedded_fonts() -> tuple[str, str] | None:
    """按环境变量和常见系统字体路径查找正文与强调字体。"""
    global _embedded_ready, _embedded_fonts
    with _font_lock:
        if _embedded_ready:
            return _embedded_fonts
        _embedded_ready = True

        body_path = ""
        env_body = os.getenv("TRAVELMIND_PDF_FONT", "").strip()
        if env_body and _register_embedded(_BODY_NAME, env_body, 0):
            body_path = env_body
        if not body_path:
            for path, index in _EMBEDDED_FONT_CANDIDATES:
                if _register_embedded(_BODY_NAME, path, index):
                    body_path = path
                    break
        if not body_path:
            return None

        env_bold = os.getenv("TRAVELMIND_PDF_FONT_BOLD", "").strip()
        if env_bold and env_bold != body_path and _register_embedded(_BOLD_NAME, env_bold, 0):
            _embedded_fonts = (_BODY_NAME, _BOLD_NAME)
            return _embedded_fonts
        for path, index in _EMBEDDED_BOLD_FONT_CANDIDATES:
            if path != body_path and _register_embedded(_BOLD_NAME, path, index):
                _embedded_fonts = (_BODY_NAME, _BOLD_NAME)
                return _embedded_fonts
        _embedded_fonts = (_BODY_NAME, _BODY_NAME)
        return _embedded_fonts


def _fonts_for(language: str) -> tuple[str, str]:
    """返回该语言下可用的正文与强调字体名。"""
    embedded = _discover_embedded_fonts()
    if embedded:
        return embedded
    with _font_lock:
        cached = _cid_fonts.get(language)
        if cached:
            return cached
        cid = _CID_FONTS.get(language, "STSong-Light")
        pdfmetrics.registerFont(UnicodeCIDFont(cid))
        _cid_fonts[language] = (cid, cid)
        return _cid_fonts[language]


def _styles(fonts: tuple[str, str]) -> dict[str, ParagraphStyle]:
    """构建 PDF 各层级文本样式。"""
    body, bold = fonts
    return {
        "title": ParagraphStyle("title", fontName=bold, fontSize=23, leading=30, textColor=_INK),
        "meta": ParagraphStyle("meta", fontName=body, fontSize=10.5, leading=16, textColor=_MUTED),
        "section": ParagraphStyle(
            "section", fontName=bold, fontSize=12.5, leading=17, textColor=_FOREST
        ),
        "day": ParagraphStyle("day", fontName=bold, fontSize=16, leading=21, textColor=_INK),
        "day_meta": ParagraphStyle(
            "day_meta", fontName=body, fontSize=9.5, leading=14, textColor=_MUTED
        ),
        "body": ParagraphStyle("body", fontName=body, fontSize=10.5, leading=16.5, textColor=_INK),
        "item": ParagraphStyle("item", fontName=body, fontSize=10, leading=15.5, textColor=_INK),
        "small": ParagraphStyle("small", fontName=body, fontSize=9, leading=13.5, textColor=_MUTED),
        "budget_label": ParagraphStyle(
            "budget_label", fontName=body, fontSize=8.5, leading=13, textColor=_MUTED
        ),
        "cell": ParagraphStyle("cell", fontName=body, fontSize=10, leading=14.5, textColor=_INK),
        "cell_muted": ParagraphStyle(
            "cell_muted", fontName=body, fontSize=9, leading=13, textColor=_MUTED
        ),
    }


def _text(value: object) -> str:
    """转义文本，避免内容中的标记符号破坏段落排版。"""
    return escape(str(value))


def _money(value: float, currency: str) -> str:
    """按货币格式化金额，人民币使用 ¥ 前缀。"""
    amount = f"{value:,.0f}"
    return f"¥{amount}" if currency.upper() == "CNY" else f"{amount} {currency}"


def _duration(minutes: int, labels: dict[str, object]) -> str:
    """把分钟数转换为本地化时长文本。"""
    safe_minutes = max(1, int(minutes))
    if safe_minutes < 60:
        return str(labels["duration_minutes"]).format(minutes=safe_minutes)
    hours, remainder = divmod(safe_minutes, 60)
    if remainder:
        return str(labels["duration_hours_minutes"]).format(hours=hours, minutes=remainder)
    return str(labels["duration_hours"]).format(hours=hours)


def _route_minutes(seconds: int, labels: dict[str, object]) -> str:
    """把路线耗时转换为分钟文本，向下取整并至少一分钟。"""
    return _duration(max(1, round(seconds / 60)), labels)


def _distance(meters: int) -> str:
    """把米转换为公里文本。"""
    return f"{meters / 1000:.1f} km"


def _attraction_title(attraction, language: str) -> str:
    """按结果语言选择景点标题，缺失时回退到可用名称。"""
    if language == "en":
        return attraction.name_en or attraction.name or attraction.name_zh
    if language == "ja":
        return attraction.name or attraction.name_zh or attraction.name_en
    return attraction.name_zh or attraction.name or attraction.name_en


def _weather_line(day: TripDay) -> str:
    """组合当天天气描述与温度区间。"""
    weather = day.weather
    if weather is None:
        return ""
    text = " / ".join(dict.fromkeys(value for value in (weather.day_weather, weather.night_weather) if value))
    low, high = weather.night_temperature, weather.day_temperature
    if low is None and high is None:
        return text
    low_text = "--" if low is None else f"{low:g}"
    high_text = "--" if high is None else f"{high:g}"
    return f"{text} {low_text}~{high_text}°" if text else f"{low_text}~{high_text}°"


def _table(rows, widths, commands=None, *, padding: float = 6) -> Table:
    """生成带统一留白的紧凑表格，并叠加调用方给出的样式。"""
    table = Table(rows, colWidths=widths, hAlign="LEFT")
    base = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), padding),
        ("RIGHTPADDING", (0, 0), (-1, -1), padding),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
    ]
    table.setStyle(TableStyle(base + list(commands or [])))
    return table


def _budget_block(plan: TripPlan, labels: dict[str, object], styles) -> list:
    """把预算按类别铺成一排，附带合计与预算目标。"""
    budget = plan.budget
    categories = labels["categories"]
    rows = []
    cells = []
    for key in ("attractions", "hotels", "meals", "transportation"):
        value = getattr(budget, key)
        cells.append(
            Paragraph(
                _text(categories[key]),
                styles["budget_label"],
            )
        )
        rows.append(value)
    cells.append(Paragraph(_text(str(labels["budget_total"])), styles["budget_label"]))

    header = _table(
        [cells],
        [_FRAME_WIDTH / 5] * 5,
        [
            ("BACKGROUND", (0, 0), (-1, -1), _SOFT),
            ("LINEBEFORE", (1, 0), (-1, -1), 0.5, _LINE),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ],
        padding=8,
    )
    values = _table(
        [
            [
                Paragraph(
                    f"<font size=13.5 color='{'#2f6b4a' if index == 4 else '#1f2a24'}'>"
                    f"{_text(_money(value, budget.currency))}</font>",
                    styles["budget_label"],
                )
                for index, value in enumerate(rows + [budget.total])
            ]
        ],
        [_FRAME_WIDTH / 5] * 5,
        [
            ("BACKGROUND", (0, 0), (-1, -1), _SOFT),
            ("LINEBEFORE", (1, 0), (-1, -1), 0.5, _LINE),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ],
        padding=8,
    )

    story = [
        Paragraph(_text(str(labels["budget"])), styles["section"]),
        Spacer(1, 2 * mm),
        header,
        values,
    ]
    if budget.target:
        target = _money(budget.target, budget.currency)
        story.append(
            Paragraph(
                _text(f"{labels['budget_target']}  {target}"),
                styles["small"],
            )
        )
    return story


def _warnings_block(plan: TripPlan, labels: dict[str, object], styles) -> Table:
    """把行程提醒渲染成带强调边的提示块。"""
    lines = "".join(f"• {_text(item)}<br/>" for item in plan.warnings).rstrip("<br/>")
    paragraph = Paragraph(f"<b>{_text(labels['warnings'])}</b><br/>{lines}", styles["small"])
    return _table(
        [[paragraph]],
        [_FRAME_WIDTH],
        [
            ("BACKGROUND", (0, 0), (-1, -1), _WARN_BG),
            ("LINEBEFORE", (0, 0), (0, -1), 2, _CORAL),
        ],
        padding=8,
    )


def _load_images(plan: TripPlan, provider: ImageProvider) -> dict[tuple[int, int], bytes]:
    """并发下载各景点首图，下载失败或超出数量上限的直接跳过。"""
    targets: list[tuple[tuple[int, int], str]] = []
    for day in plan.days:
        for index, attraction in enumerate(day.attractions, start=1):
            url = attraction.photos[0] if attraction.photos else ""
            if url:
                targets.append(((day.day_index, index), url))
    if not targets:
        return {}

    images: dict[tuple[int, int], bytes] = {}
    with ThreadPoolExecutor(max_workers=_IMAGE_WORKERS) as executor:
        pending = {
            executor.submit(provider, url): key
            for key, url in targets[:_MAX_IMAGES]
        }
        for future in as_completed(pending):
            try:
                payload = future.result()
            except Exception:
                payload = None
            if payload:
                images[pending[future]] = payload
    return images


def _attraction_block(
    index: int,
    attraction,
    labels: dict[str, object],
    styles,
    language: str,
    image: bytes | None = None,
) -> Table:
    """渲染单个景点：标题、关键信息、推荐理由、地址与可选首图。"""
    title = f"{index}. {_attraction_title(attraction, language)}"
    html = [f"<b>{_text(title)}</b>"]
    meta = []
    if attraction.rating is not None:
        meta.append(str(labels["rating"]).format(rating=f"{attraction.rating:g}"))
    meta.append(_duration(attraction.duration, labels))
    if attraction.reservation_required:
        meta.append(str(labels["reservation"]))
    html.append(f"<font size=9 color='#77867d'>{_text('  ·  '.join(meta))}</font>")
    if attraction.reason:
        html.append(_text(attraction.reason))
    if attraction.address:
        html.append(f"<font size=9 color='#77867d'>{_text(attraction.address)}</font>")

    paragraph = Paragraph("<br/>".join(html), styles["item"])
    commands = [
        ("BACKGROUND", (0, 0), (-1, -1), _SOFT),
        ("LINEBEFORE", (0, 0), (0, -1), 2, _FOREST),
    ]
    if image is None:
        return _table([[paragraph]], [_FRAME_WIDTH], commands, padding=7)

    thumbnail = FlowableImage(
        io.BytesIO(image), width=_THUMBNAIL_WIDTH, height=_THUMBNAIL_HEIGHT
    )
    thumbnail.hAlign = "RIGHT"
    return _table(
        [[paragraph, thumbnail]],
        [_FRAME_WIDTH - _THUMBNAIL_WIDTH - 14, _THUMBNAIL_WIDTH + 14],
        commands + [("ALIGN", (1, 0), (1, -1), "RIGHT")],
        padding=7,
    )


def _routes_block(day: TripDay, labels: dict[str, object], styles) -> Table:
    """渲染当天相邻地点之间的路线摘要。"""
    rows = []
    for segment in day.routes:
        route = segment.route
        detail = "  ·  ".join(
            [
                _distance(route.distance_meters),
                _route_minutes(route.duration_seconds, labels),
                str(labels["transport"][route.mode]),
            ]
        )
        rows.append(
            [
                Paragraph(_text(f"{segment.origin_name} → {segment.destination_name}"), styles["cell"]),
                Paragraph(_text(detail), styles["cell_muted"]),
            ]
        )
    return _table(rows, [_FRAME_WIDTH * 0.54, _FRAME_WIDTH * 0.46], padding=4)


def _meals_block(day: TripDay, labels: dict[str, object], styles) -> Table:
    """渲染当天餐饮建议。"""
    rows = []
    for meal in day.meals:
        name = meal.name
        if meal.estimated_cost:
            name = f"{name}  ·  ¥{meal.estimated_cost:,.0f}"
        rows.append(
            [
                Paragraph(_text(labels["meal_types"].get(meal.type, meal.type)), styles["cell_muted"]),
                Paragraph(_text(name), styles["cell"]),
            ]
        )
    return _table(rows, [_FRAME_WIDTH * 0.22, _FRAME_WIDTH * 0.78], padding=4)


def _stay_block(day: TripDay, labels: dict[str, object], styles) -> Paragraph:
    """渲染当晚住宿摘要。"""
    hotel = day.hotel
    if hotel is None:
        return Paragraph(_text(labels["stay_empty"]), styles["small"])
    html = [f"<b>{_text(hotel.name)}</b>"]
    meta = []
    if hotel.average_price:
        meta.append(f"¥{hotel.average_price:,.0f}")
    if hotel.rating is not None:
        meta.append(str(labels["rating"]).format(rating=f"{hotel.rating:g}"))
    if meta:
        html.append(f"<font size=9 color='#77867d'>{_text('  ·  '.join(meta))}</font>")
    if hotel.address:
        html.append(f"<font size=9 color='#77867d'>{_text(hotel.address)}</font>")
    return Paragraph("<br/>".join(html), styles["item"])


def _section(title: object, styles) -> list:
    """生成区块标题及其上下的留白。"""
    return [
        Spacer(1, 4 * mm),
        Paragraph(_text(title), styles["section"]),
        Spacer(1, 1.8 * mm),
    ]


def _day_block(
    day: TripDay,
    labels: dict[str, object],
    styles,
    language: str,
    images: dict[tuple[int, int], bytes],
) -> list:
    """渲染单个自然日的标题、说明、景点、路线、餐饮与住宿。"""
    meta_bits = [day.date.isoformat(), str(labels["transport"][day.transportation])]
    if day.is_transfer_day:
        meta_bits.append(str(labels["transfer"]))
    weather = _weather_line(day)
    if weather:
        meta_bits.append(weather)
    if day.transfer_info:
        meta_bits.append(day.transfer_info)

    heading = [
        Paragraph(_text(f"{str(labels['day']).format(day=day.day_index)}  ·  {day.city}"), styles["day"]),
        Paragraph(_text("  ·  ".join(meta_bits)), styles["day_meta"]),
        HRFlowable(width="100%", thickness=0.6, color=_LINE, spaceBefore=5, spaceAfter=7),
    ]
    story: list = [KeepTogether(heading + [Paragraph(_text(day.description), styles["body"])])]

    if day.attractions:
        cards = [
            _attraction_block(
                index,
                attraction,
                labels,
                styles,
                language,
                images.get((day.day_index, index)),
            )
            for index, attraction in enumerate(day.attractions, start=1)
        ]
        story.append(KeepTogether(_section(labels["attractions"], styles) + [cards[0]]))
        for card in cards[1:]:
            story.extend([Spacer(1, 2.5 * mm), KeepTogether([card])])

    if day.routes:
        story.append(KeepTogether(_section(labels["routes"], styles) + [_routes_block(day, labels, styles)]))

    if day.meals:
        story.append(KeepTogether(_section(labels["meals"], styles) + [_meals_block(day, labels, styles)]))

    story.append(KeepTogether(_section(labels["stay"], styles) + [_stay_block(day, labels, styles)]))
    return story


def _page_decorator(canvas, doc, labels: dict[str, object], fonts: tuple[str, str]) -> None:
    """在每页底部绘制分隔线、来源说明与页码。"""
    body, _ = fonts
    canvas.saveState()
    canvas.setStrokeColor(_LINE)
    canvas.setLineWidth(0.5)
    canvas.line(_MARGIN, 14 * mm, _PAGE_SIZE[0] - _MARGIN, 14 * mm)
    canvas.setFillColor(_MUTED)
    canvas.setFont(body, 8)
    canvas.drawString(_MARGIN, 10.5 * mm, str(labels["footer"]))
    canvas.drawRightString(_PAGE_SIZE[0] - _MARGIN, 10.5 * mm, str(labels["page"]).format(page=doc.page))
    canvas.restoreState()


def _build_story(
    plan: TripPlan,
    labels: dict[str, object],
    styles,
    language: str,
    images: dict[tuple[int, int], bytes],
) -> list:
    """按封面信息、逐日安排、行前建议的顺序组织文档内容。"""
    city = " · ".join(plan.cities)
    meta = "  ·  ".join(
        [
            str(labels["meta_range"]).format(
                start=plan.start_date.isoformat(), end=plan.end_date.isoformat()
            ),
            str(labels["meta_days"]).format(days=len(plan.days)),
            str(labels["meta_travelers"]).format(count=plan.travelers),
        ]
    )
    stamp = "  ·  ".join(
        [
            str(labels["plan_id"]).format(plan_id=plan.plan_id),
            str(labels["generated"]).format(time=datetime.now().strftime("%Y-%m-%d %H:%M")),
        ]
    )
    story: list = [
        Paragraph(_text(str(labels["doc_title"]).format(city=city)), styles["title"]),
        Spacer(1, 1.5 * mm),
        Paragraph(_text(meta), styles["meta"]),
        Spacer(1, 5 * mm),
    ]
    story.extend(_budget_block(plan, labels, styles))
    if plan.warnings:
        story.extend([Spacer(1, 4 * mm), _warnings_block(plan, labels, styles)])
    story.extend([Spacer(1, 3 * mm), Paragraph(_text(stamp), styles["small"])])

    if plan.days:
        for day in plan.days:
            story.append(Spacer(1, 7 * mm))
            story.extend(_day_block(day, labels, styles, language, images))
    else:
        story.extend([Spacer(1, 6 * mm), Paragraph(_text(labels["empty"]), styles["body"])])

    if plan.overall_suggestions:
        story.extend(
            [
                Spacer(1, 8 * mm),
                Paragraph(_text(labels["advice"]), styles["section"]),
                Spacer(1, 2 * mm),
                _warnings_rule(),
                Paragraph(_text(plan.overall_suggestions), styles["body"]),
            ]
        )
    return story


def _warnings_rule() -> HRFlowable:
    """行前建议与行程主体之间的分隔线。"""
    return HRFlowable(width="100%", thickness=0.6, color=_LINE, spaceAfter=6)


def render_plan_pdf(
    plan: TripPlan,
    language: str = "zh",
    *,
    images: bool = True,
    image_provider: ImageProvider | None = None,
) -> bytes:
    """把完整行程渲染为 PDF 字节，供下载接口直接返回。"""
    normalized = language if language in _LABELS else "zh"
    labels = _LABELS[normalized]
    fonts = _fonts_for(normalized)
    styles = _styles(fonts)
    attachments = _load_images(plan, image_provider or fetch_attraction_image) if images else {}

    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=_PAGE_SIZE,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        bottomMargin=_MARGIN,
        title=f"TravelMind-AI {plan.plan_id}",
        author="TravelMind-AI",
        subject=" · ".join(plan.cities),
    )
    frame = Frame(
        _MARGIN,
        _MARGIN,
        _FRAME_WIDTH,
        _PAGE_SIZE[1] - 2 * _MARGIN,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="plan",
    )
    doc.addPageTemplates(
        [
            PageTemplate(
                id="plan",
                frames=[frame],
                onPage=lambda canvas, template: _page_decorator(canvas, template, labels, fonts),
            )
        ]
    )
    try:
        doc.build(_build_story(plan, labels, styles, normalized, attachments))
    except Exception as exc:
        raise PlanExportError("生成行程 PDF 失败") from exc
    return buffer.getvalue()
