from typing import Tuple, List, Optional

import allure
from selenium.webdriver.common.by import By

from pages import BasePage


class ShoppingListPage(BasePage):
    # ЛОКАТОРЫ ДЛЯ СПИСКА ПОКУПОК
    SHOPPING_LIST_LINK = (By.XPATH, "//a[@href='/shopping']")  # кнопка "Список покупок"
    PRODUCT_UNIT = (By.XPATH, ".//b//span[contains(@class, 'ms-1')]")  # единица измерения продукта
    PRODUCT_QUANTITY = (By.XPATH, ".//b//span[1]")  # количество продукта
    GROUP_LIST = ".v-list.v-theme--light"  # основной контейнер списка

    # ИНФОРМАЦИЯ О ТОВАРЕ В СПИСКЕ ПОКУПОК
    ITEM_NAME = ".d-flex.flex-column.flex-grow-1.align-self-center"
    RECIPE_INFO = "small.text-disabled"  # для получения информации о рецепте, сюда не входит название самого продукта
    ITEM_FULL_TEXT = (By.CSS_SELECTOR,
                      ".d-flex.flex-column.flex-grow-1.align-self-center")  # вся информация о продукте без количества продуктов(гр и т.д)
    CHECK_BOX = (By.CSS_SELECTOR,
                 "button.v-btn[type='button'].text-success.btn-success")  # для кнопки с галочкой (чек-кнопка)

    # ЛОКАТОРЫ ФИЛЬТРА
    SLIDERS_ICON = "i.fa-solid.fa-sliders"  # кнопка фильтра в шапке
    FILTER = (By.XPATH,
              "//label[contains(., 'Сгруппировать по')]/..")  # это dropdown/select поле для группировки с выбранным значением "Рецепт"
    CARET_XPATH = "//i[contains(@class, 'fa-caret-down')]"  # кнопка вниз для выпадающего списка
    GROUP_HEADER = ".v-list-subheader__text"  # заголовок группы
    GROUP_ITEMS = ".v-list-item.v-list-item--link"

    # ЛОКАТОРЫ ДЛЯ ТОВАРОВ( РЕДАКТИРОВАНИЕ, ИЗМЕНЕНИЕ, УДАЛЕНИЕ ВНУТРИ КАРТОЧКИ ТОВАРА И.Т.Д.)
    EDITING_BUTTON = (By.XPATH,
                      "//i[@class='fa-solid fa-carrot fa-2x mb-2']")  # кнопка "Редактирование" после клика на продукт
    DESCRIPTION_PRODUCT_BUTTON = (By.CSS_SELECTOR,
                                  "textarea.v-field__input[rows='5']")  # кнопка описания при редактировании карточки товара конкретного
    SAVE_BUTTON = (By.XPATH,
                   "//span[@class='v-btn__content' and @data-no-activator='' and text()='Сохранить']")  # кнопка "Сохранить" после редактирования внутри карточки товара"
    VIEWING_THE_RECORDING_ICON = (By.CSS_SELECTOR,
                                  "a.bg-edit")  # это кнопка с иконкой книги (book) ведущая на рецепт (тоесть, после клика на сам продукт появится значок )
    DELETE_ICON = (By.XPATH,
                   "//button[contains(@class, 'bg-delete')]")  # кнопка удаление конкретного продукта через описание продукта(тоесть, после клика на сам продукт появится значок удаления)

    # ЛОКАТОРЫ, КОТОРЫЕ ПОЯВЛЯЮТСЯ ПОСЛЕ НАЖАТИЯ КНОПКИ РЕДАКТИРОВАНИЯ ВНУТРИ КАРТОЧКИ ПРОДУКТА
    FOOD_BUTTON = (By.XPATH,
                   "//button[contains(@class, 'v-tab') and .//span[text()='Еда']]")  # кнопка "Еда" внутри карточки
    PROPERTIES_INPUT = (By.XPATH,
                        "//span[@data-no-activator='' and text()='Свойства' and ./div[@class='v-tab__slider']]")  # строка для ввода текста  внутри карточки товара
    TRANSFORMATION_BUTTON = (By.XPATH,
                             "//span[text()='Преобразование' and ./div[@class='v-tab__slider']]")  # кнопка "Преобразование" внутри карточки товара
    BACK_BUTTON = (By.XPATH,
                   "//button[.//i[contains(@class, 'fa-arrow-left')] and .//span[text()='Назад']]")  # кнопка "Назад" внутри карточки товара
    DIFFERENT_BUTTON = (By.XPATH,
                        "//span[text()='Разное' and ./div[@class='v-tab__slider']]")  # кнопка разное внутри карточки

    def __init__(self, driver):
        super().__init__(driver)
        self.page_url = f"{self.base_url}/shopping"

    #===НАВИГАЦИЯ===

    @allure.step("Открыть по ссылке страницу плана")
    def open_shopping_list_page(self) -> 'ShoppingListPage':
        """Открывает по ссылке страницу плана"""
        self.open_url(self.page_url)
        return self

    @allure.step("Получить локатор(tuple) для элемента списка по названию продукта '{food_name}'")
    def get_food_item_locator(self, food_name: str) -> Tuple[str, str]:
        """Локатор для элемента списка по названию продукта"""
        return (By.XPATH, f"//div[contains(@class, 'v-list-item') and contains(., '{food_name}')]")

    @allure.step("Получить динамический локатор (tuple) для элемента по количеству '{amount}'")
    def get_food_item_by_amount(self, amount: str, unit: str = "г") -> Tuple[str, str]:
        """Локатор для элемента по количеству"""
        return (By.XPATH, f"//div[contains(@class, 'v-list-item') and .//span[contains(., '{amount}{unit}')]]")

    @allure.step("Получить динамический локатор (tuple) для получения продуктов,"
                 " относящихся к рецепту '{recipe_name}' ")
    def get_recipe_item_locator(self, recipe_name: str) -> Tuple[str, str]:
        """Локатор для получения информации, к какому рецепту относится продукт"""
        return (By.XPATH, f"//small[contains(@class, 'text-disabled') and contains(text(), '{recipe_name}')]")

    @allure.step("Получить локатор (tuple) для кнопки галочки "
                 "продукта '{food_name}' списка продуктов")
    def get_check_button_for_food(self, food_name: str) -> Tuple[str, str]:
        """Локатор кнопки галочки для конкретного продукта"""
        return (By.XPATH,
                f"//div[contains(@class, 'v-list-item') and contains(., '{food_name}')]//button[.//i[contains(@class, 'fa-check')]]")

    #===МЕТОДЫ ВОЗВРАЩАЮЩИЕ РЕЗУЛЬТАТ ДЛЯ ТЕСТОВ===

    @allure.step("Получить все продукты в списке покупок с информацией о продуктах")
    def get_all_recipes(self) -> List[str]:
        """Получает список всех продуктов в списке покупок"""
        recipes = []

        # find_elements возвращает список элементов
        recipe_elements = self.find_elements(self.ITEM_FULL_TEXT)
        print(f"Найдено элементов : {len(recipe_elements)}")

        for element in recipe_elements:
            recipe_text = element.text.strip()
            if recipe_text:
                recipes.append(recipe_text)
                print(f" Рецепт: {recipe_text}")
        return recipes

    @allure.step("Получить все элементы, содержащие название рецепта: '{recipe_name}'")
    def get_all_the_elements_related_recipe(self, recipe_name: str) -> List[str]:
        """Возвращает все элементы, содержащие название рецепта, и логирует результат"""
        recipes = self.get_all_recipes()
        search_term = recipe_name.split()[0]
        related_items = [text for text in recipes if search_term in text]
        print(f"Найдено {len(related_items)} элементов, связанных с рецептом '{recipe_name}':")
        for item in related_items:
            print(f"  - {item}")
        return related_items

    @allure.step("Отметить продукт '{food_name}' как купленный")
    def check_product(self, food_name: str) -> None:
        """Отмечает продукт как купленный (кликает на чекбокс)."""
        check_button = self.get_check_button_for_food(food_name)
        self.click(check_button)
        print(f"Продукт '{food_name}' отмечен как купленный")

    @allure.step("Удалить продукт '{food_name}' из списка")
    def delete_product(self, food_name: str) -> bool:
        """Удаляет продукт из списка покупок."""
        try:
            item_locator = self.get_food_item_locator(food_name)
            self.click(item_locator)
            self.click(self.DELETE_ICON)
            print(f"Продукт '{food_name}' удален")
            return True
        except Exception as e:
            print(f"Ошибка при удалении продукта '{food_name}': {e}")
            return False

    #===ПРОВЕРКИ===

    @allure.step("Проверить видимость продукта '{food_name}' в листе покупок")
    def is_product_visible(
            self,
            food_name: str,
            timeout: Optional[int] = None
    ) -> bool:
        """Проверка видимости товаров в листе покупок с настраиваемым таймаутом"""
        item = self.get_food_item_locator(food_name)
        visible = self.is_element_visible(item, timeout)
        if visible:
            print(f"Продукт '{food_name}' найден и видим")
            return True
        else:
            print(f" Продукт '{food_name}' не найден за {timeout} секунд")
        return visible

    @allure.step("Проверить, есть ли в списке покупок продукты,"
                 " связанные с рецептом '{recipe_name}'(частичное совпадение)")
    def is_recipe_in_shopping_list(
            self,
            recipe_name: str,
            timeout: Optional[int] = None
    ) -> bool:
        """Проверяет, есть ли рецепт в списке покупок (частичное совпадение)"""
        recipes = self.get_all_recipes()
        # Берем первое слово из названия рецепта для поиска
        search_term = recipe_name.split()[0]

        for recipe_text in recipes:
            if search_term in recipe_text:
                return True
        return False
