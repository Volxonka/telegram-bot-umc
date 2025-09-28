#!/usr/bin/env python3
"""
Проверка статуса интеграции бота с веб-приложением
"""

import os
import sys

def check_files():
    """Проверяет наличие всех необходимых файлов"""
    print("📁 Проверка файлов...")
    
    required_files = [
        'bot.py',
        'webapp_config.py',
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

def check_webapp_config():
    """Проверяет конфигурацию веб-приложения"""
    print("\n⚙️ Проверка конфигурации...")
    
    try:
        with open('webapp_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'WEBAPP_BASE_URL = "https://your-domain.com"' in content:
            print("⚠️  URL веб-приложения не настроен (используется по умолчанию)")
            print("   Обновите WEBAPP_BASE_URL в webapp_config.py")
            return False
        else:
            print("✅ URL веб-приложения настроен")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка чтения конфигурации: {e}")
        return False

def check_bot_integration():
    """Проверяет интеграцию в боте"""
    print("\n🤖 Проверка интеграции бота...")
    
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('from webapp_config import', 'Импорт конфигурации'),
            ('handle_webapp', 'Обработчик веб-приложения'),
            ('🚀 Веб-приложение', 'Кнопка веб-приложения'),
            ('get_webapp_info()', 'Создание WebAppInfo')
        ]
        
        all_found = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - не найдено")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Ошибка проверки бота: {e}")
        return False

def check_webapp_server():
    """Проверяет веб-сервер"""
    print("\n🌐 Проверка веб-сервера...")
    
    try:
        with open('webapp/server.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'PORT = int(os.environ.get(\'PORT\', 8080))' in content:
            print("✅ Сервер поддерживает переменную PORT (для хостинга)")
        else:
            print("⚠️  Сервер может не поддерживать хостинг")
        
        if 'Access-Control-Allow-Origin' in content:
            print("✅ CORS заголовки настроены")
        else:
            print("❌ CORS заголовки не настроены")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки сервера: {e}")
        return False

def main():
    print("🔍 Проверка статуса интеграции бота с веб-приложением")
    print("=" * 60)
    
    checks = [
        ("Файлы", check_files),
        ("Конфигурация", check_webapp_config),
        ("Интеграция бота", check_bot_integration),
        ("Веб-сервер", check_webapp_server)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Ошибка в проверке {check_name}: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ ГОТОВО" if result else "⚠️  ТРЕБУЕТ ВНИМАНИЯ"
        print(f"{check_name:.<30} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("\n📋 Следующие шаги:")
        print("1. 🌐 Настройте хостинг веб-приложения")
        print("2. 🔧 Обновите WEBAPP_BASE_URL в webapp_config.py")
        print("3. 🤖 Запустите бота: python bot.py")
        print("4. 📱 Протестируйте в Telegram")
    else:
        print("⚠️  НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ!")
        print("Исправьте проблемы перед продолжением")
    
    print("\n💡 Для подробной инструкции см. NEXT_STEPS.md")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
