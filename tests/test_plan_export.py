"""行程导出 PDF 的渲染和接口边界测试。"""

from __future__ import annotations

from datetime import date, datetime, timezone
from io import BytesIO
from unittest.mock import patch
import unittest

from fastapi.testclient import TestClient
from PIL import Image

from app.models.hotel import Hotel
from app.models.poi import POILocation
from app.models.route import RouteEndpoint, RoutePlan
from app.models.trip import TripBudget, TripDay, TripMeal, TripPlan, TripRouteSegment
from app.models.weather import WeatherForecast
from app.models.xhs import AttractionCandidate
from app.services.image_fetcher import THUMBNAIL_SIZE, _to_thumbnail
from app.services.plan_export import render_plan_pdf
from main import app

PLAN_ID = "plan-export-test"
PHOTO_URL = "https://cdn.example.test/attraction-1.jpg"
IMAGE_XOBJECT_MARKER = b"/Subtype /Image"


def _fake_image(url: str) -> bytes:
    """生成固定图片字节，替代导出时的真实下载。"""
    assert url == PHOTO_URL
    buffer = BytesIO()
    Image.new("RGB", (640, 480), (46, 107, 74)).save(buffer, format="JPEG")
    return buffer.getvalue()


def _plan(*, with_days: bool = True) -> TripPlan:
    """构造一份包含景点、路线、餐饮和住宿的完整行程。"""
    attraction = AttractionCandidate(
        name="景点一",
        name_zh="景点一",
        name_en="Place One",
        reason="来自旅行笔记的推荐",
        duration=120,
        reservation_required=True,
        poi_id="poi-1",
        address="示例路 1 号",
        location=POILocation(longitude=114.05, latitude=22.55),
        rating=4.6,
        photos=[PHOTO_URL],
    )
    route = RoutePlan(
        provider="amap",
        origin=RouteEndpoint(
            name="景点一",
            address="示例路 1 号",
            city="深圳",
            location=POILocation(longitude=114.0, latitude=22.5),
        ),
        destination=RouteEndpoint(
            name="景点二",
            address="示例路 2 号",
            city="深圳",
            location=POILocation(longitude=114.1, latitude=22.6),
        ),
        mode="transit",
        distance_meters=8600,
        duration_seconds=2400,
    )
    days = (
        [
            TripDay(
                day_index=1,
                date=date(2026, 10, 1),
                city="深圳",
                description="第一天安排核心景点。",
                transportation="transit",
                attractions=[attraction],
                meals=[TripMeal(type="lunch", name="午餐", estimated_cost=80)],
                hotel=Hotel(id="hotel-1", name="示例酒店", city="深圳", average_price=600),
                weather=WeatherForecast(
                    provider="amap",
                    city="深圳",
                    date=date(2026, 10, 1),
                    day_weather="晴",
                    day_temperature=30,
                    night_temperature=24,
                ),
                routes=[TripRouteSegment(origin_name="景点一", destination_name="景点二", route=route)],
            )
        ]
        if with_days
        else []
    )
    return TripPlan(
        plan_id=PLAN_ID,
        cities=["深圳"],
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 1),
        travelers=2,
        days=days,
        budget=TripBudget(
            attractions=100,
            hotels=600,
            meals=80,
            transportation=30,
            total=810,
            target=3000,
        ),
        overall_suggestions="出发前确认开放时间。",
        warnings=["门票费用未包含。"],
        created_at=datetime.now(timezone.utc),
    )


class ImageThumbnailTest(unittest.TestCase):
    """验证缩略图裁剪和异常图片处理。"""

    def test_thumbnail_is_cropped_to_fixed_size(self) -> None:
        """宽高比不同的原图都应裁剪为统一尺寸的 JPEG。"""
        buffer = BytesIO()
        Image.new("RGB", (1000, 200), (10, 20, 30)).save(buffer, format="PNG")

        result = _to_thumbnail(buffer.getvalue())

        self.assertIsNotNone(result)
        with Image.open(BytesIO(result or b"")) as thumbnail:
            self.assertEqual(thumbnail.size, THUMBNAIL_SIZE)
            self.assertEqual(thumbnail.format, "JPEG")

    def test_thumbnail_returns_none_for_broken_payload(self) -> None:
        """无法解析的字节不应抛错。"""
        self.assertIsNone(_to_thumbnail(b"not-an-image"))


