# 🔐 Настройка HTTPS для Telegram Web App

## 🚨 **Проблема:**
```
telegram.error.BadRequest: Inline keyboard button web app url 'http://localhost:8081/enhanced.html' is invalid: only https links are allowed
```

**Telegram Web App требует HTTPS ссылки!**

## 🔧 **Решение: Использовать ngrok**

### **Шаг 1: Установите ngrok**
1. Скачайте ngrok: https://ngrok.com/download
2. Распакуйте в папку (например, `C:\ngrok\`)
3. Добавьте в PATH или используйте полный путь

### **Шаг 2: Запустите FastAPI сервер**
```bash
cd D:\imc\webapp
python fastapi_server.py
```

### **Шаг 3: Запустите ngrok**
```bash
ngrok http 8081
```

### **Шаг 4: Получите HTTPS URL**
ngrok покажет что-то вроде:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8081
```

### **Шаг 5: Обновите конфигурацию**
Замените в `webapp_config.py`:
```python
WEBAPP_BASE_URL = "https://abc123.ngrok.io"
```

### **Шаг 6: Перезапустите бота**
```bash
python bot.py
```

## 🎯 **Альтернативное решение: Временно отключить Web App**

Если ngrok не работает, можно временно отключить кнопку Web App:
