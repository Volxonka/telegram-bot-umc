#!/usr/bin/env python3
"""
Тест FastAPI сервера
"""

import requests
import time
import sys

def test_fastapi_server():
    """Тестирует FastAPI сервер"""
    print("🧪 Тестирование FastAPI сервера...")
    
    base_url = "http://localhost:8080"
    
    # Ждем запуска сервера
    print("⏳ Ожидание запуска сервера...")
    time.sleep(3)
    
    try:
        # Тест health endpoint
        print("🔍 Проверка health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint работает")
            print(f"   Ответ: {response.json()}")
        else:
            print(f"❌ Health endpoint вернул {response.status_code}")
            return False
        
        # Тест главной страницы
        print("🔍 Проверка главной страницы...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Главная страница загружается")
        else:
            print(f"❌ Главная страница вернула {response.status_code}")
            return False
        
        # Тест API данных
        print("🔍 Проверка API данных...")
        response = requests.get(f"{base_url}/api/data", timeout=5)
        if response.status_code == 200:
            print("✅ API данных работает")
            data = response.json()
            print(f"   Статус: {data.get('status')}")
        else:
            print(f"❌ API данных вернул {response.status_code}")
            return False
        
        # Тест Context7 info
        print("🔍 Проверка Context7 info...")
        response = requests.get(f"{base_url}/api/context7/info", timeout=5)
        if response.status_code == 200:
            print("✅ Context7 info работает")
            info = response.json()
            print(f"   Оптимизации: {len(info.get('context7_optimizations', {}))}")
        else:
            print(f"❌ Context7 info вернул {response.status_code}")
            return False
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print(f"🌐 Веб-приложение доступно: {base_url}")
        print(f"📚 API документация: {base_url}/api/docs")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу")
        print("   Убедитесь, что FastAPI сервер запущен")
        return False
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("🚀 Тест FastAPI сервера для веб-приложения УМЦ")
    print("=" * 50)
    
    success = test_fastapi_server()
    
    if success:
        print("\n📋 Следующие шаги:")
        print("1. 🤖 Запустите бота: python bot.py")
        print("2. 📱 Протестируйте в Telegram")
        print("3. 🌐 Откройте веб-приложение в браузере")
    else:
        print("\n❌ Тесты не пройдены!")
        print("Проверьте, что FastAPI сервер запущен")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
