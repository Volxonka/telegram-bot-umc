@echo off
chcp 65001
git add .
git commit -m "Добавлена функция очистки объявлений для админов"
git push origin main
echo Готово!
pause


