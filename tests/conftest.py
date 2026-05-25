import json
import asyncio
import pytest
import allure
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.database import get_session

DB_URL = "postgresql+asyncpg://postgres:1234@127.0.0.1:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(DB_URL, pool_pre_ping=True, pool_reset_on_return=None)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def session(engine):
    async_session_factory = async_sessionmaker(
        bind=engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    async with async_session_factory() as s:
        yield s
        # Безопасный teardown для работы с allure-pytest в Python 3.13
        try:
            await s.rollback()
        except RuntimeError:
            pass

@pytest.fixture
async def client(session):
    app.dependency_overrides[get_session] = lambda: session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        orig_get, orig_post = c.get, c.post

        async def annotated_get(*args, **kwargs):
            res = await orig_get(*args, **kwargs)
            allure.attach(
                body=f"URL: {args[0]}\nStatus: {res.status_code}\nBody: {res.text}", 
                name="GET", 
                attachment_type=allure.attachment_type.TEXT
            )
            return res

        async def annotated_post(*args, **kwargs):
            res = await orig_post(*args, **kwargs)
            allure.attach(
                body=f"URL: {args[0]}\nPayload: {json.dumps(kwargs.get('json', {}), ensure_ascii=False)}\nStatus: {res.status_code}\nBody: {res.text}", 
                name="POST", 
                attachment_type=allure.attachment_type.TEXT
            )
            return res

        c.get, c.post = annotated_get, annotated_post
        yield c
        
    app.dependency_overrides.clear()