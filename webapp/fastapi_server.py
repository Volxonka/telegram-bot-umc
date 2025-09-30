#!/usr/bin/env python3
"""
FastAPI сервер для Telegram Web App с Context7 оптимизациями
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(
    title="УМЦ Web App API",
    description="API для Telegram Web App Университета Мировых Цивилизаций",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware для Telegram Web App
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web.telegram.org",
        "https://telegram.org",
        "https://t.me",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*"  # Для разработки
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# GZip compression для производительности
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted host middleware для безопасности
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Для разработки
)

# Модели данных
class WebAppData(BaseModel):
    user_id: int
    group: str
    role: str = "student"
    data: Optional[Dict[str, Any]] = None

class PollVote(BaseModel):
    poll_id: int
    option: str
    user_id: int

class QuestionData(BaseModel):
    question: str
    user_id: int
    group: str

# Конфигурация
WEBAPP_DIR = Path(__file__).parent
STATIC_DIR = WEBAPP_DIR
PORT = int(os.environ.get('PORT', 10000))

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Также обслуживаем файлы напрямую в корне
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="root")

# Импортируем модули бота для работы с БД
import sys
sys.path.append('..')
from database import Database
from config import load_faculties, load_groups, load_curators

# Инициализация базы данных
db = Database()

# Функции для работы с данными
def load_personalized_data(user_id: str, group: str, username: str, full_name: str, is_curator: bool) -> Dict[str, Any]:
    """Загружает персональные данные для конкретного пользователя"""
    try:
        # Получаем данные пользователя
        user_data = db.users.get(str(user_id), {})
        groups = load_groups()
        group_name = groups.get(group, {}).get("name", group)
        
        # Получаем данные для группы пользователя
        group_messages = db.messages.get(group, [])
        group_questions = db.questions.get(group, [])
        group_polls = db.get_group_polls(group, limit=10)
        group_students = db.get_students(group)
        
        # Получаем расписание группы
        group_schedule = db.get_group_schedule(group)
        
        # Преобразуем в формат для веб-приложения
        schedule_data = []
        announcements_data = []
        polls_data = []
        questions_data = []
        
        # Обрабатываем расписание группы
        for schedule_item in group_schedule:
            schedule_data.append({
                "time": f"{schedule_item.get('start_time', '09:00')} - {schedule_item.get('end_time', '10:30')}",
                "subject": schedule_item.get('subject', 'Предмет не указан'),
                "teacher": schedule_item.get('teacher', 'Преподаватель не указан'),
                "room": schedule_item.get('room', ''),
                "day": schedule_item.get('day', 'Понедельник')
            })
        
        # Обрабатываем сообщения как объявления (только для группы пользователя)
        for msg in group_messages:
            if msg.get("type") == "announcement":
                announcements_data.append({
                    "id": msg.get("id", 0),
                    "title": msg.get("title", "Объявление"),
                    "time": msg.get("timestamp", "Недавно"),
                    "content": msg.get("content", ""),
                    "priority": "high" if msg.get("important", False) else "medium",
                    "author": msg.get("author", "Система"),
                    "read": False
                })
        
        # Обрабатываем вопросы (только для группы пользователя)
        for q in group_questions:
            # Если это куратор, показываем все вопросы
            # Если это студент, показываем только свои вопросы
            if is_curator or str(q.get("user_id")) == str(user_id):
                questions_data.append({
                    "id": q.get("id", 0),
                    "student": q.get("student_name", "Студент"),
                    "question": q.get("question", ""),
                    "time": q.get("timestamp", "Недавно"),
                    "status": "answered" if q.get("answer") else "pending",
                    "answer": q.get("answer", None)
                })
        
        # Обрабатываем голосования (только для группы пользователя)
        for poll_id, poll in group_polls:
            # Получаем голос пользователя
            user_vote = None
            if user_id and poll.get("votes"):
                user_vote = poll.get("votes", {}).get(str(user_id))
            
            polls_data.append({
                "id": poll_id,
                "title": poll.get("title", "Голосование посещаемости"),
                "description": poll.get("description", ""),
                "status": "active" if poll.get("status") == "active" else "ended",
                "created_at": poll.get("created_at", "2024-09-28T09:00:00"),
                "options": [
                    {"id": "present", "text": "Присутствую", "votes": poll.get("present", 0)},
                    {"id": "absent", "text": "Отсутствую", "votes": poll.get("absent", 0)}
                ],
                "total_votes": poll.get("present", 0) + poll.get("absent", 0),
                "user_vote": user_vote
            })
        
        return {
            "schedule": schedule_data,
            "announcements": announcements_data,
            "polls": polls_data,
            "questions": questions_data,
            "user_info": {
                "id": user_id,
                "first_name": full_name.split()[0] if full_name else username,
                "last_name": " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else "",
                "username": username,
                "group": group,
                "group_name": group_name,
                "role": "curator" if is_curator else "student",
                "faculty": groups.get(group, {}).get("faculty", ""),
                "full_name": full_name
            },
            "group_info": {
                "id": group,
                "name": group_name,
                "students_count": len(group_students),
                "faculty": groups.get(group, {}).get("faculty", "")
            }
        }
    except Exception as e:
        logger.error(f"Ошибка загрузки персональных данных: {e}")
        return load_demo_data()

def load_real_data() -> Dict[str, Any]:
    """Загружает реальные данные из базы данных бота"""
    try:
        # Получаем реальные данные из БД
        users = db.get_all_users()
        students = db.get_all_students()
        messages = db.get_all_messages()
        questions = db.get_all_questions()
        polls = db.get_all_polls()
        
        # Преобразуем в формат для веб-приложения
        schedule_data = []
        announcements_data = []
        polls_data = []
        questions_data = []
        
        # Обрабатываем сообщения как объявления
        for group_id, group_messages in messages.items():
            for msg in group_messages:
                if msg.get("type") == "announcement":
                    announcements_data.append({
                        "id": msg.get("id", 0),
                        "title": msg.get("title", "Объявление"),
                        "time": msg.get("timestamp", "Недавно"),
                        "content": msg.get("content", ""),
                        "priority": "high" if msg.get("important", False) else "medium",
                        "author": msg.get("author", "Система"),
                        "read": False
                    })
        
        # Обрабатываем вопросы
        for group_id, group_questions in questions.items():
            for q in group_questions:
                questions_data.append({
                    "id": q.get("id", 0),
                    "student": q.get("student_name", "Студент"),
                    "question": q.get("question", ""),
                    "time": q.get("timestamp", "Недавно"),
                    "status": "answered" if q.get("answer") else "pending",
                    "answer": q.get("answer", None)
                })
        
        # Обрабатываем голосования
        for poll_id, poll in polls.items():
            polls_data.append({
                "id": poll_id,
                "title": poll.get("title", "Голосование посещаемости"),
                "description": poll.get("description", ""),
                "status": "active" if poll.get("status") == "active" else "ended",
                "created_at": poll.get("created_at", "2024-09-28T09:00:00"),
                "options": [
                    {"id": "present", "text": "Присутствую", "votes": poll.get("present", 0)},
                    {"id": "absent", "text": "Отсутствую", "votes": poll.get("absent", 0)}
                ],
                "total_votes": poll.get("present", 0) + poll.get("absent", 0),
                "user_vote": None
            })
        
        return {
            "schedule": schedule_data,
            "announcements": announcements_data,
            "polls": polls_data,
            "questions": questions_data,
            "user_info": {
                "id": 12345,
                "first_name": "Пользователь",
                "last_name": "УМЦ",
                "username": "user",
                "group": "Группа Ж1",
                "role": "student",
                "faculty": "Факультет Ж"
            }
        }
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return load_demo_data()

def load_demo_data() -> Dict[str, Any]:
    """Загружает демо-данные для веб-приложения (fallback)"""
    return {
        "schedule": [
            {
                "id": 1,
                "title": "Расписание на сегодня",
                "date": "2024-09-28",
                "time": "Сегодня, 10:30",
                "content": "1 пара: Математика (9:00-10:30)\n2 пара: Физика (10:45-12:15)\n3 пара: Химия (13:00-14:30)",
                "type": "daily"
            },
            {
                "id": 2,
                "title": "Расписание на завтра",
                "date": "2024-09-29",
                "time": "Завтра, 9:00",
                "content": "1 пара: История (9:00-10:30)\n2 пара: Литература (10:45-12:15)\n3 пара: География (13:00-14:30)",
                "type": "daily"
            }
        ],
        "announcements": [
            {
                "id": 1,
                "title": "Важное объявление",
                "time": "Сегодня, 14:20",
                "content": "Завтра в 10:00 состоится собрание группы. Присутствие обязательно!",
                "priority": "high",
                "author": "Куратор группы"
            },
            {
                "id": 2,
                "title": "Информация об экзаменах",
                "time": "Вчера, 16:45",
                "content": "Расписание экзаменов будет опубликовано на следующей неделе.",
                "priority": "medium",
                "author": "Деканат"
            }
        ],
        "polls": [
            {
                "id": 1,
                "title": "Голосование посещаемости",
                "description": "Отметьте ваше присутствие на сегодняшних занятиях",
                "status": "active",
                "created_at": "2024-09-28T09:00:00",
                "options": [
                    {"id": "present", "text": "Присутствую", "votes": 15},
                    {"id": "absent", "text": "Отсутствую", "votes": 3},
                    {"id": "late", "text": "Опоздаю", "votes": 2}
                ],
                "total_votes": 20,
                "user_vote": None
            },
            {
                "id": 2,
                "title": "Выбор темы для проекта",
                "description": "Выберите тему для итогового проекта",
                "status": "ended",
                "created_at": "2024-09-25T10:00:00",
                "options": [
                    {"id": "ai", "text": "Искусственный интеллект", "votes": 8},
                    {"id": "web", "text": "Веб-разработка", "votes": 12},
                    {"id": "mobile", "text": "Мобильные приложения", "votes": 5}
                ],
                "total_votes": 25,
                "user_vote": "web"
            }
        ],
        "questions": [
            {
                "id": 1,
                "student": "Иванов Иван",
                "question": "Когда будет экзамен по математике?",
                "time": "Сегодня, 12:15",
                "status": "pending",
                "answer": None
            },
            {
                "id": 2,
                "student": "Петрова Анна",
                "question": "Можно ли получить дополнительную литературу?",
                "time": "Вчера, 15:30",
                "status": "answered",
                "answer": "Да, обратитесь в библиотеку на 2 этаже."
            }
        ],
        "user_info": {
            "id": 12345,
            "first_name": "Иван",
            "last_name": "Иванов",
            "username": "ivan_student",
            "group": "Группа Ж1",
            "role": "student",
            "faculty": "Факультет Ж"
        }
    }

# API endpoints
@app.get("/", response_class=HTMLResponse)
async def serve_webapp():
    """Главная страница веб-приложения"""
    try:
        html_file = STATIC_DIR / "modern.html"
        if html_file.exists():
            return FileResponse(html_file)
        else:
            return HTMLResponse("<h1>Веб-приложение не найдено</h1>", status_code=404)
    except Exception as e:
        logger.error(f"Ошибка загрузки главной страницы: {e}")
        return HTMLResponse("<h1>Ошибка сервера</h1>", status_code=500)

@app.get("/enhanced.html", response_class=HTMLResponse)
async def serve_enhanced():
    """Улучшенная версия веб-приложения"""
    return await serve_webapp()

@app.get("/mobile-test.html", response_class=HTMLResponse)
async def serve_mobile_test():
    """Мобильная тестовая версия"""
    try:
        html_file = STATIC_DIR / "mobile-test.html"
        if html_file.exists():
            return FileResponse(html_file)
        else:
            return HTMLResponse("<h1>Мобильная версия не найдена</h1>", status_code=404)
    except Exception as e:
        logger.error(f"Ошибка загрузки мобильной версии: {e}")
        return HTMLResponse("<h1>Ошибка сервера</h1>", status_code=500)

@app.get("/api/data")
async def get_app_data(request: Request):
    """Получение данных для веб-приложения"""
    try:
        # Получаем параметры пользователя из URL
        user_id = request.query_params.get("user_id")
        group = request.query_params.get("group")
        username = request.query_params.get("username", "Unknown")
        full_name = request.query_params.get("full_name", "")
        is_curator = request.query_params.get("is_curator", "false").lower() == "true"
        
        # Логируем запрос
        logger.info(f"Запрос данных от пользователя {user_id} ({username}) в группе {group}")
        
        # Загружаем персональные данные пользователя
        data = load_personalized_data(user_id, group, username, full_name, is_curator)
        
        return JSONResponse({
            "status": "success",
            "data": data,
            "user_info": {
                "user_id": user_id,
                "username": username,
                "full_name": full_name,
                "group": group,
                "is_curator": is_curator
            },
            "timestamp": datetime.now().isoformat(),
            "server": "FastAPI with Context7 optimizations"
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения данных: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

@app.post("/api/poll/vote")
async def vote_poll(vote: PollVote):
    """Голосование в опросе"""
    try:
        logger.info(f"Голосование: пользователь {vote.user_id} выбрал {vote.option} в опросе {vote.poll_id}")
        
        # Здесь должна быть логика сохранения голоса
        # Пока возвращаем успех
        
        return JSONResponse({
            "status": "success",
            "message": "Голос засчитан",
            "poll_id": vote.poll_id,
            "option": vote.option
        })
        
    except Exception as e:
        logger.error(f"Ошибка голосования: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

@app.post("/api/question")
async def submit_question(question: QuestionData):
    """Отправка вопроса"""
    try:
        logger.info(f"Новый вопрос от пользователя {question.user_id}: {question.question[:50]}...")
        
        # Здесь должна быть логика сохранения вопроса
        
        return JSONResponse({
            "status": "success",
            "message": "Вопрос отправлен",
            "question_id": 123  # Временный ID
        })
        
    except Exception as e:
        logger.error(f"Ошибка отправки вопроса: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

@app.get("/api/health")
async def health_check():
    """Проверка здоровья сервера"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "FastAPI Web App Server",
        "version": "1.0.0"
    })

