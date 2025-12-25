from datetime import datetime

import pytest

from tests.conftest import temporary_meal_plan_for_ui, clean_test_plan_ui

#===ТЕСТИРОВАНИЕ UI ПЛАНА ПИТАНИЯ===

@pytest.mark.api
def test_create_plan_with_fixture(meal_plan_page, clean_test_plan_ui):
    """Проверка корректности создания плана через UI
    Фикстура очищает данные до и после теста"""

    # получает название плана "Крем Рафаэлло" из фикстуры.
    # Чтобы не дублировать планы recipe_name должен быть равен plan_name

    plan_name = clean_test_plan_ui

    created = meal_plan_page.create_plan_ui(
        day_number=datetime.today().day,
        recipe_name="Крем Рафаэлло",
        title='Завтрак на понедельник',
        meal_type='Завтрак',
        servings='3'
    )
    assert created, 'План не был создан'

    # Проверяем, что план отображается
    assert meal_plan_page.is_plan_visible(plan_name), \
        f"План '{plan_name}' не отображается после создания"

    print(f"Тест пройден: план '{plan_name}' создан и отображается")

@pytest.mark.api
def test_delete_plan(api_client, meal_plan_page, temporary_meal_plan_for_ui):
    """Проверяет корректность удаления через UI c подтверждением через API"""
    # Предварительная подготовка: план создается фикстурой
    meal_plan_page.open_meal_plan_page()
    plan_name = temporary_meal_plan_for_ui

    # вызываем метод удаления
    success = meal_plan_page.delete_plan_by_name(plan_name)
    assert success, "Удаление плана не удалось"

    # Проверяем через API, что план исчез
    response = meal_plan_page.verify_plan_deleted_via_api(plan_name, api_client)
    assert response, "План не удален. Проверка API не прошла"

    # Проверка через UI, что план исчез
    assert meal_plan_page.is_plan_invisibility(plan_name), f"План'{plan_name}' отображается после удаления в тесте"

#===ТЕСТИРОВАНИЕ UI СПИСКА ПОКУПОК===

@pytest.mark.ui
def test_product_added_in_shopping_list(meal_plan_page, shopping_list_page, temporary_meal_plan_for_ui):
    """Фикстура, если нужно, создает и обязательно удаляет план. Тест проверяет автоматическую
     интеграцию продукта в список покупок(корзина) после создания плана с отметкой чек-бокса"""

    # Фикстура возвращает название плана, которое совпадает с названием рецепта.

    plan_name = temporary_meal_plan_for_ui
    assert meal_plan_page.is_plan_visible, f"План '{plan_name}' не создан фикстурой"

    shopping_list_page.open_shopping_list_page()

    # Получаем все элементы, связанные с рецептом
    print(f"Получаем все элементы, связанные с рецептом'{plan_name}' после создания плана")
    related_items = shopping_list_page.get_all_the_elements_related_recipe(recipe_name=plan_name)
    assert len(related_items) > 0, f"Нет элементов, связанных с рецептом '{plan_name}'"
    assert shopping_list_page.is_recipe_in_shopping_list(plan_name,
                                                         timeout=5), f" В списке отсутстуют продукты связанных с рецептом '{plan_name}'"

    meal_plan_page.open_meal_plan_page()

    # Удаляем план для проверки удаления списка покупок
    print(f"Удаляем в тесте план '{plan_name}' для проверки удаления списка продуктов, связанных с рецептом")
    meal_plan_page.delete_plan_by_name(plan_name)

    if meal_plan_page.is_plan_invisibility(plan_name):
        print(f"План {plan_name} удален, проверяем удаление продуктов, связанных с этим рецептом из списка покупок")

        shopping_list_page.open_shopping_list_page()

        # Получаем все элементы, связанные с рецептом, после удаления плана
        print(f"Получаем все элементы, связанные с рецептом'{plan_name}' после удаления плана")
        related_items = shopping_list_page.get_all_the_elements_related_recipe(recipe_name=plan_name)
        assert len(related_items) == 0, f"Нет элементов, связанных с рецептом '{plan_name}'"
    else:
        f"План '{plan_name}' не удален в тесте. Нельзя проверить удаление продуктов из списка покупок "
