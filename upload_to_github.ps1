# Установка кодировки UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Git команды
git add .
git commit -m "Добавлена функция очистки объявлений для админов"
git push origin main

Write-Host "Готово! Изменения загружены в GitHub." -ForegroundColor Green


