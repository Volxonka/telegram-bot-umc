#!/usr/bin/env python3
"""
Скрипт для обновления URL ngrok в конфигурации
"""

def update_ngrok_url(ngrok_url):
    """Обновляет URL ngrok в webapp_config.py"""
    try:
        with open('webapp_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем URL
        new_content = content.replace(
            'WEBAPP_BASE_URL = "http://localhost:8080"',
            f'WEBAPP_BASE_URL = "{ngrok_url}"'
        )
        
        with open('webapp_config.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Конфигурация обновлена: {ngrok_url}")
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Обновление URL ngrok в конфигурации")
    print("=" * 40)
    
    ngrok_url = input("Введите URL ngrok (например: https://abc123.ngrok.io): ").strip()
    
    if ngrok_url.startswith('https://'):
        if update_ngrok_url(ngrok_url):
            print("\n🎉 Готово!")
            print("Теперь перезапустите бота: python bot.py")
        else:
            print("\n❌ Ошибка обновления")
    else:
        print("❌ URL должен начинаться с https://")
