from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base, sessionmaker
from src.configs import (DB_HOST, DB_NAME, DB_PORT, POSTGRES_PASSWORD,
                         POSTGRES_USER)

SQLALCHEMY_DATABASE_URL = (
    f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

engine: AsyncEngine = create_async_engine(SQLALCHEMY_DATABASE_URL)

async_session_local = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with async_session_local() as session:
        yield session
        await session.commit()
