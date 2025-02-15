from fastapi import FastAPI, Depends
from backend.api.routes.reviews import reviews_router

app = FastAPI()

# роутер, що відповідає саме за ревю
app.include_router(router=reviews_router, prefix='/api/v1')
