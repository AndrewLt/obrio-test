import json
from datetime import datetime
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response
from backend.api.logic.reviews import get_app_review

reviews_router = APIRouter()

def datatime_converter_json(dict_date: dict):
    if isinstance(dict_date, datetime):
        return dict_date.__str__()


@reviews_router.get('/get-review')
async def get_review(
        app_id: int = Query(default=None, ge=1),
        task_id: str = Query(default=None, min_length=36, max_length=36),
        # використати в тому випадку, якщо потрібно отримати увесь об'єкт
        raw: bool = False
):
    if not app_id and not task_id:
        return JSONResponse(status_code=400, content={'message': 'fill app_id or task_id field'})
    # напевно найкраще було б розділити на різні ендпоінти
    # але вже як є :)
    result = await get_app_review(
        app_id=app_id,
        task_id=task_id,
        raw=raw
    )
    # обробка коли є message
    if message := result.get('message'):
        if message == 'inProgress':
            JSONResponse(status_code=202, content=result)
        elif message == 'created':
            JSONResponse(status_code=201, content=result)

    data = json.dumps(result, default=datatime_converter_json)
    return Response(status_code=200, content=data)
