import time
from typing import Tuple, Any, Optional

import allure
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages import BasePage


class MealPlanPage(BasePage):
    """
       Page Object для работы со страницей планов питания.
       Содержит методы для создания, просмотра и удаления планов питания.
       """

    # === ЛОКАТОРЫ ЭЛЕМЕНТОВ СТРАНИЦЫ ===

    # Карточки и форма
    CARD_EVENTS = (By.CSS_SELECTOR, ".card.cv-item")
    PLAN_FORM = (By.XPATH,
                 "//span[@class='v-btn__content' and contains(., 'Планирование')]")
    CREATE_BUTTON = (By.CSS_SELECTOR,
                     "div.cv-day.future.hasItems[aria-label='12']")

    # Поля формы
    RECIPE_INPUT = (By.XPATH,
                    '//input[@class="multiselect-search" and @aria-placeholder="Рецепт"]')
    ADD_SHOPPING_LIST_CHECKBOX = (By.CSS_SELECTOR,
                                  "input[type='checkbox'][aria-label='Добавить в лист покупок']")
    TITLE_INPUT = (By.CSS_SELECTOR, "input[id^='input-v-'][id$='-5']")
    MEAL_TYPE_INPUT = (By.CSS_SELECTOR,
                       'input.multiselect-search[aria-placeholder="Тип питания"]')
    SERVINGS_INPUT = (By.CSS_SELECTOR,
                      'input.v-field__input[type="text"][inputmode="decimal"]')
    USER_SEARCH_INPUT = (By.CSS_SELECTOR,
                         'input.multiselect-tags-search[aria-placeholder="Пользователь"]')

    # Кнопки
    SAVE_BUTTON = (By.XPATH,
                   '//span[@class="v-btn__content" and text()="Создать"]')
    SAVE_BUTTON_2 = (By.XPATH,
                     '//span[@class="v-btn__content" and @data-no-activator="" and text()="Сохранить"]')
    DELETE_BUTTON = (By.XPATH,
                     "//span[contains(@class, 'v-btn__content') and normalize-space()='Удалить']")

    # Планы на странице
    PLAN_CARD = (By.XPATH,
                 "//div[contains(@class, 'cv-item') and contains(@class, 'card')]")
    PLAN_RECIPE_NAME = (By.XPATH,
                        ".//span[contains(@class, 'one-line-text')]")

    # Модальное окно удаления
    DELETE_BUTTON_MODAL = (By.XPATH,
                           '//span[@class="v-btn__content" and text()="Удалить"]')
    REPEAL_BUTTON_MODAL = (By.XPATH,
                           '//span[@class="v-btn__content" and text()="Отменить"]')

    # === ИНИЦИАЛИЗАЦИЯ ===

    def __init__(self, driver):
        """ Инициализация страницы планов питания."""
        super().__init__(driver)
        self.page_url = f"{self.base_url}/mealplan"

    # ===НАВИГАЦИЯ===

    @allure.step("Открыть страницу плана по ссылке")
    def open_meal_plan_page(self)-> 'MealPlanPage':
        """Открыцвает по ссылке страницу плана"""
        self.open_url(self.page_url)
        return self

    @allure.step("Получить локатор карточки плана по названию: '{plan_name}'")
    def get_plan_card_locator_by_name(self, plan_name: str) -> Tuple[str, str]:
        """Получает локатор для всей карточки плана по названию"""
        # Находим карточку по тексту внутри неё
        return (By.XPATH,
                f"//div[contains(@class, 'cv-item') and .//span[contains(@class, 'one-line-text') and contains(text(), '{plan_name}')]]")

    # === РАБОТА С ДАТАМИ ===

    @allure.step("Получить локатор дня по дню: {day_number}")
    def get_day_locator_by_number(self, day_number: int) -> Tuple[str, str]:
        """Находит и кликает на день в календаре"""
        locator = (By.CSS_SELECTOR, f"div.cv-day[aria-label='{day_number}']")
        time.sleep(2)  # Даем время на загрузку календаря
        self.click(locator)
        print(f"Кликнули на день {day_number}")
        return locator

    @allure.step("Выбрать дату с числом: {day_number}")
    def click_date_by_number(self, day_number: int) -> None:
        """Кликает на кнопку даты с указанным числом"""
        # Преобразуем в строку если передали число
        day_str = str(day_number)

        locator = (By.XPATH,
                   f'//span[@class="v-btn__content" and text()="{day_str}"]/ancestor::button[contains(@class, "v-date-picker-month__day-btn")]')

        self.find_element(locator).click()
        print(f" Выбрана дата: {day_str}")

    @allure.step("Получить форму плана питания")
    def get_plan_form(self)-> WebElement:
        """Получает форму плана питания после выбора дня"""
        return self.wait.until(EC.visibility_of_element_located(self.PLAN_FORM))

    # === РАБОТА С ФОРМОЙ ===

    @allure.step("Ввести заголовок: {title}")
    def enter_title(self, title: str) -> None:
        """Вводит заголовок в соответствующее поле"""
        if not self.is_form_opened():
            raise Exception("Форма не открыта. Нельзя вводить заголовок.")

        self.input_text(self.TITLE_INPUT, title)
        print(f"Введен заголовок: {title}")

    @allure.step("Ввести рецепт: {recipe_name}")
    def enter_recipe(self, recipe_name: str) -> None:
        """Вводит название рецепта в соответствующее поле"""
        if not self.is_form_opened():
            raise Exception("Форма не открыта. Нельзя вводить рецепт.")

        self.input_text(self.RECIPE_INPUT, recipe_name)
        print(f"Введен рецепт: {recipe_name}")

    def choose_recipe(self, text: str) -> None:
        """Кликает на элемент выпадающего списка рецептов"""
        locator = (By.XPATH, f"//span[text()='{text}']")
        self.click(locator)
        print(f"Выбран рецепт из выпадающего списка: {text}")

    @allure.step("Ввести тип питания: {meal_type}")
    def enter_meal_type(self, meal_type: str) -> None:
        """Вводит тип плана питания в соответствующее поле и нажимает Enter"""
        if not self.is_form_opened():
            raise Exception("Форма не открыта. Нельзя вводить тип питания.")

        try:
            # Используем существующий метод input_text для ввода
            self.input_text(self.MEAL_TYPE_INPUT, meal_type)
            print(f"Введен тип питания: {meal_type}")

            # Находим элемент еще раз для нажатия Enter
            element = self.find_element(self.MEAL_TYPE_INPUT)

            # Ждем немного для появления автодополнения (если есть)
            time.sleep(1)

            # Нажимаем Enter
            element.send_keys(Keys.RETURN)
            print("Нажата клавиша Enter после ввода типа питания")

            # Даем время на обработку
            time.sleep(1)

        except Exception as e:
            print(f"Ошибка при вводе типа питания: {e}")

    @allure.step("Ввести количество порций: {servings}")
    def enter_servings(self, servings: str) -> None:
        """Вводит количество порций в соответствующее поле"""
        if not self.is_form_opened():
            raise Exception("Форма не открыта. Нельзя вводить количество порции.")

        try:
            self.input_text(self.SERVINGS_INPUT, servings)
            print(f"Введено количество порции: {servings}")
            # Находим элемент еще раз для нажатия Enter
            element = self.find_element(self.SERVINGS_INPUT)

            # Ждем немного
            time.sleep(1)

            # Нажимаем TAB
            element.send_keys(Keys.TAB)
            print("Нажата клавиша TAB после ввода количества порции")

            time.sleep(1)

        except Exception as e:
            print(f"Ошибка при ввода количества порции: {e}")

    # === РАБОТА С ПЛАНАМИ ===

    @allure.step("Создать план питания")
    def create_plan_ui(self,
                      day_number: int,
                      recipe_name: str,
                      title: str,
                      meal_type: str,
                      servings: str) -> bool:
        """Создает план через UI и возвращает результат"""
        try:
            self.open_meal_plan_page()
            allure.attach(
                f"Создание плана с параметрами:\n"
                f"- День: {day_number}\n"
                f"- Рецепт: {recipe_name}\n"
                f"- Заголовок: {title}\n"
                f"- Тип питания: {meal_type}\n"
                f"- Порций: {servings}",
                name="plan_parameters",
                attachment_type=allure.attachment_type.TEXT
            )
            self.get_day_locator_by_number(day_number)
            time.sleep(2)

            if not self.is_form_opened():
                print("Форма не открылась автоматически. Пробуем еще раз...")
                time.sleep(1)
                self.get_day_locator_by_number(day_number)
                time.sleep(1)

            # Заполняем форму
            self.enter_recipe(recipe_name)
            self.choose_recipe(text=recipe_name)
            self.click(self.ADD_SHOPPING_LIST_CHECKBOX)
            time.sleep(0.5)
            self.enter_title(title)
            self.enter_meal_type(meal_type)
            time.sleep(0.5)
            self.enter_servings(servings)

            # Сохраняем
            self.click(self.SAVE_BUTTON)
            time.sleep(0.5)
            self.click(self.SAVE_BUTTON_2)

            # Проверяем результат
            if self.is_plan_visible(recipe_name, timeout=5):
                allure.attach(
                    f"План '{recipe_name}' успешно создан",
                    name="plan_created",
                    attachment_type=allure.attachment_type.TEXT
                )
                print(f"План '{recipe_name}' успешно создан и отображается")
                return True
            else:
                allure.attach(
                    f"План '{recipe_name}' не найден после создания",
                    name="plan_not_found",
                    attachment_type=allure.attachment_type.TEXT
                )
                print(f"План '{recipe_name}' не найден после создания")
                return False

        except Exception as e:
            allure.attach(
                f"Ошибка при создании плана: {str(e)}",
                name="create_plan_error",
                attachment_type=allure.attachment_type.TEXT
            )
            return False
            print(f"Ошибка при создании плана: {e}")
            return False

    @allure.step("Удалить первый найденный план по названию '{plan_name}'")
    def delete_plan_by_name(self, plan_name: str) -> bool:
        """Удаляет план питания по названию и возвращает результат"""
        try:
            self.open_meal_plan_page()

            if not self.is_plan_visible(plan_name):
                allure.attach(
                    f"План '{plan_name}' не найден для удаления",
                    name="plan_not_found_for_delete",
                    attachment_type=allure.attachment_type.TEXT
                )
                print(f"План '{plan_name}' не найден на странице.")
                return False

            locator = self.get_plan_card_locator_by_name(plan_name)
            self.click(locator)

            if not self.is_form_opened():
                print("Пробуем еще раз открыть форму...")
                time.sleep(2)
                self.click(locator)
                time.sleep(1)

            self.click(self.DELETE_BUTTON)
            time.sleep(1)
            print(f"Удаляем план: '{plan_name}'")
            self.click(self.DELETE_BUTTON_MODAL)

            # Проверяем результат
            if self.is_plan_invisibility(plan_name):
                allure.attach(
                    f"План '{plan_name}' успешно удален",
                    name="plan_deleted",
                    attachment_type=allure.attachment_type.TEXT
                )
                print(f"План: '{plan_name}' удален")
                return True
            else:
                allure.attach(
                    f"План '{plan_name}' не удален (все еще виден)",
                    name="delete_failed",
                    attachment_type=allure.attachment_type.TEXT
                )
                print(f"План: '{plan_name}' не удален.")
                return False

        except Exception as e:
            allure.attach(
                f"Ошибка при удалении плана '{plan_name}': {str(e)}",
                name="delete_error",
                attachment_type=allure.attachment_type.TEXT
            )
            print(f"Ошибка при удалении плана: {e}")
            return False

    @allure.step("Удалить все планы c названием '{plan_name}'")
    def delete_all_plans_with_name(self,
                                  plan_name: str,
                                  timeout: Optional[int] = None) -> None:
        """Находит и удаляет все существующие планы по названию"""
        # Локатор карточки плана по названию
        if timeout is None:
            timeout = self.timeout
        locator = self.get_plan_card_locator_by_name(plan_name)
        plans = self.driver.find_elements(*locator)
        for plan in plans:
            plan.click()
            if not self.is_form_opened():
                # попробуйте повторно
                self.wait.until(EC.element_to_be_clickable(locator))

                plan.click()
            # подтверждение удаления
            self.click(self.DELETE_BUTTON)
            self.click(self.DELETE_BUTTON_MODAL)
            # ждать исчезновения
            WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))
            print(f"Удален план: {plan_name}")


    # ===ПРОВЕРКИ===

    def is_plan_visible(self, plan_name: str, timeout: Optional[int] = None) -> bool:
        """Проверка видимости плана с настраиваемым таймаутом"""
        plan_locator = self.get_plan_card_locator_by_name(plan_name)
        is_visible = self.is_element_visible(plan_locator, timeout)

        if is_visible:
            print(f"План '{plan_name}' найден и видим")
        else:
            print(f"План '{plan_name}' не найден за таймаут")

        return is_visible

    @allure.step("Проверить невидимость плана: {plan_name}")
    def is_plan_invisibility(self,
                           plan_name: str,
                           timeout: Optional[int] = None) -> bool:
        """Проверяет, что план исчез со страницы"""
        if timeout is None:
            timeout = self.timeout
        plan_locator = self.get_plan_card_locator_by_name(plan_name)
        is_invisible = self.is_element_invisible(plan_locator, timeout)

        if is_invisible:
            print(f"План '{plan_name}' не видим (удален/скрыт)")
        else:
            print(f"План '{plan_name}' все еще видим за таймаут")

        return is_invisible

    @allure.step("Проверить, что форма открыта")
    def is_form_opened(self) -> bool:
        """Проверяет, открыта ли форма плана питания"""
        return self.is_element_visible(self.PLAN_FORM)

    # ===ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ===

    def verify_plan_deleted_via_api(self,
                                  plan_name: str,
                                  api_client: Any) -> bool:
        """Проверяет через API что план удален """
        response = api_client.get_all_meal_plans()

        if isinstance(response, dict):
            if response.get('status_code') == 200:
                # Получаем список рецептов из ключа 'results'
                recipe_data = response.get('json', {})
                recipe_list = recipe_data.get('results', [])

                if recipe_list:
                    for recipe in recipe_list:
                        # Проверяем название рецепта
                        if recipe.get('name') == plan_name:
                            # Рецепт найден - удаление не сработало
                            return False
                # Если список пуст или рецепт не найден
                return True

        # В случае ошибки возвращаем False
        return False
