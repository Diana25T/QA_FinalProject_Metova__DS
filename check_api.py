print("=== ПРОВЕРКА API КЛИЕНТА ===")

try:
    # Импортируем наш класс
    from api.client import TandoorAPIClient

    # Создаем клиент
    client = TandoorAPIClient()
    print(" Клиент создан")

    # Проверяем соединение
    if client.test_connection():
        print(" ВСЁ РАБОТАЕТ!")
    else:
        print(" ЕСТЬ ПРОБЛЕМЫ")

except ImportError:
    print(" Не найден файл api/client.py")
except Exception as e:
    print(f" Ошибка: {e}")