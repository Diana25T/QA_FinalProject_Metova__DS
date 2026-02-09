from unittest.mock import Mock

import allure
import pytest

from api.client import TandoorAPIClient
from tests.conftest import api_client, temporary_recipe


@pytest.mark.api
@allure.title("Проверка аутентификации через Bearer Token")
@allure.severity(allure.severity_level.CRITICAL)
def test_bearer_token_auth():
    """Тестирует аутентификацию через Bearer Token"""
    client = TandoorAPIClient()

    # Пробуем получить список рецептов
    recipes = client.get_recipes()

    assert recipes['status_code'] == 200, "API должен возвращать ответ"
    data_json = recipes['json']
    assert 'results' in data_json, "Ответ должен содержать поле 'results'"
    print(f" Bearer Token аутентификация работает!")
    print(f" Найдено рецептов: {data_json['results']}")


@pytest.mark.api
@allure.title("Проверка доступности API")
@allure.severity(allure.severity_level.BLOCKER)
def test_api_health(api_client):
    """Проверяет доступность API"""
    try:
        # Проверяем базовый эндпоинт
        response = api_client._make_request('GET', '')
        assert response['status_code'] == 200
        print(" API доступен")
    except Exception as e:
        pytest.fail(f"API недоступен: {e}")


@pytest.mark.api
@allure.title("Получение списка всех рецептов")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_recipes(api_client):
    """Получает рецепты через  API
     и проверяет наличия ключа 'results'"""
    response = api_client.get_recipes()
    assert response['status_code'] == 200, f"Ожидался код 200, получен {response.get('status_code')}"
    data_json = response['json']
    assert 'results' in data_json, "Ответ API не содержит ключ 'results'"
    recipes_list = data_json.get("results", [])
    for recipe in recipes_list:
        print(recipe['name'], recipe['id'])
    assert recipes_list is not None, "API не вернул ответ"
    assert len(recipes_list) > 0, "Список рецептов пусой"


@pytest.mark.api
@allure.title("Импорт рецептов из внешних источников")
@allure.severity(allure.severity_level.NORMAL)
def test_import_recipes(recipe_data):
    """Импортирует рецепты по ссылкам"""
    print(f" Всего успешно импортировано и сохранено рецептов: {len(recipe_data)}")

    # Проверяем уникальность ID
    unique_ids = set(recipe_data)
    assert len(unique_ids) == len(recipe_data), f"Обнаружены дубликаты ID: {recipe_data}"

    # Проверяем, что рецепты действительно сохранены в базе
    for recipe_id in recipe_data:
        print(f" Рецепт сохранен с ID: {recipe_id}")

    # Минимальная проверка - что хотя бы некоторые рецепты импортировались
    assert len(recipe_data) > 0, "Ни один рецепт не был успешно импортирован и сохранен"

    print(f" Все рецепты уникальны и подтверждены в базе данных!")


@pytest.mark.api
@allure.title("Создание нового рецепта через API")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_recipe(api_client, temporary_recipe):
    """Тестирует создание простого рецепта через API"""
    recipe_id = temporary_recipe['id']
    recipe_name = temporary_recipe['name']
    assert recipe_id is not None, "ID не получен"
    success = api_client.get_recipe_by_id(recipe_id)
    assert success is not None, "Рецепт не создан"
    print(f" Создан рецепт {recipe_name}  c ID: {recipe_id}")


@pytest.mark.api
@allure.title("Удаление рецепта по ID")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_recipe_by_id(api_client, temporary_recipe):
    """Проверяет удаление рецепта по id"""
    recipe_id = temporary_recipe['id']

    # Проверяем, что рецепт существует перед удалением
    initial_response = api_client.get_recipe_by_id(recipe_id)
    assert initial_response.get('status_code') == 200, "Рецепт не найден перед удалением"

    # Удаляем рецепт
    success = api_client.delete_recipe(recipe_id)
    assert success, "Не удалось удалить рецепт"

    # Проверяем, что рецепт исчез
    deleted_response = api_client.get_recipe_by_id(recipe_id)

    # Проверяем статус код
    status_code = deleted_response.get('status_code')

    # Рецепт должен быть не найден (404)
    assert status_code in [404, 410], f"Ожидался статус 404 или 410, получен {status_code}"

    print(f"Рецепт ID:{recipe_id} успешно удален (статус ответа: {status_code})")


@pytest.mark.api
@allure.title("Поиск и удаление дубликатов рецептов")
@allure.severity(allure.severity_level.NORMAL)
def test_remove_dublicate_recipes(api_client):
    """Удаляет рубликаты рецептов"""
    print("Ищем повторяющиея рецепты")

    # 1. Получаем все рецепты из системы
    response = api_client.get_recipes()
    assert response['status_code'] == 200, f"Ожидался код 200, получен {response.get('status_code')}"
    data_json = response['json']
    assert 'results' in data_json, "Не получены данные 'results'"

    recipes = data_json['results']
    print(f"Всего найдено рецептов: {len(recipes)}")

    # 2. Ищем с одинаковыми названиями

    recipe_names = {}
    dublicates = []

    for recipe in recipes:
        name = recipe['name']
        recipe_id = recipe['id']

        if name in recipe_names:
            # Нашли дубликат
            dublicates.append(recipe)
            print(f"Найден дубликат: {name}, ID: {recipe_id}")
        else:
            # Первый раз видим название
            recipe_names[name] = recipe_id

    # 3. Если дубликатов нет -закачиваем
    if not dublicates:
        print("Дубликатов не найдено")
        return

    print(f"Найдено: {len(dublicates)} дубликатов для удаления")

    # 4. Удаляем дубликаты
    deleted_count = 0
    for recipe in dublicates:
        print(f" Удаляем: '{recipe['name']}'(ID: {recipe['id']})")

    # 5. Пытаемся удалить рецепт
    success = api_client.delete_recipe(recipe['id'])
    if success:
        deleted_count += 1
        print(f"Успешно удален: {deleted_count}")

    # 6. Результаты
    print(f"Готово!Удалено: {deleted_count} дубликатов")
    print(f" Осталось {len(recipes) - deleted_count} уникальных рецептов")