class PlanExportRenderTest(unittest.TestCase):
    """验证 PDF 渲染结果是一份可打开的文档。"""

    def test_render_returns_pdf_for_each_language(self) -> None:
        """中文、英文和日文都应生成有效的 PDF 字节。"""
        plan = _plan()
        for language in ("zh", "en", "ja"):
            with self.subTest(language=language):
                payload = render_plan_pdf(plan, language, image_provider=_fake_image)
                self.assertTrue(payload.startswith(b"%PDF-"))
                self.assertIn(b"ReportLab", payload)
                self.assertGreater(len(payload), 2000)

    def test_render_embeds_attraction_photo(self) -> None:
        """启用图片时内嵌图像对象，关闭时不内嵌。"""
        with_image = render_plan_pdf(_plan(), "zh", image_provider=_fake_image)
        without_image = render_plan_pdf(_plan(), "zh", images=False)

        self.assertIn(IMAGE_XOBJECT_MARKER, with_image)
        self.assertNotIn(IMAGE_XOBJECT_MARKER, without_image)
        self.assertGreater(len(with_image), len(without_image))

    def test_render_survives_unavailable_photo(self) -> None:
        """图片下载失败时只保留文字，不影响导出。"""
        payload = render_plan_pdf(_plan(), "zh", image_provider=lambda _url: None)

        self.assertTrue(payload.startswith(b"%PDF-"))
        self.assertNotIn(IMAGE_XOBJECT_MARKER, payload)

    def test_render_accepts_empty_itinerary(self) -> None:
        """没有逐日安排的计划也应能导出。"""
        payload = render_plan_pdf(_plan(with_days=False), "zh", images=False)
        self.assertTrue(payload.startswith(b"%PDF-"))

    def test_render_falls_back_to_chinese_for_unknown_language(self) -> None:
        """无法识别的语言标记退回中文排版而不是报错。"""
        payload = render_plan_pdf(_plan(), "fr", images=False)
        self.assertTrue(payload.startswith(b"%PDF-"))


class PlanExportEndpointTest(unittest.TestCase):
    """验证导出接口的响应类型、文件头与缺失计划处理。"""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_export_returns_pdf_attachment(self) -> None:
        """已保存的行程应返回可下载的 PDF 附件。"""
        with patch("app.routers.trip.TripRepository") as repository, patch(
            "app.services.plan_export.fetch_attraction_image", _fake_image
        ):
            repository.return_value.get_plan.return_value = _plan()
            response = self.client.get(
                f"/api/trip/plan/{PLAN_ID}/export.pdf", params={"language": "en"}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        disposition = response.headers["content-disposition"]
        self.assertIn("attachment", disposition)
        self.assertIn("filename*=UTF-8''", disposition)
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertIn(IMAGE_XOBJECT_MARKER, response.content)

    def test_export_can_skip_images(self) -> None:
        """images=false 时不下载图片，返回纯文字 PDF。"""
        with patch("app.routers.trip.TripRepository") as repository:
            repository.return_value.get_plan.return_value = _plan()
            response = self.client.get(
                f"/api/trip/plan/{PLAN_ID}/export.pdf",
                params={"language": "zh", "images": "false"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(IMAGE_XOBJECT_MARKER, response.content)

    def test_export_missing_plan_returns_404(self) -> None:
        """不存在的计划返回 404 而不是空文件。"""
        with patch("app.routers.trip.TripRepository") as repository:
            repository.return_value.get_plan.return_value = None
            response = self.client.get("/api/trip/plan/missing/export.pdf")

        self.assertEqual(response.status_code, 404)

    def test_export_rejects_unknown_language(self) -> None:
        """非法语言参数由接口校验拦截。"""
        response = self.client.get(
            f"/api/trip/plan/{PLAN_ID}/export.pdf", params={"language": "fr"}
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
