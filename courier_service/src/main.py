from fastapi import FastAPI
from src.admin.admin import setup_admin
from src.delivery.routers import delivery_router
from src.users.routers import user_router

from .database import engine

app = FastAPI(title='Courier Service API', description='Прототип API сервиса курьерской доставки.')

setup_admin(app, engine)
app.include_router(user_router)
app.include_router(delivery_router)
