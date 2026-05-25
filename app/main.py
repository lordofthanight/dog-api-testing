from fastapi import FastAPI
from app.routes import users, items, utils # Импортируем модули роутов

app = FastAPI()

# Убедись, что префиксы в точности такие, как в тестах
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(utils.router, prefix="/utils", tags=["utils"])
