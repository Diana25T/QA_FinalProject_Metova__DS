import time
from typing import Optional

import allure
from selenium.webdriver.common.by import By

from .base_page import BasePage


class HeaderComponent(BasePage):
    """Компонент панели навигации (наследует BasePage)"""

    # Локаторы компонентов header
    MEAL_PLAN_LINK = (By.CSS_SELECTOR, "i.fa-calendar-alt")  # Кнопка "Список покупок"
    SHOPPING_LIST_LINK = (By.XPATH, "//a[@href='/shopping']")  # Кнопка "Список покупок"
    USER_MENU = (By.CSS_SELECTOR, "i.fa-bars")  # Кнопка меню пользователя
    USERNAME_DISPLAY = (By.CSS_SELECTOR, ".v-avatar.bg-primary.cursor-pointer")  # Отображение имени пользователя
    LOGIN_BUTTON = (By.CLASS_NAME, ".btn btn-success")  # Кнопка "Войти"
    LOGOUT_BUTTON = (By.XPATH, "//div[text() = 'Выйти']")  # Кнопка "Выйти"

    # ===НАВИГАЦИЯ===

    @allure.step("Перейти к разделу планов питания")
    def go_to_meal_plan(self):
        """ Переход к разделу планов питания"""
        self.click(self.MEAL_PLAN_LINK)
        print("Перешли к планам питания")
        time.sleep(2)

    @allure.step("Перейти к списку покупок")
    def go_to_shopping_list(self):
        """ Переход к списку покупок"""
        self.click(self.SHOPPING_LIST_LINK)  # Кликаем на кнопку
        print("Вы перешли к списку покупок")
        time.sleep(2)

    @allure.step("Открыть меню пользователя")
    def go_to_user_menu(self):
        """ Переход в меню пользователя"""
        self.click(self.USER_MENU)
        print("Вы перешли в меню пользователя")
        time.sleep(2)

    # ===ПРОВЕРКИ===

    @allure.step("Проверить авторизацию пользователя")
    def is_user_logged_in(self) -> bool:
        """Проверяет, авторизован ли пользователь."""
        # Вариант 1: Проверяем по наличию кнопки входа
        if self.is_element_visible(self.LOGIN_BUTTON, timeout=3):
            allure.attach("Пользователь не авторизован (видна кнопка входа)",
                          name="Результат проверки",
                          attachment_type=allure.attachment_type.TEXT)
            return False  # не авторизован

        # Вариант 2: Проверяем по наличию имени пользователя
        if self.is_element_visible(self.USERNAME_DISPLAY, timeout=3):
            allure.attach("Пользователь авторизован (видно имя)",
                          name="Результат проверки",
                          attachment_type=allure.attachment_type.TEXT)
            return True  # авторизован

        allure.attach("Не удалось определить статус авторизации",
                      name="Результат проверки",
                      attachment_type=allure.attachment_type.TEXT)
        return False  # не удалось определить

    # ===ПОЛУЧЕНИЕ ДАННЫХ===

    @allure.step("Получить имя пользователя")
    def get_username(self) -> Optional[str]:
        """Получает имя авторизованного пользователя.
        Возвращает None если пользователь не авторизован."""
        if self.is_element_visible(self.USERNAME_DISPLAY, timeout=3):
            return self.get_text(self.USERNAME_DISPLAY)
        return None

    # ===ДЕЙСТВИЯ===

    @allure.step("Выйти из системы")
    def logout(self) -> None:
        """Выход из системы"""
        self.go_to_user_menu()
        time.sleep(1)
        self.click(self.LOGOUT_BUTTON)
        print("Вышли из системы")
        time.sleep(2)
