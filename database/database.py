from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from database.models import Base
from config.config import settings

async_engine = create_async_engine(url=settings.database_url_aisqlite, echo=True)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

#инициализируем базу данных и ее таблицы
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)