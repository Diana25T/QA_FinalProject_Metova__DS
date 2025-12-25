import time

import pytest

from pages import LoginPage

@pytest.mark.api
def test_success_login(driver):
  """Тест логина """
  page = LoginPage(driver)
  page.login_user()
  time.sleep(2)
  assert page.is_login_successful(), "Логин не выполнен"
print("Логин прошел успешно")
