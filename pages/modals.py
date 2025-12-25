from selenium.webdriver.common.by import By

#Локаторы для формы заполнения плана питания
RECIPE_SEARCH_INPUT = (By.CSS_SELECTOR, "input.multiselect-search[aria-placeholder='Рецепт']")
HEADING_INPUT = (By.ID, "input#input-v-18-5")
DATE_BUTTON_PLUS = (By.CSS_SELECTOR, "button i.fa-solid.fa-plus")
DATE_BUTTON_MINUS = (By.CSS_SELECTOR, "button i.fa-solid.fa-minus")
MEAL_TYPE_INPUT = (By.CSS_SELECTOR, "[aria-placeholder='Тип питания'][role='combobox']")
PORTIONS_BUTTON_PLUS = (By.CSS_SELECTOR, "button[data-testid='increment']")
PORTIONS_BUTTON_MINUS = (By.CSS_SELECTOR, "button[data-testid='decrement']")
USER_SEARCH_INPUT = (By.CSS_SELECTOR, "input.multiselect-tags-search[aria-placeholder='Пользователь']")
RECIPE_SPAN = (By.XPATH, "//span[text()='Карамельный пудинг']")
SHOPPING_LIST_CHECKBOX_LABEL = (By.XPATH, "//label[text()='Добавить в лист покупок']")
ADMIN_USER_BY_ID = (By.ID, "multiselect-option-1")
CREATE_BUTTON = (By.CSS_SELECTOR, "span.v-btn__content:has-text('Создать')")
DELETE_PLAN_BUTTON = (By.xpath("//span[text()='Удалить']"))
SAVE_BUTTON = (By.xpath("//span[text()='Сохранить']"))
RECIPE_ICON_BY_NAME = (By.XPATH, "//span[contains(text(),'Сырники из творога')]")


def get_date_locator(full_date):
   """Локатор по полной дате в формате YYYY-MM-DD"""
   return (By.CSS_SELECTOR, f"div.cv-day.d{full_date}")






