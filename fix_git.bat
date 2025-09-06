@echo off
echo Исправление Git репозитория...
git branch -M main
echo Попытка отправки в GitHub...
git push -u origin main
echo Готово!
pause
