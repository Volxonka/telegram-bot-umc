#!/usr/bin/env python3
"""
Скрипт для тестирования интеграции веб-приложения с ботом
"""

import subprocess
import time
import requests
import json
import os
from webapp_config import WEBAPP_BASE_URL

def check_ngrok():
    """Проверяет, установлен ли ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def start_webapp_server():
    """Запускает веб-сервер приложения"""
    print("🚀 Запуск веб-сервера...")
    try:
        # Запускаем сервер в фоне
        process = subprocess.Popen(
            ['python', 'server.py'],
            cwd='webapp',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Даем время серверу запуститься
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return None

def get_ngrok_url():
    """Получает URL ngrok туннеля"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        data = response.json()
        
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
        
        return None
    except Exception as e:
        print(f"❌ Ошибка получения ngrok URL: {e}")
        return None

def update_webapp_config(ngrok_url):
    """Обновляет конфигурацию веб-приложения"""
    config_file = 'webapp_config.py'
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем URL
        new_content = content.replace(
            'WEBAPP_BASE_URL = "https://your-domain.com"',
            f'WEBAPP_BASE_URL = "{ngrok_url}"'
        )
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Конфигурация обновлена: {ngrok_url}")
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления конфигурации: {e}")
        return False

def test_webapp_access(url):
    """Тестирует доступность веб-приложения"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Веб-приложение доступно: {url}")
            return True
        else:
            print(f"❌ Веб-приложение недоступно: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки веб-приложения: {e}")
        return False

def main():
    print("🎯 Тестирование интеграции веб-приложения с ботом")
    print("=" * 50)
    
    # Проверяем ngrok
    if not check_ngrok():
        print("❌ ngrok не установлен!")
        print("📥 Установите ngrok: https://ngrok.com/download")
        return
    
    print("✅ ngrok найден")
    
    # Запускаем веб-сервер
    server_process = start_webapp_server()
    if not server_process:
        return
    
    print("✅ Веб-сервер запущен на порту 8080")
    
    # Запускаем ngrok
    print("🌐 Запуск ngrok туннеля...")
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', '8080'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)  # Даем время ngrok запуститься
    
    # Получаем URL
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("❌ Не удалось получить ngrok URL")
        ngrok_process.terminate()
        server_process.terminate()
        return
    
    print(f"✅ ngrok туннель создан: {ngrok_url}")
    
    # Обновляем конфигурацию
    if not update_webapp_config(ngrok_url):
        ngrok_process.terminate()
        server_process.terminate()
        return
    
    # Тестируем доступность
    webapp_url = f"{ngrok_url}/enhanced.html"
    if not test_webapp_access(webapp_url):
        ngrok_process.terminate()
        server_process.terminate()
        return
    
    print("\n🎉 Готово к тестированию!")
    print("=" * 50)
    print(f"🌐 Веб-приложение: {webapp_url}")
    print(f"📱 Мобильная версия: {ngrok_url}/mobile-test.html")
    print(f"🧪 Простая версия: {ngrok_url}/test.html")
    print("\n📋 Следующие шаги:")
    print("1. Запустите бота: python bot.py")
    print("2. Отправьте /start боту")
    print("3. Выберите группу")
    print("4. Нажмите '🚀 Веб-приложение'")
    print("5. Проверьте, что приложение открывается")
    print("\n⏹️  Нажмите Ctrl+C для остановки")
    
    try:
        # Держим процессы запущенными
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Остановка...")
        ngrok_process.terminate()
        server_process.terminate()
        print("✅ Процессы остановлены")

if __name__ == "__main__":
    main()
