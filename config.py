import os
import json
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', "8311335395:AAFFWfZgLGtH7C-1ES_RW4gchOCuhO7Qi-E")

# ID главного администратора (у вас полные права на все факультеты)
ADMIN_ID = 665509323  # Ваш ID

# Файлы для хранения динамических данных
FACULTIES_FILE = "faculties.json"
GROUPS_FILE = "groups.json"
CURATORS_FILE = "curators.json"

# Инициализация базовых данных
def init_default_data():
    """Инициализирует базовые данные если файлы не существуют"""
    
    # Базовые факультеты
    if not os.path.exists(FACULTIES_FILE):
        default_faculties = {
            "ж": {"name": "Факультет Ж", "description": "Факультет Ж УМЦ"},
            "р": {"name": "Факультет Р", "description": "Факультет Р УМЦ"}
        }
        with open(FACULTIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_faculties, f, ensure_ascii=False, indent=2)
    
    # Базовые группы
    if not os.path.exists(GROUPS_FILE):
        default_groups = {
            "ж1": {"name": "Ж1", "faculty": "ж", "description": "Группа Ж1"},
            "ж2": {"name": "Ж2", "faculty": "ж", "description": "Группа Ж2"},
            "ж3": {"name": "Ж3", "faculty": "ж", "description": "Группа Ж3"},
            "р1": {"name": "Р1", "faculty": "р", "description": "Группа Р1"},
            "р2": {"name": "Р2", "faculty": "р", "description": "Группа Р2"}
        }
        with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_groups, f, ensure_ascii=False, indent=2)
    
    # Базовые кураторы
    if not os.path.exists(CURATORS_FILE):
        default_curators = {
            "ж1": [665509323],  # ID куратора Ж1 (@Meep4anskiy)
            "ж2": [],            # ID куратора Ж2 (пока не назначен)
            "ж3": [1617448796], # ID куратора Ж3
            "р1": [1408151201], # ID куратора Р1
            "р2": [943915529]   # ID куратора Р2
        }
        with open(CURATORS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_curators, f, ensure_ascii=False, indent=2)

# Инициализируем данные при импорте
init_default_data()

# Функции для работы с данными
def load_faculties():
    """Загружает факультеты из файла"""
    with open(FACULTIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_faculties(faculties):
    """Сохраняет факультеты в файл"""
    with open(FACULTIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(faculties, f, ensure_ascii=False, indent=2)

def load_groups():
    """Загружает группы из файла"""
    with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_groups(groups):
    """Сохраняет группы в файл"""
    with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

def load_curators():
    """Загружает кураторов из файла"""
    with open(CURATORS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_curators(curators):
    """Сохраняет кураторов в файл"""
    with open(CURATORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(curators, f, ensure_ascii=False, indent=2)

# Загружаем текущие данные
FACULTIES = load_faculties()
GROUPS = load_groups()
CURATORS = load_curators()

# Обратная совместимость - создаем старые структуры для существующего кода
GROUPS_LEGACY = {k: v["name"] for k, v in GROUPS.items()}