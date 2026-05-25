import pytest
import allure

@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Проверка healthcheck")
@pytest.mark.asyncio
async def test_healthcheck(client):
    with allure.step("Запрос на /utils/check-db"):
        response = await client.get("/utils/check-db")
    with allure.step("Проверка статуса"):
        assert response.status_code == 200

@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Создание пользователя")
@pytest.mark.asyncio
async def test_user_happy_path(client):
    payload = {"username": "sergey_kobzev", "email": "sergey@example.com"}
    with allure.step("POST запрос"):
        response = await client.post("/users/", json=payload)
        assert response.status_code == 200