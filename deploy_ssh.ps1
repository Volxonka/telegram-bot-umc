Write-Host "========================================" -ForegroundColor Green
Write-Host "   Деплой проекта на сервер через SSH" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "[1/4] Добавление файлов в Git..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при добавлении файлов в Git!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "[2/4] Коммит изменений..." -ForegroundColor Yellow
$commitMessage = "Deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при коммите!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "[3/4] Отправка в GitHub..." -ForegroundColor Yellow
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при отправке в GitHub!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "[4/4] Деплой на сервер Beget..." -ForegroundColor Yellow
ssh root@84.54.29.102 "cd /var/www/html && git pull origin main"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при деплое на сервер!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Деплой завершен успешно!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Read-Host "Нажмите Enter для выхода"
