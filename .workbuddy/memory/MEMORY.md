# 项目长期记忆

## 架构约定

- 分层：`routers`（HTTP/WS）→ `services`（编排）→ `integrations` / `storage`；接口模型放 `schemas`，领域模型放 `models`，两者分开维护。
- `TripPlan`（`app/models/trip.py`）是已校验的完整行程，持久化在 SQLite `trip_plans.plan_json`；`plan_id` 是导出行程的稳定入口。
- 中文注释与中文 docstring 是本项目风格；测试用 `unittest` + `fastapi.testclient`。

## 行程导出 PDF

- 渲染服务：`app/services/plan_export.py`（ReportLab，`render_plan_pdf(plan, language)`）；接口：`GET /api/trip/plan/{plan_id}/export.pdf?language=`。
- 字体：优先内嵌系统 TrueType（STHeiti / wqy-zenhei），可用 `TRAVELMIND_PDF_FONT` 指定；兜底用 ReportLab CID 字体。ReportLab 不支持 CFF/OTF 轮廓，PingFang 与 Noto CJK 的 .ttc 会注册失败。
- 图片：`app/services/image_fetcher.py` 负责下载 + 裁剪成 480×360 JPEG；`render_plan_pdf` 的 `image_provider` 契约是「返回可直接嵌入的成品图片字节」，直接塞原图会让 PDF 膨胀到 MB 级。
- 本地核对 PDF 的办法：`uv run --with pypdfium2 --with pillow python`，用 `pypdfium2` 渲染成 PNG 再读图。

## 常用命令

- 后端测试：`./.venv/bin/python -m unittest discover -s tests -v`
- 前端：`cd ui && npm run lint && npm run build`
- 本地 Python 环境在仓库根的 `.venv`（非系统 python）。
