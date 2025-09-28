#!/usr/bin/env python3
"""
Скрипт для запуска FastAPI сервера веб-приложения
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Устанавливает зависимости"""
    print("📦 Установка зависимостей...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "webapp/requirements.txt"
        ], check=True)
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def start_fastapi_server():
    """Запускает FastAPI сервер"""
    print("🚀 Запуск FastAPI сервера...")
    
    try:
        # Переходим в папку webapp
        os.chdir("webapp")
        
        # Запускаем сервер
        subprocess.run([
            sys.executable, "fastapi_server.py"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска сервера: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

def main():
    print("🎯 Запуск FastAPI сервера для веб-приложения УМЦ")
    print("=" * 50)
    
    # Проверяем наличие файлов
    if not Path("webapp/fastapi_server.py").exists():
        print("❌ Файл fastapi_server.py не найден")
        return
    
    if not Path("webapp/requirements.txt").exists():
        print("❌ Файл requirements.txt не найден")
        return
    
    # Устанавливаем зависимости
    if not install_requirements():
        return
    
    print("\n🌐 FastAPI сервер будет доступен по адресам:")
    print("   📱 Веб-приложение: http://localhost:8080")
    print("   📚 API документация: http://localhost:8080/api/docs")
    print("   🔍 Context7 info: http://localhost:8080/api/context7/info")
    print("\n⏹️  Нажмите Ctrl+C для остановки")
    
    # Запускаем сервер
    start_fastapi_server()

if __name__ == "__main__":
    main()
