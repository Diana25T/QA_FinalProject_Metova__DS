import allure
import pytest

from tests.conftest import api_client


# ===ТЕСТЫ ДЛЯ ПЛАНА ПИТАНИЯ===

@pytest.mark.api
@allure.title("Создание плана питания с использованием фикстуры")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_meal_plan_with_fixture(api_client, temporary_meal_plan):
    """Создает план с использованием фикстуры с автоматической очисткой"""
    plan_id = temporary_meal_plan.get('id')
    assert plan_id is not None

    # Проверка, что план есть
    response = api_client.get_meal_plan_id(plan_id)
    json_data = response['json']
    assert response is not None, 'План не найден после создания'
    assert json_data['id'] == plan_id, "План не найден после создания"


@pytest.mark.api
@allure.title("Получение и валидация списка планов питания")
@allure.severity(allure.severity_level.NORMAL)
def test_get_meal_plan_list_2(api_client):
    """Получает список планов и проверяет наличие обязательных полей:
    servings,
    meal_type,
    from_date
    """
    response = api_client.get_all_meal_plans()
    results = response.get("results", [])
    for plan in results:
        print(f"ID: {plan['id']}, Название: {plan.get('title')}")
        # Проверяем servings
        assert 'servings' in plan and plan['servings'] is not None, "Нет servings"
        # Проверяем meal_type
        assert 'meal_type' in plan and plan['meal_type'] is not None
        assert 'id' in plan['meal_type'], "В meal_type нет id"
        # Проверяем from_date
        assert 'from_date' in plan and plan['from_date'] is not None
        # Можно проверить формат даты, например, что это строка
        assert isinstance(plan['from_date'], str), "from_date не строка"


@pytest.mark.api
@allure.title("Полный цикл создания и проверки плана питания")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_meal_plan(api_client, temporary_meal_plan):
    """Создает план питания через API"""
    response = temporary_meal_plan
    assert response is not None, "Ответ API не получен"

    plan_id = response.get('id')
    assert plan_id is not None, "Список ID планов не получен"

    checking_the_plan = api_client.get_meal_plan_id(plan_id)
    assert checking_the_plan is not None, "План не создан"

    print(f" Создан план с ID:{plan_id} ")
    print(f"Создан план: {response.get('title')}")


@pytest.mark.api
@allure.title("Полный цикл создания и удаления плана питания")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_meal_plan(api_client, temporary_meal_plan):
    """Проверяет удаление плана через API используя фикстуру
    с автоматической очисткой"""
    meal_plan_id = temporary_meal_plan['id']
    print(f" Получен план с ID={meal_plan_id}")
    response = api_client.delete_meal_plan(meal_plan_id)
    assert response, "Не удалось удалить план"

    all_meal_plans = api_client.get_all_meal_plans()
    assert meal_plan_id not in all_meal_plans, "План найден после удаления"


# ===ТЕСТЫ ДЛЯ СПИСКА ПОКУПОК===

@pytest.mark.api
@allure.title("Получение списка покупок, не связанных с рецептами")
@allure.severity(allure.severity_level.NORMAL)
def test_get_shopping_list(api_client, entries_for_shopping_list):
    """Получает лист покупок"""
    # Фикстура entries_for_shopping_list это просто данные
    # Создаем сначала запись
    data = entries_for_shopping_list
    create_response = api_client.create_shopping_list_entry(data)
    assert create_response['status_code'] == 201, f"Ожидался код 201, получен {create_response.get('status_code')}"

    # Сохраняем ID созданной записи
    data_json = create_response.get("json", {})
    shopping_list_id = data_json.get('id')
    assert shopping_list_id is not None, "ID созданной записи не получен"

    # Получаем весь список покупок
    list_response = api_client.get_shopping_list_entry()
    assert list_response['status_code'] == 200

    list_data = list_response.get('json', {})
    results = list_data.get('results', [])

    # Проверяем что список не пустой
    assert len(results) > 0, "Список покупок пуст"

    # Находим нашу созданную запись в списке
    found_entry = None
    for entry in results:
        if entry.get('id') == shopping_list_id:
            found_entry = entry
            break

    # Проверяем, что запись найдена
    assert found_entry is not None, f"Запись с ID {shopping_list_id} не найдена в списке покупок"

    # Получаем название и ID добавленного продукта
    assert found_entry.get('food',{}).get('name')== data['food']['name']
    assert float(found_entry.get('amount', 0)) == float(data['amount'])
    assert found_entry.get('unit', {}).get('name') == data['unit']['name']

    # Очистка - удаляем созданную запись
    if shopping_list_id:
        cleanup_response = api_client.delete_shopping_list(shopping_list_id)
        assert cleanup_response['status_code'] in [200, 204], f"Запись не удалена {cleanup_response.get('status_code')}"


@pytest.mark.api
@allure.title("Добавление продукта в список покупок")
@allure.severity(allure.severity_level.NORMAL)
def test_add_to_shopping_list(api_client, temporary_shopping_list):
    """Добавляет данные в лист покупок используя фикстуру
    с автоматической очисткой  """
    data_json = temporary_shopping_list

    # Проверяем, что данные получены
    assert data_json is not None, "Не получены данные ответа"
    assert isinstance(data_json, dict), f"Ожидался словарь, получен {type(data_json)}"

    # Проверяем структуру ответ(обязательные поля)
    assert data_json['food']['name'] == 'Масло', f"Ожидался продукт 'Масло', получен {data_json['food']['name']}"
    assert data_json['amount'] == 100, f"Ожидалось количество 100, получено {data_json['amount']}"
    assert data_json['unit']['name'] == 'грамм', f"Ожидалась единица 'грамм', получена {data_json['unit']['name']}"

    entry_id = data_json['id']
    print(f" Успешно создана запись: {data_json['food']['name']} с ID: {entry_id}")
