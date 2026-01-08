import json
import os

from dotenv import load_dotenv

from api.client import TandoorAPIClient

load_dotenv()

def main():
    with open('recipes_links.json', 'r') as f:
        data = json.load(f)

    links = data['recipes']
    client = TandoorAPIClient(os.getenv('BASE_URL'), os.getenv('TANDOOR_TOKEN'))

    # Получаем ID рецептов
    imported_recipes = []
    for link in links:
        recipe = client.import_recipe_from_url(link)
        if recipe:
            imported_recipes.append(recipe['id'])
            print(f'Импортирован рецепт: {link} — ID: {recipe["id"]}')
        else:
            print(f'Ошибка импорта рецепта: {link}')

    # Сохраняем ID в файл для использования
    with open('imported_recipes.json', 'w') as f:
        json.dump({"recipe_ids": imported_recipes}, f)

if __name__ == "__main__":
    main()
