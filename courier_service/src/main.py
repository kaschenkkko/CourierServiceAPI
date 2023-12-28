from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from src.admin.admin import setup_admin
from src.delivery.routers import delivery_router
from src.users.routers import user_router

from .database import engine

app = FastAPI(title='Courier Service API', description='Прототип API сервиса курьерской доставки.')

setup_admin(app, engine)
app.include_router(user_router)
app.include_router(delivery_router)

limits = ['10/minute']
limiter = Limiter(key_func=get_remote_address, default_limits=limits)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)
