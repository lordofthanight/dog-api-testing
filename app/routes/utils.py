from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session

router = APIRouter()

@router.get("/check-db")
async def check_db(session: AsyncSession = Depends(get_session)):
    try:
        # Используй await обязательно!
        await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        # Если будет ошибка, мы увидим её описание в консоли pytest
        print(f"DB Check Error: {e}") 
        raise HTTPException(status_code=503, detail="Database connection failed")
