#!/usr/bin/env python3
"""
API для интеграции веб-приложения с Telegram ботом
"""

import json
import os
import sys
from datetime import datetime

# Добавляем путь к основному проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from config import load_groups, load_curators

class WebAppAPI:
    def __init__(self):
        self.db = Database()
    
    def get_user_data(self, user_id, group):
        """Получает данные пользователя для веб-приложения"""
        try:
            user_info = self.db.users.get(str(user_id), {})
            groups = load_groups()
            group_name = groups.get(group, {}).get("name", group)
            is_curator = self.db.is_curator(user_id, group)
            
            return {
                "user_id": user_id,
                "username": user_info.get("username", "Unknown"),
                "full_name": user_info.get("full_name", ""),
                "group": group,
                "group_name": group_name,
                "is_curator": is_curator,
                "role": "curator" if is_curator else "student"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_schedule(self, group):
        """Получает расписание для группы"""
        try:
            messages = self.db.get_messages_by_group(group)
            schedule_messages = [msg for msg in messages if msg.get("type") == "schedule"]
            
            # Сортируем по времени (новые сверху)
            schedule_messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            result = []
            for msg in schedule_messages[:5]:  # Последние 5 расписаний
                result.append({
                    "id": msg.get("id"),
                    "title": f"Расписание - {msg.get('timestamp', 'Неизвестно')}",
                    "content": msg.get("content", ""),
                    "time": self.format_timestamp(msg.get("timestamp")),
                    "has_media": bool(msg.get("photo") or msg.get("document"))
                })
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def get_announcements(self, group):
        """Получает объявления для группы"""
        try:
            messages = self.db.get_messages_by_group(group)
            announcement_messages = [msg for msg in messages if msg.get("type") == "announcement"]
            
            # Сортируем по времени (новые сверху)
            announcement_messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            result = []
            for msg in announcement_messages[:10]:  # Последние 10 объявлений
                result.append({
                    "id": msg.get("id"),
                    "title": msg.get("title", "Объявление"),
                    "content": msg.get("content", ""),
                    "time": self.format_timestamp(msg.get("timestamp")),
                    "has_media": bool(msg.get("photo") or msg.get("document"))
                })
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def get_polls(self, group, user_id):
        """Получает голосования для группы"""
        try:
            polls = self.db.get_polls_by_group(group)
            result = []
            
            for poll in polls:
                poll_data = {
                    "id": poll.get("id"),
                    "title": poll.get("title", "Голосование"),
                    "status": "active" if poll.get("active", False) else "ended",
                    "created_time": self.format_timestamp(poll.get("timestamp")),
                    "duration": poll.get("duration", 30),
                    "options": ["Присутствую", "Отсутствую", "Опоздаю"],
                    "user_voted": str(user_id) in poll.get("votes", {}),
                    "total_votes": len(poll.get("votes", {}))
                }
                
                # Добавляем результаты голосования
                votes = poll.get("votes", {})
                poll_data["results"] = {
                    "present": len([v for v in votes.values() if v == "present"]),
                    "absent": len([v for v in votes.values() if v == "absent"]),
                    "late": len([v for v in votes.values() if v == "late"])
                }
                
                result.append(poll_data)
            
            # Сортируем по времени (новые сверху)
            result.sort(key=lambda x: x.get("created_time", ""), reverse=True)
            return result[:10]  # Последние 10 голосований
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_questions(self, group, user_id):
        """Получает вопросы для группы"""
        try:
            questions = self.db.get_questions_by_group(group)
            is_curator = self.db.is_curator(user_id, group)
            
            result = []
            for q in questions:
                question_data = {
                    "id": q.get("id"),
                    "student_id": q.get("student_id"),
                    "student_name": q.get("student_name", "Неизвестно"),
                    "question": q.get("question", ""),
                    "answer": q.get("answer", ""),
                    "time": self.format_timestamp(q.get("timestamp")),
                    "answered": bool(q.get("answer")),
                    "answered_time": self.format_timestamp(q.get("answered_timestamp")) if q.get("answered_timestamp") else None
                }
                
                # Для студентов показываем только свои вопросы
                # Для кураторов показываем все неотвеченные вопросы
                if is_curator:
                    if not question_data["answered"]:
                        result.append(question_data)
                else:
                    if question_data["student_id"] == user_id:
                        result.append(question_data)
            
            # Сортируем по времени (новые сверху)
            result.sort(key=lambda x: x.get("time", ""), reverse=True)
            return result[:20]  # Последние 20 вопросов
            
        except Exception as e:
            return {"error": str(e)}
    
    def submit_question(self, user_id, group, question_text):
        """Отправляет вопрос от студента"""
        try:
            user_info = self.db.users.get(str(user_id), {})
            student_name = user_info.get("full_name", user_info.get("username", "Неизвестно"))
            
            question_id = self.db.add_question(group, user_id, student_name, question_text)
            
            return {
                "success": True,
                "question_id": question_id,
                "message": "Вопрос отправлен куратору"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def submit_poll_vote(self, user_id, group, poll_id, vote):
        """Отправляет голос в голосовании"""
        try:
            success = self.db.vote_poll(poll_id, user_id, vote)
            
            if success:
                return {
                    "success": True,
                    "message": "Ваш голос учтен"
                }
            else:
                return {
                    "success": False,
                    "message": "Ошибка при голосовании"
                }
        except Exception as e:
            return {"error": str(e)}
    
    def format_timestamp(self, timestamp):
        """Форматирует timestamp для отображения"""
        if not timestamp:
            return "Неизвестно"
        
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            
            now = datetime.now()
            diff = now - dt.replace(tzinfo=None) if dt.tzinfo else now - dt
            
            if diff.days > 0:
                return f"{diff.days} дн. назад"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} ч. назад"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} мин. назад"
            else:
                return "Только что"
        except:
            return "Неизвестно"

# Глобальный экземпляр API
api = WebAppAPI()
