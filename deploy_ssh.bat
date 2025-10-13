@echo off
echo ========================================
echo    Деплой проекта на сервер через SSH
echo ========================================
echo.

echo [1/4] Добавление файлов в Git...
git add .
if %errorlevel% neq 0 (
    echo Ошибка при добавлении файлов в Git!
    pause
    exit /b 1
)

echo [2/4] Коммит изменений...
git commit -m "Deploy: %date% %time%"
if %errorlevel% neq 0 (
    echo Ошибка при коммите!
    pause
    exit /b 1
)

echo [3/4] Отправка в GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo Ошибка при отправке в GitHub!
    pause
    exit /b 1
)

echo [4/4] Деплой на сервер Beget...
ssh root@84.54.29.102 "cd /var/www/html && git pull origin main"
if %errorlevel% neq 0 (
    echo Ошибка при деплое на сервер!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Деплой завершен успешно!
echo ========================================
pause
