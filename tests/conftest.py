import json
import os
import sys
import time
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
import allure
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from api.client import TandoorAPIClient
from pages.login_page import LoginPage

# Загружаем переменные окружения
load_dotenv()

# ===================================================================
# КОНФИГУРАЦИЯ TESTS/CONFTEST.PY - ПОЛНОЕ ОГЛАВЛЕНИЕ
# ===================================================================

"""СОДЕРЖАНИЕ ФАЙЛА (структурированное по группам):

1. ПУТИ И НАСТРОЙКИ 
   ├── ROOT_DIR - корневая директория проекта
   ├── get_test_data_path() - путь к тестовым данным
   └── cleanup_old_screenshots() - очистка старых скриншотов

2. HOOKS PYTEST (перехватчики событий)
   ├── pytest_sessionstart() - перед началом сессии
   ├── pytest_sessionfinish() - после завершения сессии
   └── pytest_runtest_makereport() - создание скриншотов при падении

3. ФИКСТУРЫ API 
   ├── api_client() - клиент Tandoor API
   ├── test_data() - ссылки на рецепты из recipe_links.json
   └── recipe_data() - ГЛАВНАЯ: импорт рецептов с кешированием

4. ДАННЫЕ ДЛЯ ТЕСТОВ
   ├── basic_recipe_data() - простой рецепт для создания
   ├── meal_plan_data() - данные плана питания
   ├── test_meal_plan_data() - тестовые данные плана
   ├── entries_for_shopping_list() - данные для списка покупок
   └── test_recipe_data() - существующие/импортированные рецепты

5. ВРЕМЕННЫЕ ОБЪЕКТЫ (автоочистка)
   ├── temporary_meal_plan() - план питания
   ├── temporary_recipe() - рецепт
   ├── temporary_shopping_list() - список покупок
   ├── get_or_create_recipe() - рецепт (создает, если его нет)
   └── cleanup_test_data() - очистка тестовых данных

6. UI ФИКСТУРЫ (браузер и авторизация)
   ├── driver() - браузер Chrome
   ├── login() - авторизация (с проверкой)
   ├── login_page() - страница логина
   ├── meal_plan_page() - страница планов питания
   └── shopping_list_page() - страница списка покупок

7. UI ФИКСТУРЫ ДЛЯ ПЛАНОВ ПИТАНИЯ
   ├── temporary_meal_plan_for_ui() - создание/использование плана
   └── clean_test_plan_ui() - гарантия чистой среды для тестов
"""

# ======================== ПУТИ И НАСТРОЙКИ ========================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)


def get_test_data_path(filename):
    """Получаем правильный путь к файлам в test_data"""
    return os.path.join(ROOT_DIR, 'test_data', filename)


def cleanup_old_screenshots(days=1):
    """Удаляет скриншоты старше указанного количества дней"""
    try:
        current_time = time.time()
        for filename in os.listdir('.'):
            if (filename.startswith(('screenshot_', 'failure_', 'fail_'))
                    and filename.endswith('.png')):
                file_path = os.path.join('.', filename)
                if os.path.getctime(file_path) < current_time - (days * 24 * 60 * 60):
                    os.remove(file_path)
                    print(f"Удален старый скриншот: {filename}")
    except Exception as e:
        print(f"Ошибка при очистке скриншотов: {e}")


# ======================== HOOKS PYTEST ========================
@pytest.hookimpl
def pytest_sessionstart(session):
    """Удалить скриншоты старше 1 дня перед тестами"""
    print(" Очистка старых скриншотов...")
    cleanup_old_screenshots(days=1)


@pytest.hookimpl
def pytest_sessionfinish(session, exitstatus):
    """Удалить все скриншоты если все тесты прошли успешно"""
    if exitstatus == 0:
        print(" Все тесты прошли - удаляем все скриншоты")
        cleanup_old_screenshots(days=3)
    else:
        print(f"Упало тестов: {session.testsfailed}")
        print(" Скриншоты сохранены для отладки")
        cleanup_old_screenshots(days=1)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для автоматического создания скриншотов при падении тестов"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        try:
            for fixture_name in item.fixturenames:
                if 'browser' in fixture_name:
                    browser = item.funcargs[fixture_name]
                    timestamp = datetime.now().strftime("%H%M%S")
                    screenshot_name = f"fail_{item.name}_{timestamp}.png"
                    browser.save_screenshot(screenshot_name)
                    print(f"📸 Скриншот: {screenshot_name}")
                    break
        except Exception as e:
            print(f"Ошибка скриншота: {e}")


# ======================== ФИКСТУРЫ API ========================

@pytest.fixture(scope="session")
def api_client():
    """Фикстура для API клиента с токеном из окружения"""
    token = os.getenv('TANDOOR_TOKEN')
    assert token, "TANDOOR_TOKEN не найден!"
    return TandoorAPIClient(token=token)


