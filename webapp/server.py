#!/usr/bin/env python3
"""
Простой веб-сервер для хостинга Telegram Web App
Запуск: python server.py
"""

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

class WebAppHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        # Обработка корневого пути
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        
        # Добавляем CORS заголовки для Telegram Web App
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Обслуживаем файлы
        return super().do_GET()
    
    def do_POST(self):
        """Обработка POST запросов от веб-приложения"""
        if self.path == '/api/data':
            self.handle_api_request()
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        """Обработка CORS preflight запросов"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_api_request(self):
        """Обработка API запросов от веб-приложения"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Здесь можно добавить логику для получения данных из бота
            # Пока возвращаем тестовые данные
            response_data = {
                "status": "success",
                "data": {
                    "schedule": [
                        {
                            "title": "Расписание на сегодня",
                            "time": "Сегодня, 10:30",
                            "content": "1 пара: Математика (9:00-10:30)\n2 пара: Физика (10:45-12:15)\n3 пара: Химия (13:00-14:30)"
                        }
                    ],
                    "announcements": [
                        {
                            "title": "Важное объявление",
                            "time": "Сегодня, 14:20",
                            "content": "Завтра в 10:00 состоится собрание группы. Присутствие обязательно!"
                        }
                    ],
                    "polls": [
                        {
                            "id": 1,
                            "title": "Голосование посещаемости",
                            "status": "active",
                            "options": ["Присутствую", "Отсутствую", "Опоздаю"]
                        }
                    ],
                    "questions": [
                        {
                            "id": 1,
                            "student": "Иванов Иван",
                            "question": "Когда будет экзамен по математике?",
                            "time": "Сегодня, 12:15"
                        }
                    ]
                }
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

def run_server(port=None):
    """Запуск веб-сервера"""
    if port is None:
        port = int(os.environ.get('PORT', 8080))  # Для Heroku/Render
    
    with socketserver.TCPServer(("", port), WebAppHandler) as httpd:
        print(f"🚀 Веб-сервер запущен на порту {port}")
        print(f"📱 Откройте в браузере: http://localhost:{port}")
        print(f"🔗 Для Telegram Web App используйте: https://your-domain.com")
        print("Нажмите Ctrl+C для остановки")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")

if __name__ == "__main__":
    run_server()
