@echo off
echo Обновление requirements.txt...
git add requirements.txt
git commit -m "Fix: Update python-telegram-bot to version 21.0.1 for Python 3.13 compatibility"
git push origin main
echo Готово! Теперь перезапусти деплой в Render.
pause
