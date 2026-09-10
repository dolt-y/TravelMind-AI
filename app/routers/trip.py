"""旅行规划任务提交、状态订阅、结果和历史查询接口。"""

from __future__ import annotations

import asyncio
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, WebSocket
from pydantic import ValidationError

from app.models.trip import TripCityStay, TripPlan, TripPlanningRequest
from app.schemas.trip import (
    TripCreateResponse,
    TripHistoryItemResponse,
    TripHistoryResponse,
    TripPlanRequest,
    TripPlanResponse,
    TripTaskResponse,
)
from app.services.trip_planner_service import TripPlannerService
from app.storage.trip_repository import TripRepository, TripRepositoryError
from app.xhs_session import XHSClientSession, require_xhs_session


router = APIRouter(prefix="/api/trip", tags=["trip"])


def _domain_request(request: TripPlanRequest) -> TripPlanningRequest:
    """将 REST 输入转换为不依赖接口层的旅行需求。"""
    travel_days = (request.end_date - request.start_date).days + 1
    cities = (
        [TripCityStay(city=item.city.strip(), days=item.days) for item in request.cities]
        if request.cities
        else [TripCityStay(city=request.city, days=travel_days)]
    )
    return TripPlanningRequest(
        cities=cities,
        start_date=request.start_date,
        end_date=request.end_date,
        transportation=request.transportation,
        accommodation=request.accommodation.strip(),
        preferences=[item.strip() for item in request.preferences if item.strip()],
        extra_requirements=request.free_text_input.strip(),
        language=request.language,
        note_limit=request.note_limit,
        travelers=request.travelers,
        total_budget=request.total_budget,
        hotel_budget_max=request.hotel_budget_max,
    )


def _plan_response(plan: TripPlan) -> TripPlanResponse:
    """将完整领域计划映射为独立 REST 响应模型。"""
    return TripPlanResponse.model_validate(plan.model_dump(mode="json"))


def _task_response(repository: TripRepository, task_id: str) -> TripTaskResponse:
    """读取任务快照，并在完成时附带已持久化的完整行程。"""
    task = repository.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="旅行规划任务不存在")
    plan = repository.get_plan(task.plan_id) if task.plan_id else None
    return TripTaskResponse(
        **task.model_dump(mode="json"),
        result=_plan_response(plan) if plan else None,
    )


@router.post("/plan", response_model=TripCreateResponse, status_code=202)
def create_trip_plan(
    request: TripPlanRequest,
    background_tasks: BackgroundTasks,
    session: XHSClientSession = Depends(require_xhs_session),
) -> TripCreateResponse:
    """持久化旅行需求并在后台启动完整规划。"""
    try:
        domain_request = _domain_request(request)
        repository = TripRepository()
        task_id = uuid4().hex
        repository.create_task(task_id, domain_request)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except TripRepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # NOTE: BackgroundTasks 在响应发出后执行同步编排，提交接口只负责返回任务标识。
    background_tasks.add_task(
        TripPlannerService(repository=repository, xhs_cookie=session.cookie).run_task,
        task_id,
        domain_request,
    )
    return TripCreateResponse(
        task_id=task_id,
        status="submitted",
        status_url=f"/api/trip/status/{task_id}",
        ws_url=f"/api/trip/ws/{task_id}",
        message="旅行规划任务已提交",
    )


@router.get("/status/{task_id}", response_model=TripTaskResponse)
def get_trip_status(task_id: str) -> TripTaskResponse:
    """返回任务最新进度，并在完成后附带完整行程。"""
    try:
        return _task_response(TripRepository(), task_id)
    except TripRepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.websocket("/ws/{task_id}")
async def watch_trip_status(websocket: WebSocket, task_id: str) -> None:
    """推送持久化任务状态；晚连接或服务重启后仍能得到当前快照。"""
    await websocket.accept()
    last_updated = ""
    try:
        while True:
            repository = TripRepository()
            task = repository.get_task(task_id)
            if task is None:
                await websocket.send_json({"code": "TRIP_TASK_NOT_FOUND", "message": "旅行规划任务不存在"})
                await websocket.close(code=1008)
                return
            updated = task.updated_at.isoformat()
            if updated != last_updated:
                await websocket.send_json(
                    _task_response(repository, task_id).model_dump(mode="json")
                )
                last_updated = updated
            if task.status in {"completed", "failed"}:
                await websocket.close()
                return
            await asyncio.sleep(0.6)
    except TripRepositoryError:
        await websocket.close(code=1011)


@router.get("/history", response_model=TripHistoryResponse)
def list_trip_history(
    limit: int = Query(default=20, ge=1, le=100),
) -> TripHistoryResponse:
    """返回最近完成的旅行计划摘要。"""
    try:
        items = TripRepository().list_plans(limit)
    except TripRepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return TripHistoryResponse(
        items=[TripHistoryItemResponse.model_validate(item) for item in items]
    )


@router.get("/plan/{plan_id}", response_model=TripPlanResponse)
def get_trip_plan(plan_id: str) -> TripPlanResponse:
    """按计划 ID 返回可恢复查看的完整旅行计划。"""
    try:
        plan = TripRepository().get_plan(plan_id)
    except TripRepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if plan is None:
        raise HTTPException(status_code=404, detail="旅行计划不存在")
    return _plan_response(plan)
