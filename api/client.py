import os
from typing import Dict, Optional, Any

import allure
import requests
from dotenv import load_dotenv


class TandoorAPIClient:
    """
      Клиент для работы с API Tandoor Recipes.
      Обеспечивает взаимодействие с сервером Tandoor через REST API.
      """

    def __init__(self):
        """Инициализация клиента API с загрузкой переменных окружения."""
        load_dotenv()
        self.base_url = os.getenv('BASE_URL', 'http://localhost').rstrip('/')
        self.token = os.getenv('TANDOOR_TOKEN')

        if not self.token:
            raise ValueError('TANDOOR_TOKEN не указан в переменных окружения')

        # Формируем заголовки для HTTP-запросов
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        print(" Используем Bearer Token аутентификацию")

    def _make_request(self, method: str, endpoint: str, **kwargs)-> Dict[str, Any]:
        """ Внутренний метод для выполнения HTTP-запросов

         Args:
            method: HTTP-метод (GET, POST, DELETE)
            endpoint: конечная точка API
            **kwargs: дополнительные параметры (json, data и т.д.)

        Returns:
            Dict[str, Any]: словарь с результатом запроса
                {
                    'status_code': int,  # код ответа
                    'json': Optional[Dict]  # JSON ответ (если есть)
                    'content': Optional[str]  # текст ответа (при ошибке)
                    'error': Optional[str]  # текст ошибки (при исключении) """
        # Формируем полный URL
        # Убираем лишние слеши
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        url = f"{self.base_url}/api/{endpoint}"

        try:
            response = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)
            print(f"[API] Запрос: {method} {url}")
            print(f"[API] Статус: {response.status_code}")
            print(f"[API] Ответ: {response.text[:200]}...")

            # Обработка ошибок HTTP (4xx, 5xx)
            if response.status_code >= 400:
                return {
                    'status_code': response.status_code,
                    'content': response.text
                }

            # Обработка успешного ответа
            if response.content:
                try:
                    json_data = response.json()
                    return {
                        'status_code': response.status_code,
                        'json': json_data
                    }
                except ValueError as e:
                    # Если не удалось распарсить JSON, возвращаем текст
                    print(f"Ошибка парсинга JSON: {e}")
                    return {
                        'status_code': response.status_code,
                        'content': response.text
                    }
            else:
                # Если ответ пустой
                return {
                    'status_code': response.status_code,
                    'json': None
                }

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return {'status_code': None, 'error': str(e)}

# === МЕТОДЫ ДЛЯ РЕЦЕПТОВ ===

    @allure.step("Импорт рецепта по URL: '{recipe_url}'")
    def import_recipe_from_url(self, recipe_url: str)  -> Dict[str, Any]:
        """Импортирует рецепт по URL """
        data = {
            "url": recipe_url,
            "data": "",  # Пустая строка
            "bookmarklet": 0
        }
        print(f" Импортируем рецепт по URL: '{recipe_url}'")
        response = self._make_request('POST', 'recipe-from-source/', json=data)
        print(f" Ответ импорта: {response}")
        return response

    @allure.step("Получить список всех рецептов")
    def get_recipes(self)  -> Dict[str, Any]:
        """Получает список всех рецептов"""
        return self._make_request('GET', 'recipe/')

    @allure.step("Получить рецепт по ID = {recipe_id}")
    def get_recipe_by_id(self, recipe_id: int)  -> Dict[str, Any]:
        """Получает рецепт по ID"""
        return self._make_request('GET', f'recipe/{recipe_id}/')

    @allure.step("Создать рецепт с данными")
    def create_recipe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создает рецепт"""
        return self._make_request('POST', 'recipe/', json=data)

    @allure.step("Удалить рецепт по ID = {recipe_id}")
    def delete_recipe(self, recipe_id: int) -> bool:
        """Удаляет рецепт по ID"""

        response = self._make_request('DELETE', f'recipe/{recipe_id}/')
        if response.get('status_code') is None:
            print(f"Ошибка сети для рецепта {recipe_id}: {response.get('error')}")
            return False

        status_code = response.get('status_code')
        print(f"Статус код ответа: {status_code}")

        # Смотрим статус код
        status_code = response.get('status_code')
        print(f"Статус код ответа : {status_code}")

        # Если статус код 204 - успешно удалено
        if status_code == 204:
            print(f"Рецепт {recipe_id} успешно удален")
            return True
        elif status_code == 404:
            print(f"Рецепт {recipe_id} не найден (уже удален или не существовал)")
            return True # Так как в фикстура создает и удалеет рецепты
        else:
            # Выводим дополнительную информацию
            error_content = response.get('content')
            if error_content:
                print(f"Ошибка удаления рецепта {recipe_id}: {error_content}")
            return False


# === МЕТОДЫ ДЛЯ ПЛАНОВ ПИТАНИЯ ===

    @allure.step("Создать план питания")
    def create_meal_plan(self, meal_plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создает план питания"""
        return self._make_request('POST', 'meal-plan/', json=meal_plan_data)

    @allure.step("Получить план питания по ID = {meal_plan_id}")
    def get_meal_plan_id(self, meal_plan_id: int) -> Dict[str, Any]:
        """Получает план питания"""
        return self._make_request('GET', f'meal-plan/{meal_plan_id}/')

    @allure.step("Получить список планов питания")
    def get_all_meal_plans(self)-> Dict[str, Any]:
        """Получает список планов питания"""
        return self._make_request('GET', 'meal-plan/')

    @allure.step("Удалить план питания по ID = {plan_id}")
    def delete_meal_plan(self, plan_id: int) -> bool:
        """Удаляет план питания"""
        response = self._make_request('DELETE', f'meal-plan/{plan_id}/')
        if response is None:
            return False
            # response — это словарь, содержащий 'status_code'
        return response.get('status_code') == 204

