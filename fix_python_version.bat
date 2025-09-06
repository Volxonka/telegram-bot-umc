@echo off
echo Исправление версии Python...
git add .python-version runtime.txt requirements.txt
git commit -m "Fix: Use Python 3.11.9 instead of 3.13 for compatibility"
git push origin main
echo Готово! Теперь перезапусти деплой в Render.
pause
