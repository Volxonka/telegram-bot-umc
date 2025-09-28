#!/usr/bin/env python3
"""
Простой тест интеграции бота с веб-приложением
"""

import asyncio
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from webapp_config import get_webapp_url, get_webapp_info

async def test_webapp_button():
    """Тестирует создание кнопки веб-приложения"""
    print("🧪 Тестирование кнопки веб-приложения...")
    
    try:
        # Получаем URL и WebAppInfo
        url = get_webapp_url("main")
        webapp_info = get_webapp_info()
        
        print(f"✅ URL: {url}")
        print(f"✅ WebAppInfo: {type(webapp_info)}")
        
        # Создаем кнопку
        keyboard = [
            [InlineKeyboardButton("🚀 Открыть приложение", web_app=webapp_info)],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        print("✅ Кнопка создана успешно")
        print(f"📱 Кнопка будет открывать: {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def test_bot_imports():
    """Тестирует импорты бота"""
    print("\n🤖 Тестирование импортов бота...")
    
    try:
        # Имитируем импорты из бота
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
        from telegram.ext import Application, CallbackQueryHandler, ContextTypes
        from webapp_config import get_webapp_url, get_webapp_info
        
        print("✅ Все импорты успешны")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_webapp_files():
    """Тестирует наличие файлов веб-приложения"""
    print("\n📁 Тестирование файлов веб-приложения...")
    
    files_to_check = [
        'webapp/enhanced.html',
        'webapp/enhanced-styles.css',
        'webapp/enhanced-app.js',
        'webapp/server.py'
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - не найден")
            all_exist = False
    
    return all_exist

async def main():
    print("🚀 Тест интеграции бота с веб-приложением")
    print("=" * 50)
    
    # Запускаем тесты
    tests = [
        ("Импорты бота", test_bot_imports()),
        ("Файлы веб-приложения", test_webapp_files()),
        ("Кнопка веб-приложения", test_webapp_button())
    ]
    
    results = []
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name:.<30} {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\n📋 Что делать дальше:")
        print("1. 🌐 Настройте хостинг веб-приложения")
        print("2. 🔧 Обновите WEBAPP_BASE_URL в webapp_config.py")
        print("3. 🤖 Запустите бота: python bot.py")
        print("4. 📱 Протестируйте в Telegram")
        print("\n💡 Для быстрого тестирования:")
        print("   - Установите ngrok: https://ngrok.com/download")
        print("   - Запустите: ngrok http 8080")
        print("   - Обновите URL в webapp_config.py")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        print("Исправьте ошибки перед продолжением")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
