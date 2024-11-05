from __future__ import annotations

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from utils import env
from .models._base import Base

engine = create_async_engine(env.DATABASE_URL, echo=False)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
