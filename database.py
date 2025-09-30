import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class Database:
    def __init__(self):
        self.users_file = "users.json"
        self.messages_file = "messages.json"
        self.students_file = "students.json"
        self.polls_file = "polls.json"
        self.load_data()
    
    def load_data(self):
        """Загружает данные из файлов"""
        if not os.path.exists(self.users_file):
            self.users = {}
            self.save_users()
        else:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        
        if not os.path.exists(self.messages_file):
            self.messages = {}
            self.save_messages()
        else:
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)

        if not os.path.exists(self.students_file):
            self.students = {}
            self.save_students()
        else:
            with open(self.students_file, 'r', encoding='utf-8') as f:
                self.students = json.load(f)

        if not os.path.exists(self.polls_file):
            self.polls = {}
            self.save_polls()
        else:
            with open(self.polls_file, 'r', encoding='utf-8') as f:
                self.polls = json.load(f)
        
        # Загружаем вопросы
        self.load_questions()
    
    def save_users(self):
        """Сохраняет пользователей в файл"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def save_messages(self):
        """Сохраняет сообщения в файл"""
        with open(self.messages_file, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)

    def save_students(self):
        """Сохраняет список студентов в файл"""
        with open(self.students_file, 'w', encoding='utf-8') as f:
            json.dump(self.students, f, ensure_ascii=False, indent=2)

    def save_polls(self):
        """Сохраняет голосования в файл"""
        with open(self.polls_file, 'w', encoding='utf-8') as f:
            json.dump(self.polls, f, ensure_ascii=False, indent=2)
    
    def add_user(self, user_id: int, username: str, group: str):
        """Добавляет пользователя в группу"""
        self.users[str(user_id)] = {
            "username": username,
            "group": group,
            "is_curator": False,
            "last_screen": None
        }
        self.save_users()
    
    def get_user_group(self, user_id: int) -> Optional[str]:
        """Получает группу пользователя"""
        user = self.users.get(str(user_id))
        return user["group"] if user else None
    
    def get_last_screen(self, user_id: int) -> Optional[str]:
        """Получает последний экран пользователя"""
        user = self.users.get(str(user_id))
        if not user:
            return None
        return user.get("last_screen")
    
    def set_last_screen(self, user_id: int, last_screen: Optional[str]):
        """Устанавливает последний экран пользователя"""
        user_key = str(user_id)
        if user_key not in self.users:
            return
        self.users[user_key]["last_screen"] = last_screen
        self.save_users()
    
    def is_curator(self, user_id: int, group: str) -> bool:
        """Проверяет, является ли пользователь куратором группы"""
        from config import load_curators, ADMIN_ID
        curators = load_curators()
        return user_id in curators.get(group, []) or user_id == ADMIN_ID
    
    def is_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь главным администратором"""
        from config import ADMIN_ID
        return user_id == ADMIN_ID
    
    def get_group_users(self, group: str) -> List[int]:
        """Получает всех пользователей группы"""
        return [int(uid) for uid, user in self.users.items() 
                if user["group"] == group]
    
    def add_message(self, group: str, message_type: str, content: str, sender_id: int, file_id: str = None, media_type: str = None):
        """Добавляет сообщение в группу"""
        if group not in self.messages:
            self.messages[group] = []
        
        message_data = {
            "type": message_type,
            "content": content,
            "sender_id": sender_id,
            "timestamp": str(datetime.now())
        }
        
        # Добавляем медиа данные если есть
        if file_id and media_type:
            message_data["file_id"] = file_id
            message_data["media_type"] = media_type
        
        self.messages[group].append(message_data)
        self.save_messages()
    
    def update_user_rights(self, user_id: int, username: str, group: str, is_curator: bool):
        """Обновляет права пользователя"""
        self.users[str(user_id)] = {
            "username": username,
            "group": group,
            "is_curator": is_curator,
            "last_screen": self.users.get(str(user_id), {}).get("last_screen")
        }
        self.save_users()

    # --- Students ---
    def import_students_text(self, group: str, text: str) -> int:
        """Импортирует студентов из текстового списка (по одному ФИО на строку, возможны номера в начале). Возвращает количество добавленных."""
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if group not in self.students:
            self.students[group] = []
        added = 0
        for line in lines:
            # Убираем начальные номера и точки: '1. Фамилия Имя Отчество'
            cleaned = line
            while cleaned and cleaned[0].isdigit():
                cleaned = cleaned[1:]
            cleaned = cleaned.lstrip('.').strip()
            if not cleaned:
                continue
            # Пропускаем возможные заголовки группы (например, Ж1/БО25-1)
            if len(cleaned) <= 3 and any(c.isalpha() for c in cleaned):
                continue
            # Не дублируем
            if any(s.get('full_name') == cleaned for s in self.students[group]):
                continue
            self.students[group].append({
                "full_name": cleaned,
                "user_id": None,
                "username": None
            })
            added += 1
        self.save_students()
        return added

    def get_students(self, group: str) -> List[Dict]:
        return self.students.get(group, [])

    def link_student_account(self, group: str, full_name: str, user_id: int, username: Optional[str]):
        """Связывает студента с его TG-аккаунтом по ФИО"""
        students = self.students.get(group, [])
        for s in students:
            if s.get('full_name') == full_name:
                s['user_id'] = user_id
                s['username'] = username
                self.save_students()
                return True
        return False
    
    def delete_student(self, group: str, full_name: str) -> bool:
        """Удаляет студента по ФИО из группы"""
        students = self.students.get(group, [])
        for i, s in enumerate(students):
            if s.get('full_name') == full_name:
                del students[i]
                self.students[group] = students
                self.save_students()
                return True
        return False

    def update_student_name(self, group: str, old_full_name: str, new_full_name: str) -> bool:
        """Обновляет ФИО студента в группе"""
        students = self.students.get(group, [])
        for s in students:
            if s.get('full_name') == old_full_name:
                s['full_name'] = new_full_name
                self.save_students()
                return True
        return False

    def add_student(self, group: str, user_id: int, username: str, full_name: str):
        """Добавляет студента в группу с привязкой к аккаунту"""
        if group not in self.students:
            self.students[group] = []
        
        # Проверяем, есть ли уже такой студент
        for student in self.students[group]:
            if student.get('user_id') == user_id:
                # Обновляем существующего студента
                student['username'] = username
                student['full_name'] = full_name
                self.save_students()
                return
        
        # Добавляем нового студента
        self.students[group].append({
            "user_id": user_id,
            "username": username,
            "full_name": full_name
        })
        self.save_students()

    def get_group_students_data(self, group: str) -> List[Dict]:
        """Получает данные студентов группы"""
        return self.students.get(group, [])

    # --- Polls ---
    def create_poll(self, group: str, curator_id: int, duration_minutes: int = 10) -> str:
        """Создает голосование для группы. Возвращает poll_id"""
        poll_id = f"{group}_{int(datetime.now().timestamp())}"
        self.polls[poll_id] = {
            "group": group,
            "curator_id": curator_id,
            "created_at": str(datetime.now()),
            "duration_minutes": duration_minutes,
            "status": "active",  # active, closed
            "responses": {}  # user_id -> {"status": "present"/"absent", "reason": str, "timestamp": str}
        }
        self.save_polls()
        return poll_id

    def get_poll(self, poll_id: str):
        """Получает голосование по ID"""
        return self.polls.get(poll_id)

    def add_poll_response(self, poll_id: str, user_id: int, status: str, reason: str = ""):
        """Добавляет ответ студента в голосование"""
        if poll_id not in self.polls:
            return False
        self.polls[poll_id]["responses"][str(user_id)] = {
            "status": status,
            "reason": reason,
            "timestamp": str(datetime.now())
        }
        self.save_polls()
        return True

    def close_poll(self, poll_id: str):
        """Закрывает голосование"""
        if poll_id in self.polls:
            self.polls[poll_id]["status"] = "closed"
            self.save_polls()

    def get_group_polls(self, group: str, limit: int = 10):
        """Получает последние голосования группы"""
        group_polls = []
        for poll_id, poll in self.polls.items():
            if poll.get("group") == group:
                group_polls.append((poll_id, poll))
        # Сортируем по времени создания (новые первые)
        group_polls.sort(key=lambda x: x[1].get("created_at", ""), reverse=True)
        return group_polls[:limit]

    # --- Questions ---
    def add_question(self, user_id: int, group: str, question: str):
        """Добавляет вопрос от студента"""
        if "questions" not in self.__dict__:
            self.questions = {}
        
        if group not in self.questions:
            self.questions[group] = []
        
        question_id = len(self.questions[group]) + 1
        
        self.questions[group].append({
            "id": question_id,
            "user_id": user_id,
            "question": question,
            "answer": None,
            "answered_by": None,
            "timestamp": str(datetime.now()),
            "status": "pending"  # pending, answered
        })
        
        self.save_questions()
        return question_id
    
    def get_pending_questions(self, group: str):
        """Получает неотвеченные вопросы группы"""
        if "questions" not in self.__dict__:
            return []
        return [q for q in self.questions.get(group, []) if q["status"] == 'pending']
    
    def get_all_questions(self, group: str):
        """Получает все вопросы группы"""
        if "questions" not in self.__dict__:
            return []
        return self.questions.get(group, [])
    
    def get_question(self, group: str, question_id: int):
        """Получает вопрос по id"""
        if "questions" not in self.__dict__:
            return None
        for question in self.questions.get(group, []):
            if question["id"] == question_id:
                return question
        return None
    
    def answer_question(self, group: str, question_id: int, answer: str, curator_id: int):
        """Отвечает на вопрос"""
        if "questions" not in self.__dict__:
            return False
        
        for question in self.questions.get(group, []):
            if question["id"] == question_id:
                question["answer"] = answer
                question["answered_by"] = curator_id
                question["status"] = "answered"
                question["answer_timestamp"] = str(datetime.now())
                self.save_questions()
                return True
        return False
    
    def save_questions(self):
        """Сохраняет вопросы в файл"""
        questions_file = "questions.json"
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=2)
    
    def get_group_schedule(self, group: str):
        """Получает расписание группы из сообщений"""
        if "messages" not in self.__dict__:
            return []
        
        group_messages = self.messages.get(group, [])
        schedule_messages = [m for m in group_messages if m.get('type') == 'schedule']
        
        # Преобразуем в формат расписания
        schedule = []
        for msg in schedule_messages:
            # Парсим расписание из текста сообщения
            content = msg.get('content', '')
            if content:
                # Простой парсинг расписания
                lines = content.split('\n')
                for line in lines:
                    if ':' in line and ('-' in line or '—' in line):
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            time_part = parts[0].strip()
                            subject_part = parts[1].strip()
                            
                            # Извлекаем время
                            if '-' in time_part:
                                time_parts = time_part.split('-')
                                start_time = time_parts[0].strip()
                                end_time = time_parts[1].strip()
                            else:
                                start_time = time_part
                                end_time = ""
                            
                            schedule.append({
                                'start_time': start_time,
                                'end_time': end_time,
                                'subject': subject_part,
                                'teacher': 'Преподаватель не указан',
                                'room': '',
                                'day': 'Понедельник'
                            })
        
        return schedule
    
    def vote_poll(self, poll_id: int, user_id: int, vote: str):
        """Голосование в опросе"""
        try:
            # Находим опрос по ID
            for group_id, polls in self.polls.items():
                if poll_id in polls:
                    poll = polls[poll_id]
                    
                    # Инициализируем голоса если их нет
                    if "votes" not in poll:
                        poll["votes"] = {}
                    
                    # Сохраняем голос пользователя
                    poll["votes"][str(user_id)] = vote
                    
                    # Обновляем счетчики
                    if vote == "present":
                        poll["present"] = poll.get("present", 0) + 1
                    elif vote == "absent":
                        poll["absent"] = poll.get("absent", 0) + 1
                    
                    # Сохраняем изменения
                    self.save_polls()
                    return True
            
            return False
        except Exception as e:
            print(f"Ошибка голосования: {e}")
            return False
    
    def load_questions(self):
        """Загружает вопросы из файла"""
        questions_file = "questions.json"
        if os.path.exists(questions_file):
            with open(questions_file, 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
        else:
            self.questions = {}
    
    # --- Faculty and Group Management ---
    def get_all_faculties(self):
        """Получает все факультеты"""
        from config import load_faculties
        return load_faculties()
    
    def get_all_groups(self):
        """Получает все группы"""
        from config import load_groups
        return load_groups()
    
    def get_groups_by_faculty(self, faculty_id: str):
        """Получает все группы факультета"""
        groups = self.get_all_groups()
        return {k: v for k, v in groups.items() if v.get("faculty") == faculty_id}
    
    def get_all_curators(self):
        """Получает всех кураторов"""
        from config import load_curators
        return load_curators()
    
    def get_all_users(self):
        """Получает всех пользователей"""
        return self.users
    
    def get_all_students(self):
        """Получает всех студентов из всех групп"""
        return self.students
    
    def get_all_messages(self):
        """Получает все сообщения из всех групп"""
        return self.messages
    
    def get_all_questions(self):
        """Получает все вопросы из всех групп"""
        if "questions" not in self.__dict__:
            return {}
        return self.questions
    
    def get_all_polls(self):
        """Получает все голосования"""
        return self.polls
