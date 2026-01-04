import time

import allure
import pytest

from pages import LoginPage


@pytest.mark.api
@allure.title("Успешная авторизация пользователя через UI")
@allure.severity(allure.severity_level.CRITICAL)
def test_success_login(driver):
  """Тест логина """
  page = LoginPage(driver)
  page.login_user()
  time.sleep(2)
  assert page.is_login_successful(), "Логин не выполнен"
print("Логин прошел успешно")
