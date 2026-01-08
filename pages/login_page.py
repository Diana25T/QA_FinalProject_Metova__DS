import json
import os

import allure
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    """ Страница логина Tandoor"""
    # Локаторы - споcоб поиска элементов на странице
    USERNAME_INPUT = (By.XPATH, "//input[@id='id_login']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#id_password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, 'button.btn.btn-success[type="submit"]')

    def __init__(self, driver):
        super().__init__(driver)
        self.page_url = f"{self.base_url}/accounts/login/?next=/"

    @allure.step("Открыть страницу логина")
    def open_login_page(self) -> 'LoginPage':
        """Открывает страницу логина"""
        self.open_url(self.page_url)
        return self

    @allure.step("Выполнить вход в систему c последующим сохранением cookies")
    def login_user(self) -> None:
        """ Выполняет вход в систему с последующим сохранением cookies """
        self.open_login_page()
        load_dotenv()
        username = os.getenv('TANDOOR_USERNAME')
        password = os.getenv('TANDOOR_PASSWORD')

        if not username or not password:
            raise ValueError("USERNAME или PASSWORD отсутствуют в переменных окружения")

        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

        # После успешного входа сохраняем cookies
        if self.is_login_successful():
            cookies = self.driver.get_cookies()
            with open('cookies.json', 'w', encoding='utf-8') as f:
                json.dump(cookies, f)

    @allure.step("Проверить, успешен ли логин")
    def is_login_successful(self) -> bool:
        """Проверяет, успешен ли логин"""
        try:
            # Ждем появления элемента пользователя
            user_avatar = (By.CSS_SELECTOR, ".v-avatar.cursor-pointer")
            return self.is_element_present(user_avatar)
        except:
            return False
