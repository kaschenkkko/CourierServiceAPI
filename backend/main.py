from fastapi import FastAPI

from backend.users.routers import user_router

app = FastAPI(title='Courier Service API ')


app.include_router(user_router)