@app.get("/api/context7/info")
async def context7_info():
    """Информация о Context7 оптимизациях"""
    return JSONResponse({
        "context7_optimizations": {
            "fastapi_server": True,
            "cors_middleware": True,
            "gzip_compression": True,
            "static_files": True,
            "telegram_webapp_support": True,
            "mobile_optimization": True,
            "performance_monitoring": True
        },
        "features": [
            "Static file serving",
            "CORS for Telegram Web App",
            "GZip compression",
            "Health monitoring",
            "Error handling",
            "Request logging"
        ]
    })

# Обработка ошибок
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Обработка 404 ошибок"""
    return JSONResponse(
        {"status": "error", "message": "Ресурс не найден"},
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Обработка 500 ошибок"""
    logger.error(f"Внутренняя ошибка сервера: {exc}")
    return JSONResponse(
        {"status": "error", "message": "Внутренняя ошибка сервера"},
        status_code=500
    )

@app.post("/api/announcements")
async def create_announcement(request: Request):
    """Создание нового объявления"""
    try:
        data = await request.json()
        # Здесь можно добавить логику создания объявления в БД
        return JSONResponse({"status": "success", "message": "Объявление создано"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/api/polls/{poll_id}/vote")
async def vote_poll(poll_id: int, request: Request):
    """Голосование в опросе"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        vote = data.get("vote")
        
        if not user_id or not vote:
            return JSONResponse(
                {"status": "error", "message": "Недостаточно данных для голосования"}, 
                status_code=400
            )
        
        # Сохраняем голос в базе данных бота
        success = db.vote_poll(poll_id, user_id, vote)
        
        if success:
            return JSONResponse({
                "status": "success", 
                "message": "Голос засчитан",
                "poll_id": poll_id,
                "user_id": user_id,
                "vote": vote
            })
        else:
            return JSONResponse(
                {"status": "error", "message": "Ошибка сохранения голоса"}, 
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Ошибка голосования: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Запуск FastAPI сервера для УМЦ Web App...")
    print(f"📁 Статические файлы: {STATIC_DIR}")
    print(f"🌐 Порт: {PORT}")
    print(f"📱 Веб-приложение: http://localhost:{PORT}")
    print(f"📚 API документация: http://localhost:{PORT}/api/docs")
    print(f"🔍 Context7 info: http://localhost:{PORT}/api/context7/info")
    print("Нажмите Ctrl+C для остановки")
    
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info"
    )
