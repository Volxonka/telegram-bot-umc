@echo off
echo ========================================
echo    Прямой деплой на сервер Beget
echo ========================================
echo.

echo [1/2] Синхронизация файлов с сервером...
rsync -avz --delete --exclude='.git' --exclude='*.bat' --exclude='*.ps1' --exclude='temp_key.pub' ./ root@84.54.29.102:/var/www/html/
if %errorlevel% neq 0 (
    echo Ошибка при синхронизации файлов!
    echo Попробуем альтернативный способ...
    echo.
    echo [1/2] Создание архива...
    powershell -Command "Compress-Archive -Path '*.py','*.json','*.txt','*.md','webapp' -DestinationPath 'deploy.zip' -Force"
    if %errorlevel% neq 0 (
        echo Ошибка при создании архива!
        pause
        exit /b 1
    )
    
    echo [2/2] Загрузка архива на сервер...
    scp deploy.zip root@84.54.29.102:/var/www/html/
    if %errorlevel% neq 0 (
        echo Ошибка при загрузке архива!
        pause
        exit /b 1
    )
    
    echo Распаковка архива на сервере...
    ssh root@84.54.29.102 "cd /var/www/html && unzip -o deploy.zip && rm deploy.zip"
    if %errorlevel% neq 0 (
        echo Ошибка при распаковке архива!
        pause
        exit /b 1
    )
    
    del deploy.zip
)

echo.
echo ========================================
echo    Деплой завершен успешно!
echo ========================================
pause
