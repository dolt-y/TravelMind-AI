"""TravelMind-AI 的 FastAPI 应用入口。"""

from fastapi import FastAPI

from app.routers.hotel import router as hotel_router
from app.routers.poi import map_router as map_poi_router
from app.routers.poi import router as poi_router
from app.routers.route import router as route_router
from app.routers.weather import map_router as map_weather_router
from app.routers.weather import router as weather_router
from app.routers.xhs import router as xhs_router
from app.routers.xhs_login import router as xhs_login_router

# 说明：API 应用只负责组装路由，具体业务由 integrations、services 和 storage 模块负责。
app = FastAPI(title="TravelMind-AI API")

app.include_router(xhs_router)
app.include_router(xhs_login_router)
app.include_router(poi_router)
app.include_router(map_poi_router)
app.include_router(weather_router)
app.include_router(map_weather_router)
app.include_router(hotel_router)
app.include_router(route_router)


@app.get("/")
def root():
    """返回服务基本信息，供启动检查使用。"""
    return {
        "message": "Hello TravelMind AI"
    }
