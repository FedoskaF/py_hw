import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers

# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Michail", "last_name": "Smirnov", "email": "msm@gmail.com", "password": "1234"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "first_name": "Michail",
        "last_name": "Smirnov",
        "email": "msm@gmail.com",
        "id": result_data["id"]
    }

# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller1 = sellers.Seller(
        first_name="Michail", last_name="Smirnov", email="msm@gmail.com", password="1234"
    )
    seller2 = sellers.Seller(
        first_name="Cazzi", last_name="Opeia", email="tattoo@ya.ru", password="123456"
    )

    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    result_data = response.json()

    assert result_data == {
        "sellers": [
            {
                "first_name": "Michail",
                "last_name": "Smirnov",
                "email": "msm@gmail.com",
                "id": seller1.id
            },

            {
                "first_name": "Cazzi",
                "last_name": "Opeia",
                "email": "tattoo@ya.ru",
                "id": seller2.id,
            }
        ]
    }


# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller1 = sellers.Seller(
        first_name="Michail", last_name="Smirnov", email="msm@gmail.com", password="1234")

    db_session.add_all([seller1])
    await db_session.flush()

    book = books.Book(author="David D. Burns", title="Feeling Good", year=2023, count_pages=600, seller_id=seller1.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    result_data = response.json()

    assert result_data == {
        "first_name": "Michail",
        "last_name": "Smirnov",
        "email": "msm@gmail.com",
        "books": [
                    {
                        "author": "David D. Burns",
                        "title": "Feeling Good",
                        "year": 2023,
                        "count_pages": 600,
                        "id": book.id,
                        "seller_id": seller1.id
                    }

        ]
    }


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(
        first_name="Michail", last_name="Smirnov", email="msm@gmail.com", password="1234"
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления данных о продавце
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(
        first_name="Michail", last_name="Smirnov", email="msm@gmail.com", password="1234")

    db_session.add(seller)
    await db_session.flush()

    new_data = {"id": seller.id,
                "first_name": "Cazzi",
                "last_name": "Opeia",
                "email": "tattoo@ya.ru"
                }
    
    response = await async_client.put(f"/api/v1/sellers/{seller.id}", json=new_data)

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    result_data = response.json()

    assert result_data["id"] == seller.id
    assert result_data["first_name"] == new_data["first_name"]
    assert result_data["last_name"] == new_data["last_name"]
    assert result_data["email"] == new_data["email"]
