import os
import time
from typing import Optional, Tuple

import allure
from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class BasePage:
    """Базовый класс для всех страниц"""

    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        """
              Инициализация базовой страницы.

              Args:
                  driver: WebDriver для управления браузером
                  timeout: Таймаут по умолчанию для ожиданий
              """
        self.driver = driver
        self.timeout = timeout  # Сохраняем timeout как атрибут
        self.wait = WebDriverWait(driver, timeout)
        self.base_url = os.getenv('BASE_URL', 'http://localhost:8080')

    # === НАВИГАЦИЯ ===
    @allure.step("Открыть базовый URL")
    def open_base_page(self) -> 'BasePage':
        """Открывает базовый URL"""
        self.driver.get(self.base_url)
        return self

    @allure.step("Открыть URL: {url}")
    def open_url(self, url: str) -> None:
        """Открывает конкретный URL"""
        self.driver.get(url)

    @allure.step("Обновить страницу")
    def refresh_page(self)-> None:
        """Обновить страницу"""
        self.driver.refresh()
        time.sleep(1)

    # === ПОИСК ЭЛЕМЕНТОВ ===
    @allure.step("Найти элемент: {locator}")
    def find_element(
        self,
        locator: Tuple[str, str],
        timeout: Optional[int] = None
    ) -> WebElement:
        """Найти элемент с ожиданием его появления"""
        wait_timeout = timeout if timeout is not None else self.timeout
        return self.wait.until(EC.presence_of_element_located(locator))

    @allure.step("Найти элементы: {locator}")
    def find_elements(
    self,
    locator: Tuple[str, str],  # ✅ Добавить
    timeout: Optional[int] = None  # ✅ Добавить
) -> list[WebElement]:
        """Находит несколько элементов"""
        wait_timeout = timeout if timeout is not None else self.timeout
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    @allure.step("Кликнуть по элементу: {locator}")
    def click(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> None:
        """Кликнуть по элементу"""
        wait_timeout = timeout if timeout is not None else self.timeout
        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
            element.click()
        except Exception as e:
            print(f"Ошибка при клике на {locator}: {e}")
            raise

    @allure.step("Ввести текст '{text}' в элемент: {locator}")
    def input_text(
        self,
        locator: Tuple[str, str],
        text: str
    ) -> None:
        """Ввод текста в поле с предварительной очисткой"""
        # ждём, что элемент не только есть, но и активен для взаимодействия
        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
            element.clear()
            element.send_keys(text)
        except Exception as e:
            print(f"Ошибка при вводе текста в {locator}: {e}")
            raise

    @allure.step("Получить текст из элемента: {locator}")
    def get_text(self, locator: Tuple[str, str]) -> str:
        """Получает текст из элемента"""
        try:
            element = self.find_element(locator)
            return element.text
        except Exception as e:
            print(f"Ошибка при получении текста из {locator}: {e}")
            raise

    # ===ПРОВЕРКИ===

    @allure.step("Проверить наличие элемента: {locator}")
    def is_element_present(self, locator, timeout=None) -> bool:
        """Проверяет наличие элемента на странице"""
        try:
            wait_timeout = timeout if timeout is not None else self.timeout
            WebDriverWait(self.driver, wait_timeout).until(
                EC.presence_of_element_located(locator)
            )
            allure.attach(
                f"Элемент {str(locator)} присутствует на странице",
                name="element_present",
                attachment_type=allure.attachment_type.TEXT
            )
            return True
        except TimeoutException:
            allure.attach(
                f"Элемент {str(locator)} НЕ найден (таймаут)",
                name="element_not_found",
                attachment_type=allure.attachment_type.TEXT
            )
            return False
        except Exception as e:
            allure.attach(
                f"Ошибка при проверке элемента {str(locator)}: {e}",
                name="element_check_error",
                attachment_type=allure.attachment_type.TEXT
            )
            print(f"Неожиданная ошибка при проверке элемента {locator}: {e}")
            return False

    @allure.step("Проверить видимость элемента: {locator}")
    def is_element_visible(
    self,
    locator: Tuple[str, str],
    timeout: Optional[int] = None
) -> bool:
        """Проверяет видимость элемента (не кидает исключения)"""
        try:
            wait_timeout = timeout if timeout is not None else self.timeout
            allure.attach(
                f"Параметры проверки видимости:\n"
                f"Локатор: {locator}\n"
                f"Таймаут: {wait_timeout}с",
                name="invisibility_check_params",
                attachment_type=allure.attachment_type.TEXT
            )
            WebDriverWait(self.driver, wait_timeout).until(
                EC.visibility_of_element_located(locator)
            )
            allure.attach(
                f"Элемент {str(locator)} видим на странице",
                name="element_visible",
                attachment_type=allure.attachment_type.TEXT
            )
            return True
        except TimeoutException:
            allure.attach(
                f"Элемент {str(locator)} НЕ видим (таймаут)",
                name="element_not_visible",
                attachment_type=allure.attachment_type.TEXT
            )
            return False

    @allure.step("Проверить невидимость элемента: {locator}")
    def is_element_invisible(
    self,
    locator: Tuple[str, str],
    timeout: Optional[int] = None
) -> bool:
        """Проверяет, что элемент невидим (не кидает исключения)"""
        try:
            wait_timeout = timeout if timeout is not None else self.timeout
            allure.attach(
                f"Параметры проверки невидимости:\n"
                f"Локатор: {locator}\n"
                f"Таймаут: {wait_timeout}с",
                name="invisibility_check_params",
                attachment_type=allure.attachment_type.TEXT
            )
            WebDriverWait(self.driver, wait_timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            allure.attach(
                f"Элемент {str(locator)} невидим (как и ожидалось)",
                name="element_invisible",
                attachment_type=allure.attachment_type.TEXT
            )
            return True
        except TimeoutException:
            allure.attach(
                f"Элемент {str(locator)} все еще видим (таймаут)",
                name="element_still_visible",
                attachment_type=allure.attachment_type.TEXT
            )
            return False