# === МЕТОДЫ ДЛЯ СПИСКА ПОКУПОК ===

    @allure.step("Получить список покупок, связанных с рецептами")
    def get_shopping_list_recipe(self) -> Dict:
        """Получает список покупок, связанных с рецептами"""
        return self._make_request('GET', 'shopping-list-recipe/')

    @allure.step("Получить список покупок, НЕ связанных с рецептами")
    def get_shopping_list_entry(self) -> Dict[str, Any]:
        """Получает список покупок, НЕ связанных с рецептами"""
        return self._make_request('GET', 'shopping-list-entry/')

    @allure.step("Добавить продукты в список покупок, связанных с рецептами")
    def create_shopping_list_entry(self, entries_for_shopping_list: Dict[str, Any]) -> Dict[str, Any]:
        """Добавляет данные в список покупок без привязки к рецепту"""
        return self._make_request('POST', 'shopping-list-entry/', json=entries_for_shopping_list)

    @allure.step("Удалить продукты НЕ связанные с рецептами "
                 "из списока покупок по ID = {shopping_list_id}")
    def delete_shopping_list(self, shopping_list_id: int)-> Dict[str, Any]:
        """Удаляет данные из списка покупок по ID.
        Удаление позиции не связанных с рецепом"""
        return self._make_request('DELETE', f'shopping-list-entry/{shopping_list_id}/')

    @allure.step("Удалить продукты связанные с рецептами "
                 "из списока покупок по ID = {shopping_list_id}")
    def delete_shopping_list_rec(self, shopping_list_id)-> Dict[str, Any]:
        """Удаляет данные из списка покупок по ID.
        Удаление позиции связанных с рецепом"""
        return self._make_request('DELETE', f'shopping-list/{shopping_list_id}/')

# === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===

    @allure.step("Проверить, что план удален по ID = {plan_id}")
    def verify_plan_deleted(self, plan_id: int) -> bool:
        """Проверяет, что план удален по ID"""
        response = self._make_request('GET', f'meal-plan/{plan_id}/')
        if response and response.get('status_code') == 404:
            return True
        return False


    @allure.step("Сохраняет рецепт в базу данных Tandoor")
    def save_recipe(self, recipe_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Сохраняет рецепт в базу данных Tandoor

        Args:
            recipe_data: Данные рецепта из импорта (json_data['recipe'])

        Returns:
            Ответ API с ID сохраненного рецепта
        """
        try:
            # Передаём recipe_data целиком
            # Он уже содержит все нужные поля в правильном формате

            # Убедимся, что internal = True (чтобы рецепт был виден только мне)
            recipe_data['internal'] = True

            # Отправляем данные
            response = self._make_request('POST', 'recipe/', json=recipe_data)
            return response

        except Exception as e:
            print(f" Ошибка при сохранении рецепта: {e}")
            return None

    @allure.step("Проверка соединения с API.Пытается получить список рецептов.")
    def test_connection(self) -> bool:
        """Проверяет соединение с API."""
        print(" Проверяю соединение API...")

        result = self.get_recipes()
        status_code = result.get('status_code')

        if status_code == 200:
            count = result.get('json', {}).get('count', 0)
            print(f" API Соединение установлено! Рецептов: {count}")
            return True
        else:
            error_msg = "Ошибка сети" if status_code is None else f"Статус: {status_code}"
            print(f"API {error_msg}")
            return False