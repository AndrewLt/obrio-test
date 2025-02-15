import os
import json
import tempfile
from datetime import datetime, timedelta
from uuid import uuid4
from backend.db.mongo_client_async import tasks_collection


async def get_app_review(
        app_id: int,
        task_id: str,
        raw: bool
) -> dict:
    exclude = {'_id': 0, 'evaluatedReviews': 0, 'rawReviews': 0}
    if raw:
        exclude = {'_id': 0}

    # спроба за app_id або task_id знайти репорт
    # тільки якщо по app_id то це повинен бути свіжий запис
    if result := await tasks_collection.find_one({
        'status': 'done',
        '$or': [
            {'taskId': task_id},
            {'appId': app_id, 'reviewDate': {'$gte': datetime.now() - timedelta(days=2)}}
        ]
    }, exclude):
        return result

    # якщо дані за таким app_id вже готуються
    # видати той самий taskId аби не робити кілька задач з однаковим app_id
    if task := await tasks_collection.find_one({
        'status': 'created',
        'appId': app_id
    }):
        return {'message': 'created', 'taskId': task.get('taskId')}

    # якщо усе попереднє не підходить, то створюємо новий запис в БД
    # і даємо унікальний ІД аби доступитися до цього запису
    generated_task_id = str(uuid4())
    await tasks_collection.insert_one({
        'taskId': generated_task_id,
        'status': 'created',
        'appId': app_id
    })
    return {'message': 'created', 'taskId': generated_task_id}