@pytest.fixture(scope="session")
def test_data():
    """Загрузка ссылок из файла"""
    project_root = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(project_root, 'test_data', 'recipe_links.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['recipe_links']


@pytest.fixture(scope="session")
def recipe_data(api_client, test_data):
    """Импорт рецептов по ссылкам с кешированием результатов"""
    cache_file = "imported_recipes_cache.json"
    url_to_id_map = {}
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            url_to_id_map = json.load(f)

    imported_recipes = []

    for link in test_data:
        print(f"Проверяем рецепт по URL: {link}")

        if link in url_to_id_map:
            recipe_id = url_to_id_map[link]
            print(f"Рецепт уже импортирован ранее с ID: {recipe_id}")
            allure.attach(json.dumps({'link': link, 'recipe_id': recipe_id}, ensure_ascii=False),
                          name="Известный рецепт", attachment_type=allure.attachment_type.JSON)
            imported_recipes.append(recipe_id)
            continue

        response_data = api_client.import_recipe_from_url(link)

        if response_data is None:
            print(f"Пустой ответ при импорте: {link}")
            allure.attach('Пустой ответ', name='Ошибка импорта', attachment_type=allure.attachment_type.TEXT)
            continue

        status_code = response_data.get('status_code')

        if status_code != 200:
            print(f"Ошибка при импорте {link}, статус: {status_code}")
            allure.attach(f'Статус: {status_code}\nОтвет: {response_data.get("content")}',
                          name='Ошибка импорта', attachment_type=allure.attachment_type.TEXT)
            continue

        json_data = response_data.get('json')
        if json_data is None:
            print(f"Пустой JSON при импорте {link}")
            allure.attach('Пустой JSON в ответе', name='Ошибка импорта', attachment_type=allure.attachment_type.TEXT)
            continue

        if json_data.get('recipe_id') is not None:
            recipe_id = json_data['recipe_id']
            print(f"Рецепт успешно импортирован с ID: {recipe_id}")
            allure.attach(json.dumps(json_data, ensure_ascii=False), name='Импортированный рецепт',
                          attachment_type=allure.attachment_type.JSON)
            # сохраняем в кеш
            url_to_id_map[link] = recipe_id
            imported_recipes.append(recipe_id)
            # Логируем ответ в отчёте
            allure.attach(str(json_data), name="Импортированный рецепт", attachment_type=allure.attachment_type.JSON)
            print(f"Рецепт успешно импортирован с ID: {recipe_id}")


        elif 'recipe' in json_data and json_data.get('error') is False:
            print(f"Рецепт распарсен, но не сохранен. Сохраняем...")
            saved_response = api_client.save_recipe(json_data['recipe'])

            if saved_response and saved_response.get('status_code') == 201:
                saved_json = saved_response.get('json')
                if saved_json and 'id' in saved_json:
                    recipe_id = saved_json['id']
                    print(f" Рецепт сохранен с ID: {recipe_id}")
                    url_to_id_map[link] = recipe_id
                    imported_recipes.append(recipe_id)
                else:
                    print(f" Не удалось получить ID после сохранения: {saved_response}")
                    allure.attach(str(saved_response), name='Ошибка сохранения',
                                  attachment_type=allure.attachment_type.JSON)
            else:
                print(f" Ошибка при сохранении рецепта: {saved_response}")
            allure.attach(str(saved_response), name='Ошибка сохранения', attachment_type=allure.attachment_type.JSON)
        else:
            error_msg = json_data.get('msg', 'Неизвестная ошибка импорта')
            print(f" Ошибка импорта {link}: {error_msg}")
            allure.attach(error_msg, name="Ошибка импорта", attachment_type=allure.attachment_type.TEXT)


    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(url_to_id_map, f, ensure_ascii=False, indent=2)

    return imported_recipes


# =====================ДАННЫЕ ДЛЯ ТЕСТОВ====================

@pytest.fixture
def basic_recipe_data():
    """Базовые данные для создания простого рецепта"""
    return {
        "name": f"Картофельное пюре {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
        "steps": [
            {
                "instruction": "Сварить картофель",
                "ingredients": [
                    {
                        "food": {"name": "Картофель"},
                        "unit": {"name": "г"},
                        "amount": 500
                    },
                    {
                        "food": {"name": "Сливочное масло"},
                        "unit": {"name": "г"},
                        "amount": 50
                    }
                ]
            }
        ]
    }


@pytest.fixture
def meal_plan_data():
    """Создает обязательные данные для создания плана"""
    return {
        'title': 'Тест ' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
        'servings': 1.0,
        'from_date': datetime.now().isoformat() + 'Z',
        'meal_type': {"name": "Обед"}
    }


@pytest.fixture
def test_meal_plan_data():
    """Фикстура с тестовыми данными плана питания"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    return {
        "date": tomorrow,
        "meal_type": "обед",
        "title": f"Тестовый план питания {datetime.now().strftime('%H%M%S')}",
        "servings": 2
    }


@pytest.fixture
def entries_for_shopping_list():
    """Данные для добавления в лист покупок"""
    return {
        'food': {'name': 'Масло'},
        'amount': 100,
        'unit': {'name': 'грамм'}
    }


@pytest.fixture(scope="session")
def test_recipe_data():
    """Фикстура которая предоставляет тестовые данные о рецептах"""
    print("Загружаем тестовые данные о рецептах...")
    imported_path = get_test_data_path('imported_recipes.json')

    if os.path.exists(imported_path):
        with open(imported_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            imported_recipes = data.get('imported_recipes', [])
        print(f" Используем {len(imported_recipes)} импортированных рецептов из файла")
        return imported_recipes
    else:
        print(" Файл imported_recipes.json не найден, используем существующие рецепты из API")
        try:
            api_client = TandoorAPIClient()
            response = api_client.get_recipes(limit=3)
            existing_recipes = response.get('results', [])

            test_recipes = []
            for recipe in existing_recipes:
                test_recipes.append({
                    'id': recipe['id'],
                    'name': recipe.get('name', 'Test Recipe'),
                    'link': 'manual_creation'
                })

            print(f" Используем {len(test_recipes)} существующих рецептов из API")
            return test_recipes
        except Exception as e:
            print(f" Не удалось получить рецепты из API: {e}")
            return []


# ======================== ФИКСТУРЫ ВРЕМЕННЫХ ОБЪЕКТОВ ========================

@pytest.fixture
def temporary_meal_plan(api_client, meal_plan_data):
    """Создает временный план питания"""
    new_plan = api_client.create_meal_plan(meal_plan_data)
    assert new_plan['status_code'] == 201, f"Ожидался код 201, получен {new_plan.get('status_code')}"
    json_data = new_plan['json']
    assert 'id' in json_data, "ID плана не получен"

    yield json_data

    plan_id = json_data['id']
    success = api_client.delete_meal_plan(plan_id)
    if success:
        print(f" План с ID={plan_id} успешно удален")
    else:
        print(f"Не удалось удалить план с ID={plan_id}")


@pytest.fixture
def temporary_recipe(api_client, basic_recipe_data):
    """Универсальная фикстура для создания временного рецепта"""
    recipe_id = None
    try:
        new_recipe = api_client.create_recipe(basic_recipe_data)
        assert new_recipe['status_code'] == 201, f"Ожидался код 201, получен {new_recipe.get('status_code')}"
        json_data = new_recipe['json']
        recipe_id = json_data["id"]
        print(f"Создан временный рецепт: {json_data.get('name')} (ID: {recipe_id})")
        yield json_data
    finally:
        if recipe_id:
            try:
                api_client.delete_recipe(recipe_id)
            except Exception as e:
                print(f"Ошибка при удалении рецепта {recipe_id}: {e}")


@pytest.fixture
def temporary_shopping_list(api_client, entries_for_shopping_list):
    """Создает временный список покупок"""
    response = api_client.create_shopping_list_entry(entries_for_shopping_list)
    assert response.get('status_code') == 201, f"Ожидался код 201, получен {response.get('status_code')}"
    data_json = response.get('json', {})

    yield data_json

    shopping_list_id = data_json.get('id')
    if shopping_list_id:
        delete_response = api_client.delete_shopping_list(shopping_list_id)
        if delete_response.get('status_code') in [200, 204]:
            print(f" Запись {shopping_list_id} успешно удалена")
        else:
            print(f"Не удалось удалить запись {shopping_list_id}: {delete_response.get('content')}")


@pytest.fixture
def get_or_create_recipe(api_client, basic_recipe_data):
    """Получает существующий рецепт, если его нет - создает новый"""
    try:
        recipes_response = api_client.get_recipes()
        if recipes_response and recipes_response.get('count', 0) > 0:
            existing_recipe = recipes_response['results'][0]
            yield existing_recipe
    except Exception as e:
        print(f"Ошибка при поиске рецептов: {e}")

    new_recipe = api_client.create_recipe(basic_recipe_data)
    data_json = new_recipe.get('json', {})
    yield data_json
    if data_json.get('id'):
        delete_response = api_client.delete_recipe(data_json['id'])
        if delete_response.get('status_code') == 204:
            print(f" Рецепт с ID={data_json['id']} успешно удален")
        else:
            print(f"Рецепт с ID={data_json['id']} не удален")


@pytest.fixture
def cleanup_test_data(api_client):
    """Фикстура для очистки тестовых данных после теста"""
    created_plan_ids = []

    def _register_plan(plan_id):
        created_plan_ids.append(plan_id)

    yield _register_plan

    for plan_id in created_plan_ids:
        try:
            api_client.delete_meal_plan(plan_id)
            print(f"Очистка: удален план ID {plan_id}")
        except Exception as e:
            print(f"Ошибка очистки плана {plan_id}: {e}")


# ======================== ФИКСТУРЫ UI ========================

@pytest.fixture(scope="function")
def driver():
    """Фикстура браузера с автоматическим скачиванием драйвера"""

    # Создаем опции для Chrome
    chrome_options = Options()

    # Если запущено в CI, используем headless режим
    if os.getenv('CI') or os.getenv('GITLAB_CI'):
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # ВАЖНО: Если используем Selenium контейнер, не устанавливаем ChromeDriver
        if os.getenv('SELENIUM_REMOTE_URL'):
            # Используем Remote WebDriver для контейнера
            driver = webdriver.Remote(
                command_executor=os.getenv('SELENIUM_REMOTE_URL'),
                options=chrome_options
            )
        else:
            # Используем локальный ChromeDriver (ваш текущий подход)
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        # Локальная разработка
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.implicitly_wait(10)
    driver.get(os.getenv('BASE_URL'))

    yield driver
    driver.quit()

@pytest.fixture
def login(browser) -> LoginPage:
    """Фикстура для авторизации пользователя"""
    login_page = LoginPage(browser)
    login_page.open_login_page()
    login_page.login_user()
    assert login_page.is_login_successful(), "Логин не удался"
    return login_page


@pytest.fixture
def login_page(driver):
    """Автоматический логин для UI"""
    page = LoginPage(driver)
    page.login_user()
    return page


@pytest.fixture
def meal_plan_page(login_page):
    """Возвращает обьект mealplan для теста UI после автоматического логина"""
    from pages.meal_plan_page import MealPlanPage
    return MealPlanPage(login_page.driver)


@pytest.fixture
def shopping_list_page(login_page):
    """Возвращает обьект shoppinglist для теста UI после автоматического логина"""
    from pages.shopping_list_page import ShoppingListPage
    return ShoppingListPage(login_page.driver)


# ======================== ФИКСТУРЫ UI ДЛЯ ПЛАНОВ ========================
@pytest.fixture
def temporary_meal_plan_for_ui(meal_plan_page):
    """Проверяет существование плана, при отсутствии создает новый"""
    meal_plan_page.open_meal_plan_page()
    recipe_and_plan_name = 'Карамельный пудинг'
    tomorrow = datetime.today() + timedelta(days=1)

    if meal_plan_page.is_plan_visible(recipe_and_plan_name, timeout=5):
        print(f"План '{recipe_and_plan_name}' уже есть, используем его")
    else:
        print(f"Создаю новый план'{recipe_and_plan_name} с добавлением продуктов в корзину при создании'")
        success_create = meal_plan_page.create_plan_ui(
            day_number=tomorrow.day,
            recipe_name=recipe_and_plan_name,
            title="Еда на завтра",
            meal_type='Завтрак',
            servings='2'
        )
        assert success_create, "Не удалось создать план"

    yield recipe_and_plan_name

    if meal_plan_page.is_plan_visible(recipe_and_plan_name, timeout=3):
        meal_plan_page.delete_plan_by_name(recipe_and_plan_name)
        assert not meal_plan_page.is_plan_visible(recipe_and_plan_name, timeout=5), \
            f"План '{recipe_and_plan_name}' не удален фикстурой после теста"
    else:
        print(f"План '{recipe_and_plan_name}' уже удален тестом")


@pytest.fixture
def clean_test_plan_ui(meal_plan_page):
    """Фикстура для тестов планов питания с гарантией чистой среды"""
    plan_name = 'Крем Рафаэлло'
    meal_plan_page.open_meal_plan_page()

    if meal_plan_page.is_plan_visible(plan_name, timeout=2):
        print(f" Удаляю старый план '{plan_name}' перед тестом")
        meal_plan_page.delete_plan_by_name(plan_name)

    yield plan_name

    print(f" Очищаю план '{plan_name}' после теста")
    time.sleep(1)
    meal_plan_page.open_meal_plan_page()

    try:
        if meal_plan_page.is_plan_visible(plan_name, timeout=1):
            deleted = meal_plan_page.delete_plan_by_name(plan_name)
            if deleted:
                print(f" План '{plan_name}' удален после теста")
            else:
                print(f" Не удалось удалить план '{plan_name}'")
    except Exception as e:
        print(f" Ошибка при очистке: {e}. Продолжаем...")
