#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления кураторов групп
"""

import re

def add_curator():
    print("=== Добавление куратора группы ===")
    print("Доступные группы: ж1, ж2, ж3, р1, р2")
    
    # Показываем текущих кураторов
    print("\nТекущие кураторы:")
    print("ж1: @Meep4anskiy (ID: 665509323)")
    print("ж2: не назначен")
    print("ж3: не назначен") 
    print("р1: ID: 1408151201")
    print("р2: ID: 943915529")
    
    print("\nДля добавления куратора:")
    print("1. Узнайте ID пользователя через @userinfobot")
    print("2. Введите группу и ID")
    print("3. Скопируйте обновленный код в config.py")
    
    group = input("\nВведите группу (ж1/ж2/ж3/р1/р2): ").lower()
    if group not in ['ж1', 'ж2', 'ж3', 'р1', 'р2']:
        print("❌ Неверная группа!")
        return
    
    user_id = input("Введите ID пользователя: ")
    if not user_id.isdigit():
        print("❌ ID должен быть числом!")
        return
    
    username = input("Введите username (без @): ")
    
    print(f"\n✅ Куратор {group}: @{username} (ID: {user_id})")
    print("\nОбновите config.py:")
    print(f'"{group}": [{user_id}],   # ID куратора {group.upper()} (@{username})')

if __name__ == "__main__":
    add_curator()
