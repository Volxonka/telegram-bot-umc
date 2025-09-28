# 🚀 Деплой веб-приложения на Render

## 📋 **Пошаговая инструкция:**

### **Шаг 1: Закоммитить изменения**
```bash
git add .
git commit -m "Add webapp for Render deployment"
```

### **Шаг 2: Запушить в репозиторий**
```bash
git push origin main
```

### **Шаг 3: Настроить Render**

1. **Зайдите на** https://render.com
2. **Войдите** в свой аккаунт
3. **Нажмите** "New +" → "Web Service"
4. **Подключите** ваш GitHub репозиторий
5. **Настройте:**
   - **Name:** `telegram-webapp-umc`
   - **Root Directory:** `webapp`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn fastapi_server:app --host 0.0.0.0 --port $PORT`

### **Шаг 4: Дождаться деплоя**
- Render автоматически задеплоит веб-приложение
- Получите URL (например: `https://telegram-webapp-umc.onrender.com`)

### **Шаг 5: Обновить конфигурацию**
Замените в `webapp_config.py`:
```python
WEBAPP_BASE_URL = "https://telegram-webapp-umc.onrender.com"
```

### **Шаг 6: Включить кнопку Web App**
Раскомментируйте в `bot.py`:
```python
[InlineKeyboardButton("🚀 Веб-приложение", callback_data=f"webapp_{group}")],
application.add_handler(CallbackQueryHandler(handle_webapp, pattern="^webapp_"))
```

### **Шаг 7: Задеплоить бота**
```bash
git add .
git commit -m "Enable webapp button with HTTPS URL"
git push origin main
```

## 🎯 **Результат:**
- ✅ Веб-приложение доступно по HTTPS
- ✅ Кнопка Web App работает в боте
- ✅ Полная интеграция бот + веб-приложение

---

**🚀 Готово к деплою!** ✨
