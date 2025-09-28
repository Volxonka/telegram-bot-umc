#!/usr/bin/env python3
"""
Быстрый тест интеграции бота с веб-приложением
"""

import sys
import os

def test_imports():
    """Тестирует импорты"""
    print("🧪 Тестирование импортов...")
    
    try:
        from webapp_config import get_webapp_url, get_webapp_info
        print("✅ webapp_config импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта webapp_config: {e}")
        return False
    
    try:
        from telegram import WebAppInfo
        print("✅ telegram импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта telegram: {e}")
        return False
    
    return True

def test_webapp_config():
    """Тестирует конфигурацию веб-приложения"""
    print("\n🔧 Тестирование конфигурации...")
    
    try:
        from webapp_config import get_webapp_url, get_webapp_info
        
        url = get_webapp_url()
        print(f"✅ URL веб-приложения: {url}")
        
        webapp_info = get_webapp_info()
        print(f"✅ WebAppInfo создан: {type(webapp_info)}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_bot_integration():
    """Тестирует интеграцию с ботом"""
    print("\n🤖 Тестирование интеграции с ботом...")
    
    try:
        # Проверяем, что бот может импортировать конфигурацию
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Имитируем импорт из бота
        from webapp_config import get_webapp_url, get_webapp_info
        from telegram import WebAppInfo
        
        # Тестируем создание кнопки
        webapp_info = get_webapp_info()
        print("✅ WebAppInfo для кнопки создан")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False

def test_webapp_files():
    """Тестирует наличие файлов веб-приложения"""
    print("\n📁 Тестирование файлов веб-приложения...")
    
    required_files = [
        'webapp/enhanced.html',
        'webapp/enhanced-styles.css', 
        'webapp/enhanced-app.js',
        'webapp/server.py',
        'webapp/requirements.txt'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - не найден")
            all_exist = False
    
    return all_exist

def main():
    print("🚀 Быстрый тест интеграции бота с веб-приложением")
    print("=" * 60)
    
    tests = [
        ("Импорты", test_imports),
        ("Конфигурация", test_webapp_config),
        ("Интеграция с ботом", test_bot_integration),
        ("Файлы веб-приложения", test_webapp_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name:.<30} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\n📋 Следующие шаги:")
        print("1. Настройте хостинг веб-приложения")
        print("2. Обновите WEBAPP_BASE_URL в webapp_config.py")
        print("3. Запустите бота: python bot.py")
        print("4. Протестируйте интеграцию")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        print("Исправьте ошибки перед продолжением")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
