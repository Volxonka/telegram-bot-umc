import logging
import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, GROUPS, CURATORS
from database import Database
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()

def clear_conversation_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Очищает возможные конфликтующие состояния диалога."""
    for key in (
        "waiting_for",
        "target_group",
        "target_question",
        "import_group",
        "edit_student_group",
        "edit_student_old",
        "poll_absent_id",
        "poll_absent_user",
        "poll_group",
        "poll_curator",
    ):
        try:
            context.user_data.pop(key, None)
        except Exception:
            pass

def with_home_button(keyboard, group: str):
    """Добавляет кнопку '🏠 Главное меню' в клавиатуру, если её нет"""
    try:
        for row in keyboard:
            for btn in row:
                if isinstance(btn, InlineKeyboardButton) and (btn.text.startswith("🔙 ") or btn.text.startswith("🏠 ")):
                    return InlineKeyboardMarkup(keyboard)
    except Exception:
        pass
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data=f"back_to_menu_{group}")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начальная команда с выбором группы"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    # Проверяем, зарегистрирован ли пользователь
    user_group = db.get_user_group(user_id)
    
    if user_group:
        # Пользователь уже зарегистрирован
        await show_main_menu(update, context, user_group)
    else:
        # Показываем выбор группы
        await show_group_selection(update, context)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки прав администратора"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    # Проверяем, является ли пользователь куратором какой-либо группы
    curator_groups = []
    for group, curator_ids in CURATORS.items():
        if user_id in curator_ids:
            curator_groups.append(group)
    
    if curator_groups:
        # Пользователь является куратором
        if len(curator_groups) == 1:
            group = curator_groups[0]
            # Обновляем права пользователя в базе
            db.update_user_rights(user_id, username, group, True)
            await show_main_menu(update, context, group)
        else:
            # Пользователь куратор нескольких групп
            await update.message.reply_text(
                f"Вы являетесь куратором групп: {', '.join([GROUPS[g] for g in curator_groups])}\n"
                "Используйте /start для выбора группы."
            )
    else:
        await update.message.reply_text(
            "У вас нет прав администратора. Обратитесь к администратору бота."
        )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс регистрации пользователя"""
    user_id = update.effective_user.id
    
    if str(user_id) in db.users:
        del db.users[str(user_id)]
        db.save_users()
        await update.message.reply_text(
            "✅ Ваша регистрация сброшена! Используйте /start для повторной регистрации."
        )
    else:
        await update.message.reply_text("Вы не зарегистрированы в системе.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда помощи"""
    help_text = """🔧 **Справка по боту УМЦ**

📋 **Основные команды:**
• `/start` - начать работу с ботом
• `/admin` - активировать права куратора
• `/reset` - сбросить регистрацию
• `/help` - показать эту справку
• `/today` - расписание на сегодня

🎯 **Для студентов:**
• 📅 Расписание - просмотр расписания группы
• 📢 Объявления - чтение объявлений
• ❓ Задать вопрос - задать вопрос куратору
• 🔄 Сменить группу - перейти в другую группу

👨‍🏫 **Для кураторов:**
• 📅 Отправить расписание - рассылка всем студентам
• 📢 Сделать объявление - публикация новостей
• ❓ Вопросы студентов - ответы на вопросы
• 📊 Статистика группы - информация о группе

💡 **Советы:**
• Используйте кнопки для навигации
• Вопросы автоматически отправляются куратору
• Ответы приходят с уведомлениями
• Все данные сохраняются автоматически

🆘 **Проблемы?** Обратитесь к администратору бота."""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрый вход в главное меню без /start"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    user_group = db.get_user_group(user_id)

    if user_group:
        await show_main_menu(update, context, user_group)
        return

    # Если пользователь не зарегистрирован, проверим роль куратора
    curator_groups = [g for g, ids in CURATORS.items() if user_id in ids]
    if len(curator_groups) == 1:
        group = curator_groups[0]
        db.update_user_rights(user_id, username, group, True)
        await show_main_menu(update, context, group)
        return
    elif len(curator_groups) > 1:
        await update.message.reply_text(
            "Вы являетесь куратором нескольких групп. Пожалуйста, выберите группу:")
        await show_group_selection(update, context)
        return

    await show_group_selection(update, context)

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открывает последний экран пользователя, если доступен"""
    user_id = update.effective_user.id
    last_screen = db.get_last_screen(user_id)
    if not last_screen:
        await menu(update, context)
        return
    parts = last_screen.split("_", 1)
    if len(parts) != 2:
        await menu(update, context)
        return
    screen, rest = parts[0], parts[1]
    group = rest
    if screen == "menu":
        await show_main_menu(update, context, group)
    elif screen == "today":
        # today_schedule умеет работать из message-path
        await today_schedule(update, context)
    else:
        # Для остальных экранов предложим вернуться в меню и открыть нужный раздел
        await show_main_menu(update, context, group)

async def today_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает расписание на сегодня"""
    # Определяем, откуда пришел запрос
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        group = query.data.replace("today_schedule_", "")
        user_group = group
        is_callback = True
    else:
        user_id = update.effective_user.id
        user_group = db.get_user_group(user_id)
        is_callback = False
    
    if not user_group:
        if is_callback:
            await query.edit_message_text(
                "❌ Вы не зарегистрированы в группе!\n"
                "Используйте /start для регистрации."
            )
        else:
            await update.message.reply_text(
                "❌ Вы не зарегистрированы в группе!\n"
                "Используйте /start для регистрации."
            )
        return
    
    # Сохраняем последний экран
    try:
        db.set_last_screen(user_id, f"today_{user_group}")
    except Exception:
        pass
    
    # Получаем расписание группы
    group_messages = db.messages.get(user_group, [])
    schedule_messages = [m for m in group_messages if m['type'] == 'schedule']
    
    if not schedule_messages:
        text = f"📅 **Расписание на сегодня для группы {GROUPS[user_group]} пока не добавлено.**\n\n"
        text += "💡 Куратор группы добавит расписание в ближайшее время."
    else:
        # Показываем последнее расписание (самое актуальное)
        latest_schedule = schedule_messages[-1]
        text = f"📅 **Расписание на сегодня**\n"
        text += f"Группа: {GROUPS[user_group]}\n\n"
        text += f"{latest_schedule['content']}\n\n"
        text += f"🕐 Обновлено: {latest_schedule['timestamp']}"
    
    # Добавляем кнопки навигации
    keyboard = [
        [InlineKeyboardButton("📅 Все расписания", callback_data=f"view_schedule_{user_group}")]
    ]
    reply_markup = with_home_button(keyboard, user_group)
    
    if is_callback:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_group_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает выбор группы для регистрации"""
    welcome_text = """🎓 **Добро пожаловать в бота "УМЦ"!**

📚 **УМЦ** - это Университет Мировых Цивилизаций, который помогает кураторам и студентам эффективно обучаться в университете.

🔹 **Для кураторов (старост):**
• Отправка расписания всем участникам группы
• Публикация важных объявлений
• Управление группой и просмотр статистики

🔹 **Для студентов:**
• Просмотр актуального расписания
• Чтение объявлений от кураторов
• Удобный доступ к информации группы

Выберите свою группу для регистрации:"""
    
    keyboard = []
    for group_key, group_name in GROUPS.items():
        keyboard.append([InlineKeyboardButton(group_name, callback_data=f"join_{group_key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_group_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор группы"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    username = query.from_user.username or "Unknown"
    
    if query.data.startswith("join_"):
        group = query.data.replace("join_", "")
        
        # Проверяем, является ли пользователь куратором
        if db.is_curator(user_id, group):
            # Кураторы регистрируются без запроса ФИО
            db.add_user(user_id, username, group)
            await query.edit_message_text(
                f"🎉 **Круто! Теперь ты часть цивилизации!** 🎉\n\n"
                f"👨‍🏫 **Роль:** Куратор\n"
                f"👥 **Группа:** {GROUPS[group]}\n\n"
                f"🚀 Добро пожаловать! Теперь ты можешь:\n"
                f"• 📅 Отправлять расписание\n"
                f"• 📢 Делать объявления\n"
                f"• 🗳 Создавать голосования\n"
                f"• 👥 Управлять студентами\n"
                f"• ❓ Отвечать на вопросы\n\n"
                f"**Выбери действие в меню ниже:** ⬇️"
            )
            await show_main_menu(update, context, group)
        else:
            # Для всех студентов запрашиваем ФИО при регистрации
            context.user_data['waiting_for_full_name'] = True
            context.user_data['full_name_group'] = group
            context.user_data['registration_username'] = username
            await query.edit_message_text(
                f"👋 Добро пожаловать в группу {GROUPS[group]}!\n\n"
                "📝 Укажите ваше ФИО для регистрации (например: Иванов Иван Иванович):"
            )

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, group: str):
    """Показывает главное меню для группы"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    
    # Очищаем залипшие состояния при входе в меню
    context.user_data.pop("waiting_for", None)
    context.user_data.pop("target_group", None)
    context.user_data.pop("target_question", None)

    # Сохраняем последний экран
    try:
        db.set_last_screen(user_id, f"menu_{group}")
    except Exception:
        pass
    
    # Проверяем, является ли пользователь куратором
    is_curator = db.is_curator(user_id, group)
    
    if is_curator:
        # Меню для куратора
        keyboard = [
            [InlineKeyboardButton("📅 Отправить расписание", callback_data=f"schedule_{group}")],
            [InlineKeyboardButton("📢 Сделать объявление", callback_data=f"announce_{group}")],
            [InlineKeyboardButton("🗳 Голосование", callback_data=f"polls_menu_{group}")],
            [InlineKeyboardButton("👥 Студенты", callback_data=f"students_menu_{group}")],
            [InlineKeyboardButton("❓ Вопросы студентов", callback_data=f"view_questions_{group}")],
            [InlineKeyboardButton("📊 Статистика группы", callback_data=f"stats_{group}")],
            [InlineKeyboardButton("🔄 Сменить группу", callback_data="change_group")]
        ]
        title = f"👨‍🏫 Меню куратора группы {GROUPS[group]}"
    else:
        # Меню для студента
        keyboard = [
            [InlineKeyboardButton("📅 Расписание", callback_data=f"view_schedule_{group}")],
            [InlineKeyboardButton("📢 Объявления", callback_data=f"view_announce_{group}")],
            [InlineKeyboardButton("🗳 Голосование", callback_data=f"student_polls_{group}")],
            [InlineKeyboardButton("❓ Задать вопрос", callback_data=f"ask_question_{group}")],
            [InlineKeyboardButton("🔄 Сменить группу", callback_data="change_group")]
        ]
        title = f"👨‍🎓 Меню группы {GROUPS[group]}"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(title, reply_markup=reply_markup)
        except Exception:
            # Если не удается отредактировать (например, сообщение уже удалено), отправляем новое
            await context.bot.send_message(
                chat_id=update.callback_query.from_user.id,
                text=title,
                reply_markup=reply_markup
            )
    else:
        try:
            await update.message.reply_text(title, reply_markup=reply_markup)
        except Exception:
            # Резервный канал на случай таймаута
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=title,
                reply_markup=reply_markup
            )

async def handle_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает отправку расписания"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("schedule_", "")
    user_id = query.from_user.id
    
    # Проверяем права куратора
    if not db.is_curator(user_id, group):
        await query.edit_message_text("У вас нет прав для отправки расписания в эту группу!")
        return
    
    # Сохраняем состояние для ожидания расписания
    clear_conversation_state(context)
    context.user_data["waiting_for"] = f"schedule_{group}"
    context.user_data["target_group"] = group
    
    await query.edit_message_text(
        f"📅 **Отправка расписания для группы {GROUPS[group]}**\n\n"
        f"Просто отправьте расписание:\n"
        f"• 📝 Текстом\n"
        f"• 📷 Фото\n"
        f"• 📄 Документ (PDF/JPG/PNG)\n\n"
        f"Расписание будет сохранено и доступно студентам в меню."
    )

async def handle_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает отправку объявления"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("announce_", "")
    user_id = query.from_user.id
    
    # Проверяем права куратора
    if not db.is_curator(user_id, group):
        await query.edit_message_text("У вас нет прав для отправки объявлений в эту группу!")
        return
    
    # Сохраняем состояние для ожидания объявления
    clear_conversation_state(context)
    context.user_data["waiting_for"] = f"announce_{group}"
    context.user_data["target_group"] = group
    
    await query.edit_message_text(
        f"Отправьте объявление для группы {GROUPS[group]}.\n"
        "Можно отправить текст, фото или документ (pdf/jpg/png)."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает входящие сообщения"""
    if not context.user_data.get("waiting_for"):
        # Если нет ожидаемого состояния, автоматически открываем главное меню
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        user_group = db.get_user_group(user_id)

        if user_group:
            await show_main_menu(update, context, user_group)
            return

        # Если пользователь не зарегистрирован, проверим, является ли он куратором
        curator_groups = [g for g, ids in CURATORS.items() if user_id in ids]
        if len(curator_groups) == 1:
            # Автозапись куратора в свою группу и открытие меню куратора
            group = curator_groups[0]
            db.update_user_rights(user_id, username, group, True)
            await show_main_menu(update, context, group)
            return
        elif len(curator_groups) > 1:
            # Куратор нескольких групп — попросим выбрать группу
            await update.message.reply_text(
                "Вы являетесь куратором нескольких групп. Пожалуйста, выберите группу:")
            await show_group_selection(update, context)
            return

        # Обычный пользователь — предложим выбрать группу
        await show_group_selection(update, context)
        return
    
    user_id = update.effective_user.id
    waiting_for = context.user_data["waiting_for"]
    target_group = context.user_data["target_group"]

    # Поддержка медиа
    has_photo = bool(update.message.photo)
    has_document = bool(update.message.document)
    text = update.message.caption if (has_photo or has_document) else update.message.text
    
    if waiting_for.startswith("schedule_"):
            # Проверяем права куратора для расписания
        if not db.is_curator(user_id, target_group):
            await update.message.reply_text("❌ У вас нет прав для отправки расписания в эту группу!")
            return
        
        # Просто сохраняем расписание без отправки уведомлений всем
        if has_photo:
            file_id = update.message.photo[-1].file_id
            db.add_message(target_group, "schedule", text or "[фото]", user_id, file_id, "photo")
            content_type = "фото"
        elif has_document:
            file_id = update.message.document.file_id
            db.add_message(target_group, "schedule", text or "[документ]", user_id, file_id, "document")
            content_type = "документ"
        else:
            db.add_message(target_group, "schedule", text or "", user_id)
            content_type = "текст"
        
        # Очищаем состояние
        context.user_data.pop("waiting_for", None)
        context.user_data.pop("target_group", None)
        
        await update.message.reply_text(
            f"✅ **Расписание успешно сохранено!**\n\n"
            f"📅 Группа: {GROUPS[target_group]}\n"
            f"📝 Тип: {content_type}\n\n"
            f"Студенты могут посмотреть расписание в меню \"📅 Расписание\""
        )
        
    elif waiting_for.startswith("announce_"):
        # Проверяем права куратора для объявлений
        if not db.is_curator(user_id, target_group):
            await update.message.reply_text("❌ У вас нет прав для отправки объявлений в эту группу!")
            return
        
        if has_photo:
            file_id = update.message.photo[-1].file_id
            sent_count = await send_to_group_media(context, target_group, media_type="photo", file_id=file_id, caption=(text or ""), title_prefix="📢 НОВОЕ ОБЪЯВЛЕНИЕ")
            db.add_message(target_group, "announcement", text or "[фото]", user_id)
        elif has_document:
            file_id = update.message.document.file_id
            sent_count = await send_to_group_media(context, target_group, media_type="document", file_id=file_id, caption=(text or ""), title_prefix="📢 НОВОЕ ОБЪЯВЛЕНИЕ")
            db.add_message(target_group, "announcement", text or "[документ]", user_id)
        else:
            sent_count = await send_to_group(update, context, target_group, "📢 НОВОЕ ОБЪЯВЛЕНИЕ", text or "")
            db.add_message(target_group, "announcement", text or "", user_id)
        
        # Очищаем состояние
        context.user_data.pop("waiting_for", None)
        context.user_data.pop("target_group", None)
        
        await update.message.reply_text(
            f"✅ Объявление успешно отправлено всем участникам группы {GROUPS[target_group]}!\n\n"
            f"📊 Уведомления доставлены: {sent_count} студентам"
        )
        
    elif waiting_for.startswith("question_"):
        # Студент задает вопрос (только текст)
        if has_photo or has_document:
            await update.message.reply_text("❌ Пожалуйста, отправьте вопрос текстом.")
            return
        question_id = db.add_question(user_id, target_group, text or "")
        
        # Очищаем состояние
        context.user_data.pop("waiting_for", None)
        context.user_data.pop("target_group", None)
        
        await update.message.reply_text(
            f"✅ Вопрос #{question_id} успешно отправлен куратору группы {GROUPS[target_group]}!\n\n"
            "Куратор ответит на него в ближайшее время."
        )
        
        # Уведомляем кураторов группы
        try:
            from config import CURATORS
            curator_ids = CURATORS.get(target_group, [])
            if curator_ids:
                preview = ((text or "")[:120] + '...') if (text and len(text) > 120) else (text or "")
                notify_text = (
                    f"❓ Новый вопрос от студента в группе {GROUPS[target_group]}\n\n"
                    f"🧑‍🎓 ID студента: {user_id}\n"
                    f"#ID{question_id}\n\n"
                    f"Текст: {preview}"
                )
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📝 Ответить", callback_data=f"answer_question_{target_group}")]
                ])
                for curator_id in curator_ids:
                    try:
                        await context.bot.send_message(chat_id=curator_id, text=notify_text, reply_markup=reply_markup)
                    except Exception as e:
                        logger.error(f"Не удалось уведомить куратора {curator_id}: {e}")
        except Exception as e:
            logger.error(f"Ошибка при уведомлении кураторов: {e}")

        # Планируем напоминания кураторам через 2/6/24 часа, если вопрос не отвечен
        try:
            if context.job_queue:
                for seconds in (2*60*60, 6*60*60, 24*60*60):
                    context.job_queue.run_once(
                        remind_pending_question,
                        when=seconds,
                        data={"group": target_group, "question_id": question_id}
                    )
        except Exception as e:
            logger.error(f"Не удалось запланировать напоминания: {e}")
        
    elif waiting_for.startswith("answer_"):
        # Куратор отвечает на вопрос
        if has_photo or has_document:
            await update.message.reply_text("❌ Ответ должен быть текстовым.")
            return
        parts = waiting_for.split("_")
        question_id = int(parts[2])
        
        # Проверяем права куратора
        if not db.is_curator(user_id, target_group):
            await update.message.reply_text("❌ У вас нет прав для ответов на вопросы в этой группе!")
            return
        
        # Отвечаем на вопрос
        if db.answer_question(target_group, question_id, text or "", user_id):
            # Уведомляем студента об ответе
            question = context.user_data.get("target_question", {})
            if question and "user_id" in question:
                try:
                    await context.bot.send_message(
                        chat_id=question["user_id"],
                        text=(
                            f"💬 **Ответ на ваш вопрос #{question_id}:**\n\n"
                             f"❓ **Вопрос:** {question['question']}\n\n"
                            f"✅ **Ответ:** {text or ''}\n\n"
                             f"👨‍🏫 Группа: {GROUPS[target_group]}"
                        )
                    )
                except Exception as e:
                    logger.error(f"Не удалось отправить ответ студенту {question['user_id']}: {e}")
            
            # Очищаем состояние
            context.user_data.pop("waiting_for", None)
            context.user_data.pop("target_group", None)
            context.user_data.pop("target_question", None)
            
            await update.message.reply_text(
                f"✅ **Ответ на вопрос #{question_id} успешно отправлен студенту!**\n\n"
                f"📝 Вопрос помечен как отвеченный."
            )
        else:
            await update.message.reply_text("❌ Не удалось ответить на вопрос. Возможно, он уже отвечен.")

async def send_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE, group: str, title: str, content: str):
    """Отправляет сообщение всем пользователям группы"""
    users = db.get_group_users(group)
    
    message = f"{title}\n\n{content}\n\n👥 Группа: {GROUPS[group]}"
    
    sent_count = 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
            sent_count += 1
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    
    return sent_count

async def send_to_group_media(context: ContextTypes.DEFAULT_TYPE, group: str, media_type: str, file_id: str, caption: str, title_prefix: str):
    """Отправляет фото/документ всем пользователям группы с общей подписью"""
    users = db.get_group_users(group)
    full_caption = f"{title_prefix}\n\n{caption}\n\n👥 Группа: {GROUPS[group]}" if caption else f"{title_prefix}\n\n👥 Группа: {GROUPS[group]}"
    sent_count = 0
    for user_id in users:
        try:
            if media_type == "photo":
                await context.bot.send_photo(chat_id=user_id, photo=file_id, caption=full_caption)
            elif media_type == "document":
                await context.bot.send_document(chat_id=user_id, document=file_id, caption=full_caption)
            else:
                continue
            sent_count += 1
        except Exception as e:
            logger.error(f"Не удалось отправить {media_type} пользователю {user_id}: {e}")
    return sent_count

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику группы"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("stats_", "")
    user_id = query.from_user.id
    
    # Проверяем права куратора
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ У вас нет прав для просмотра статистики!")
        return
    
    users = db.get_group_users(group)
    group_messages = db.messages.get(group, [])
    
    stats = f"📊 **Статистика группы {GROUPS[group]}**\n\n"
    stats += f"👥 **Участников:** {len(users)}\n"
    stats += f"📝 **Всего сообщений:** {len(group_messages)}\n"
    stats += f"📅 **Расписаний:** {len([m for m in group_messages if m['type'] == 'schedule'])}\n"
    stats += f"📢 **Объявлений:** {len([m for m in group_messages if m['type'] == 'announcement'])}\n"
    stats += f"❓ **Вопросов:** {len(db.get_all_questions(group))}\n"
    stats += f"⏳ **Ожидают ответа:** {len(db.get_pending_questions(group))}"
    
    keyboard = [
        [InlineKeyboardButton("📊 Обновить статистику", callback_data=f"stats_{group}")]
    ]
    reply_markup = with_home_button(keyboard, group)
    
    await query.edit_message_text(stats, reply_markup=reply_markup, parse_mode='Markdown')

async def change_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Позволяет пользователю сменить группу"""
    query = update.callback_query
    await query.answer()
    
    # Удаляем пользователя из текущей группы
    user_id = query.from_user.id
    if str(user_id) in db.users:
        del db.users[str(user_id)]
        db.save_users()
    
    # Показываем выбор новой группы
    await show_group_selection(update, context)

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("back_to_menu_", "")
    
    # Проверяем, что пользователь все еще в этой группе
    user_id = query.from_user.id
    current_group = db.get_user_group(user_id)
    
    if not current_group or current_group != group:
        # Пользователь сменил группу или не зарегистрирован
        try:
            await query.edit_message_text(
                "❌ **Ошибка навигации**\n\n"
                "Ваша группа изменилась или вы не зарегистрированы.\n"
                "Используйте /start для повторной регистрации."
            )
        except Exception:
            # Если не удается отредактировать, отправляем новое сообщение
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ **Ошибка навигации**\n\n"
                "Ваша группа изменилась или вы не зарегистрированы.\n"
                "Используйте /start для повторной регистрации."
            )
        return
    
    await show_main_menu(update, context, group)



async def view_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает расписание группы"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("view_schedule_", "")
    user_id = query.from_user.id
    group_messages = db.messages.get(group, [])
    
    # Сохраняем последний экран
    try:
        db.set_last_screen(user_id, f"view_schedule_{group}")
    except Exception:
        pass
    
    schedule_messages = [m for m in group_messages if m['type'] == 'schedule']
    
    if not schedule_messages:
        text = f"📅 **Расписание для группы {GROUPS[group]} пока не добавлено.**\n\n"
        text += "💡 Куратор группы добавит расписание в ближайшее время."
        
        keyboard = []
        reply_markup = with_home_button(keyboard, group)
    else:
        # Показываем последнее расписание
        latest_schedule = schedule_messages[-1]
        
        # Проверяем, есть ли медиа
        if latest_schedule.get('file_id') and latest_schedule.get('media_type'):
            file_id = latest_schedule['file_id']
            media_type = latest_schedule['media_type']
            caption = f"📅 **Расписание группы {GROUPS[group]}**\n\n{latest_schedule['content']}\n\n📅 Обновлено: {latest_schedule.get('timestamp', 'Неизвестно')}"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Обновить", callback_data=f"view_schedule_{group}")]
            ]
            reply_markup = with_home_button(keyboard, group)
            
            if media_type == "photo":
                await context.bot.send_photo(chat_id=query.from_user.id, photo=file_id, caption=caption, reply_markup=reply_markup, parse_mode='Markdown')
            elif media_type == "document":
                await context.bot.send_document(chat_id=query.from_user.id, document=file_id, caption=caption, reply_markup=reply_markup, parse_mode='Markdown')
            
            # Удаляем старое сообщение
            await query.delete_message()
            return
        else:
            # Обычное текстовое расписание
            text = f"📅 **Расписание группы {GROUPS[group]}**\n\n"
            text += f"{latest_schedule['content']}\n\n"
            text += f"📅 Обновлено: {latest_schedule.get('timestamp', 'Неизвестно')}"
    
            keyboard = [
                [InlineKeyboardButton("🔄 Обновить", callback_data=f"view_schedule_{group}")]
            ]
            reply_markup = with_home_button(keyboard, group)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            return

    # Единая точка отправки ответа
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def view_announcements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает объявления группы"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("view_announce_", "")
    user_id = query.from_user.id
    group_messages = db.messages.get(group, [])
    
    # Сохраняем последний экран
    try:
        db.set_last_screen(user_id, f"view_announce_{group}")
    except Exception:
        pass
    
    announce_messages = [m for m in group_messages if m['type'] == 'announcement']
    
    if not announce_messages:
        text = f"📢 **Объявления для группы {GROUPS[group]} пока нет.**\n\n"
        text += "💡 Куратор группы добавит объявления в ближайшее время."
    else:
        text = f"📢 **Объявления группы {GROUPS[group]}**\n\n"
        for i, msg in enumerate(announce_messages[-5:], 1):  # Показываем последние 5 объявлений
            text += f"**Объявление #{len(announce_messages) - 5 + i}:**\n"
            text += f"{msg['content']}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("📢 Последние объявления", callback_data=f"view_announce_{group}")]
    ]
    reply_markup = with_home_button(keyboard, group)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает запрос на задание вопроса"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("ask_question_", "")
    user_id = query.from_user.id
    
    # Сохраняем состояние для ожидания вопроса
    clear_conversation_state(context)
    context.user_data["waiting_for"] = f"question_{group}"
    context.user_data["target_group"] = group

    # Сохраняем последний экран
    try:
        db.set_last_screen(user_id, f"ask_question_{group}")
    except Exception:
        pass
    
    # Добавляем кнопку отмены
    keyboard = [[InlineKeyboardButton("❌ Отменить вопрос", callback_data=f"cancel_question_{group}")]]
    reply_markup = with_home_button(keyboard, group)
    
    await query.edit_message_text(
        f"❓ **Задайте ваш вопрос для группы {GROUPS[group]}**\n\n"
        "Просто напишите текст вопроса, и куратор группы ответит на него.\n\n"
        "💡 Вопрос будет отправлен куратору автоматически.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def view_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает только текущие (неотвеченные) вопросы для куратора.

    История отвеченных вопросов намеренно скрыта, чтобы не перегружать интерфейс.
    """
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("view_questions_", "")
    user_id = query.from_user.id
    
    # Проверяем права куратора
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ У вас нет прав для просмотра вопросов!")
        return
    
    # Сохраняем последний экран
    try:
        db.set_last_screen(user_id, f"view_questions_{group}")
    except Exception:
        pass
    
    pending_questions = db.get_pending_questions(group)

    if not pending_questions:
        text = (
            f"❓ **Вопросов для группы {GROUPS[group]} пока нет.**\n\n"
            "💡 Когда появятся новые вопросы от студентов, они будут показаны здесь."
        )
        keyboard = []
    else:
        text = f"❓ **Неотвеченные вопросы группы {GROUPS[group]}**\n\n"
        for q in pending_questions[-5:]:  # Показываем последние 5 неотвеченных
            preview = (q['question'][:80] + '...') if len(q['question']) > 80 else q['question']
            text += f"• ⏳ Вопрос #{q['id']}: {preview}\n"
        text += "\nВыберите \"Ответить на вопрос\", чтобы написать ответ студенту."
        keyboard = [[InlineKeyboardButton("📝 Ответить на вопрос", callback_data=f"answer_question_{group}")]]
    
    reply_markup = with_home_button(keyboard, group)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def answer_question_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню для ответа на вопрос"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("answer_question_", "")
    user_id = query.from_user.id
    
    # Проверяем права куратора
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ У вас нет прав для ответов на вопросы!")
        return
    
    pending_questions = db.get_pending_questions(group)
    
    if not pending_questions:
        await query.edit_message_text(
            f"✅ **Все вопросы группы {GROUPS[group]} уже отвечены!**\n\n"
            f"🎉 Отличная работа, куратор!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data=f"view_questions_{group}")
            ]]),
            parse_mode='Markdown'
        )
        return
    
    # Сохраняем последний экран
    try:
        db.set_last_screen(user_id, f"answer_question_{group}")
    except Exception:
        pass
    
    # Показываем список неотвеченных вопросов
    text = f"❓ **Выберите вопрос для ответа**\n"
    text += f"Группа: {GROUPS[group]}\n\n"
    text += f"📝 **Неотвеченных вопросов:** {len(pending_questions)}\n\n"
    
    keyboard = []
    
    for q in pending_questions[-5:]:  # Показываем последние 5 вопросов
        keyboard.append([
            InlineKeyboardButton(
                f"❓ Вопрос #{q['id']}: {q['question'][:30]}...", 
                callback_data=f"select_question_{group}_{q['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 К вопросам", callback_data=f"view_questions_{group}")])
    reply_markup = with_home_button(keyboard, group)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def select_question_for_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбирает вопрос для ответа"""
    query = update.callback_query
    await query.answer()
    
    # Формат: select_question_{group}_{question_id}
    parts = query.data.split("_")
    group = parts[2]
    question_id = int(parts[3])
    user_id = query.from_user.id
    
    # Проверяем права куратора
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ У вас нет прав для ответов на вопросы!")
        return
    
    # Получаем вопрос
    all_questions = db.get_all_questions(group)
    question = None
    for q in all_questions:
        if q['id'] == question_id and q['status'] == 'pending':
            question = q
            break
    
    if not question:
        await query.edit_message_text("❌ Вопрос не найден или уже отвечен!")
        return
    
    # Сохраняем состояние для ожидания ответа
    clear_conversation_state(context)
    context.user_data["waiting_for"] = f"answer_{group}_{question_id}"
    context.user_data["target_group"] = group
    context.user_data["target_question"] = question
    
    # Добавляем кнопку отмены
    keyboard = [[InlineKeyboardButton("❌ Отменить ответ", callback_data=f"cancel_answer_{group}")]]
    reply_markup = with_home_button(keyboard, group)
    
    await query.edit_message_text(
        f"❓ **Вопрос #{question_id}:**\n\n"
        f"{question['question']}\n\n"
        f"📝 **Напишите ваш ответ:**\n\n"
        f"💡 Ответ будет автоматически отправлен студенту.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Глобальная обработка ошибок: логируем молча, без сообщений пользователю"""
    logger.exception("Unhandled error occurred:", exc_info=context.error)
    # Не шлём пользователю предупреждения, чтобы не спамить интерфейс

async def cancel_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет задание вопроса"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("cancel_question_", "")
    
    # Очищаем состояние
    context.user_data.pop("waiting_for", None)
    context.user_data.pop("target_group", None)
    
    await query.edit_message_text(
        f"❌ **Вопрос отменен**\n\n"
        f"💡 Вы можете задать вопрос позже через главное меню.",
        reply_markup=with_home_button([], group),
        parse_mode='Markdown'
    )

async def cancel_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет ответ на вопрос"""
    query = update.callback_query
    await query.answer()
    
    group = query.data.replace("cancel_answer_", "")
    
    # Очищаем состояние
    context.user_data.pop("waiting_for", None)
    context.user_data.pop("target_group", None)
    context.user_data.pop("target_question", None)
    
    await query.edit_message_text(
        f"❌ **Ответ отменен**\n\n"
        f"💡 Вы можете ответить на вопрос позже.",
        reply_markup=with_home_button([[InlineKeyboardButton("🔙 К вопросам", callback_data=f"view_questions_{group}")]], group),
        parse_mode='Markdown'
    )

async def remind_pending_question(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет напоминание кураторам, если вопрос не отвечен"""
    try:
        data = context.job.data or {}
        group = data.get("group")
        question_id = data.get("question_id")
        if not group or not question_id:
            return
        question = db.get_question(group, question_id)
        if not question or question.get("status") != "pending":
            return
        from config import CURATORS
        curator_ids = CURATORS.get(group, [])
        if not curator_ids:
            return
        preview = (question.get("question", "")[:120] + '...') if len(question.get("question", "")) > 120 else question.get("question", "")
        notify_text = (
            f"⏰ Напоминание: вопрос #{question_id} все еще без ответа\n\n"
            f"Группа: {GROUPS[group]}\n"
            f"Текст: {preview}"
        )
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Ответить", callback_data=f"answer_question_{group}")]
        ])
        for curator_id in curator_ids:
            try:
                await context.bot.send_message(chat_id=curator_id, text=notify_text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Не удалось отправить напоминание куратору {curator_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка в напоминании: {e}")

async def import_students_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ожидает текст и импортирует студентов в указанную группу: /import_students ж1"""
    user_id = update.effective_user.id
    args = context.args if hasattr(context, 'args') else []
    if not args:
        await update.message.reply_text("Использование: /import_students <группа>\nНапример: /import_students ж1")
        return
    group = args[0].lower()
    if group not in GROUPS:
        await update.message.reply_text("Неизвестная группа. Доступные: " + ", ".join(GROUPS.keys()))
        return
    # Проверяем, что пользователь куратор этой группы
    if not db.is_curator(user_id, group):
        await update.message.reply_text("❌ У вас нет прав импортировать студентов для этой группы")
        return
    context.user_data["import_group"] = group
    await update.message.reply_text(
        f"Отправьте текстовый список студентов для группы {GROUPS[group]} одной последующей сообщением.\n"
        "Каждая строка – один студент. Номера в начале строк можно не удалять."
    )

async def handle_import_students_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принимает текст после /import_students и сохраняет студентов"""
    group = context.user_data.get("import_group")
    if not group:
        return False
    text = update.message.text or ""
    added = db.import_students_text(group, text)
    context.user_data.pop("import_group", None)
    await update.message.reply_text(f"✅ Импортировано студентов: {added}\nГруппа: {GROUPS[group]}")
    return True

async def students_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает количество студентов группы и первые 15 ФИО: /students ж1"""
    args = context.args if hasattr(context, 'args') else []
    group = (args[0].lower() if args else db.get_user_group(update.effective_user.id))
    if not group or group not in GROUPS:
        await update.message.reply_text("Использование: /students <группа>")
        return
    students = db.get_students(group)
    count = len(students)
    preview = "\n".join([f"- {s.get('full_name')}" for s in students[:15]]) if students else "—"
    await update.message.reply_text(
        f"👥 Студенты группы {GROUPS[group]}: {count}\n\n" + preview
    )

async def students_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню управления студентами для куратора"""
    query = update.callback_query
    await query.answer()
    group = query.data.replace("students_menu_", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ У вас нет прав для этой группы")
        return
    keyboard = [
        [InlineKeyboardButton("➕ Импорт из текста", callback_data=f"students_import_{group}")],
        [InlineKeyboardButton("📋 Показать список", callback_data=f"students_list_{group}")],
        [InlineKeyboardButton("✏️ Редактировать", callback_data=f"students_edit_{group}"), InlineKeyboardButton("🗑 Удалить", callback_data=f"students_delete_{group}")]
    ]
    reply_markup = with_home_button(keyboard, group)
    await query.edit_message_text(f"👥 Студенты группы {GROUPS[group]}", reply_markup=reply_markup)

async def students_import_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    group = query.data.replace("students_import_", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ Нет прав")
        return
    clear_conversation_state(context)
    context.user_data["import_group"] = group
    await query.edit_message_text(
        f"Отправьте текстовый список студентов для {GROUPS[group]} одной последующей сообщением.\n"
        "Каждая строка — один студент. Номера можно оставлять.")

async def students_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    group = query.data.replace("students_list_", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ Нет прав")
        return
    
    students = db.get_students(group)
    count = len(students)
    
    if not students:
        text = f"👥 **Студенты группы {GROUPS[group]}**\n\nСписок пуст"
    else:
        text = f"👥 **Студенты группы {GROUPS[group]}**\n\n"
        text += f"📊 Всего студентов: {count}\n\n"
        
        for i, student in enumerate(students[:25], 1):  # Показываем первые 25
            full_name = student.get('full_name', 'Не указано')
            username = student.get('username', 'Не указано')
            user_id_student = student.get('user_id', '')
            text += f"{i}. **{full_name}**\n"
            text += f"   👤 @{username} (ID: {user_id_student})\n\n"
        
        if count > 25:
            text += f"... и ещё {count - 25} студентов"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data=f"students_menu_{group}")]]
    reply_markup = with_home_button(keyboard, group)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def students_delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    group = query.data.replace("students_delete_", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ Нет прав")
        return
    students = db.get_students(group)
    keyboard = []
    for s in students[:25]:
        name = s.get('full_name')
        keyboard.append([InlineKeyboardButton(f"🗑 {name[:25]}", callback_data=f"students_delete_pick_{group}_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"students_menu_{group}")])
    reply_markup = with_home_button(keyboard, group)
    await query.edit_message_text("Выберите студента для удаления (первые 25):", reply_markup=reply_markup)

async def students_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_", 4)
    group = parts[3]
    # имя может содержать подчёркивания; используем остаток после 4-го '_'
    full_name = query.data.split(f"students_delete_pick_{group}_", 1)[1]
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ Нет прав")
        return
    keyboard = [
        [InlineKeyboardButton("✅ Да, удалить", callback_data=f"students_delete_do_{group}_{full_name}")],
        [InlineKeyboardButton("❌ Отмена", callback_data=f"students_menu_{group}")]
    ]
    reply_markup = with_home_button(keyboard, group)
    await query.edit_message_text(f"Удалить студента:\n{full_name}?", reply_markup=reply_markup)

async def students_delete_do(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_", 4)
    group = parts[3]
    full_name = query.data.split(f"students_delete_do_{group}_", 1)[1]
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ Нет прав")
        return
    ok = db.delete_student(group, full_name)
    if ok:
        await query.edit_message_text(f"✅ Удалён: {full_name}")
    else:
        await query.edit_message_text("❌ Не найден")

async def students_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    group = query.data.replace("students_edit_", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ Нет прав")
        return
    students = db.get_students(group)
    keyboard = []
    for s in students[:25]:
        name = s.get('full_name')
        keyboard.append([InlineKeyboardButton(f"✏️ {name[:25]}", callback_data=f"students_edit_pick_{group}_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"students_menu_{group}")])
    reply_markup = with_home_button(keyboard, group)
    await query.edit_message_text("Выберите студента для редактирования (первые 25):", reply_markup=reply_markup)

async def students_edit_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_", 4)
    group = parts[3]
    old_name = query.data.split(f"students_edit_pick_{group}_", 1)[1]
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ Нет прав")
        return
    clear_conversation_state(context)
    context.user_data['edit_student_group'] = group
    context.user_data['edit_student_old'] = old_name
    await query.edit_message_text(f"Введите новое ФИО для:\n{old_name}")

async def handle_edit_student_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group = context.user_data.get('edit_student_group')
    old_name = context.user_data.get('edit_student_old')
    if not group or not old_name:
        return False
    new_name = (update.message.text or '').strip()
    if not new_name:
        await update.message.reply_text("ФИО не может быть пустым. Отправьте снова.")
        return True
    ok = db.update_student_name(group, old_name, new_name)
    context.user_data.pop('edit_student_group', None)
    context.user_data.pop('edit_student_old', None)
    if ok:
        await update.message.reply_text(f"✅ Обновлено:\n{old_name}\n→ {new_name}")
    else:
        await update.message.reply_text("❌ Не удалось обновить (возможно, не найдено)")
    return True

# --- Polls ---
async def polls_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню голосований для куратора"""
    query = update.callback_query
    await query.answer()
    group = query.data.replace("polls_menu_", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ У вас нет прав для этой группы")
        return
    keyboard = [
        [InlineKeyboardButton("➕ Создать голосование", callback_data=f"polls_create_{group}")],
        [InlineKeyboardButton("📊 Результаты голосований", callback_data=f"polls_results_{group}")]
    ]
    reply_markup = with_home_button(keyboard, group)
    await query.edit_message_text(f"🗳 Голосования группы {GROUPS[group]}", reply_markup=reply_markup)

async def polls_create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания голосования"""
    query = update.callback_query
    await query.answer()
    group = query.data.replace("polls_create_", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ Нет прав")
        return
    clear_conversation_state(context)
    context.user_data["poll_group"] = group
    context.user_data["poll_curator"] = user_id
    await query.edit_message_text(
        f"Создание голосования для группы {GROUPS[group]}\n\n"
        "Введите длительность голосования в минутах (по умолчанию 10):"
    )

async def handle_poll_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода длительности голосования"""
    group = context.user_data.get("poll_group")
    curator_id = context.user_data.get("poll_curator")
    if not group or not curator_id:
        return False
    
    duration_text = (update.message.text or "").strip()
    try:
        duration = int(duration_text) if duration_text else 10
        if duration < 1 or duration > 60:
            await update.message.reply_text("Длительность должна быть от 1 до 60 минут. Попробуйте снова:")
            return True
    except ValueError:
        await update.message.reply_text("Введите число минут (1-60) или отправьте пустое сообщение для 10 минут:")
        return True
    
    # Удаляем старые голосования группы перед созданием нового
    old_polls = db.get_group_polls(group, limit=100)  # Получаем все голосования
    for old_poll_id, old_poll in old_polls:
        if old_poll_id in db.polls:
            del db.polls[old_poll_id]
    db.save_polls()
    
    # Создаем голосование
    poll_id = db.create_poll(group, curator_id, duration)
    
    # Уведомляем студентов
    users = db.get_group_users(group)
    poll_text = f"🗳 **Голосование посещаемости**\n\nГруппа: {GROUPS[group]}\nВремя: {duration} минут\n\nОтметьтесь, пожалуйста:"
    
    keyboard = [
        [InlineKeyboardButton("✅ Я на месте", callback_data=f"poll_present_{poll_id}")],
        [InlineKeyboardButton("❌ Меня нет", callback_data=f"poll_absent_{poll_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    sent_count = 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=poll_text, reply_markup=reply_markup, parse_mode='Markdown')
            sent_count += 1
        except Exception as e:
            logger.error(f"Не удалось отправить голосование пользователю {user_id}: {e}")
    
    # Планируем закрытие голосования
    if context.job_queue:
        context.job_queue.run_once(close_poll_job, when=duration*60, data={"poll_id": poll_id})
    
    # Очищаем состояние
    context.user_data.pop("poll_group", None)
    context.user_data.pop("poll_curator", None)
    
    await update.message.reply_text(
        f"✅ Голосование создано!\n\n"
        f"📊 Уведомления отправлены: {sent_count} студентам\n"
        f"⏰ Длительность: {duration} минут\n"
        f"🆔 ID голосования: {poll_id}"
    )
    return True

async def close_poll_job(context: ContextTypes.DEFAULT_TYPE):
    """Автоматическое закрытие голосования"""
    try:
        poll_id = context.job.data.get("poll_id")
        if poll_id:
            db.close_poll(poll_id)
            logger.info(f"Голосование {poll_id} автоматически закрыто")
    except Exception as e:
        logger.error(f"Ошибка при закрытии голосования: {e}")

async def poll_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа студента в голосовании"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("poll_present_"):
        poll_id = query.data.replace("poll_present_", "")
        status = "present"
    elif query.data.startswith("poll_absent_"):
        poll_id = query.data.replace("poll_absent_", "")
        status = "absent"
    else:
        return
    
    user_id = query.from_user.id
    poll = db.get_poll(poll_id)
    
    if not poll or poll.get("status") != "active":
        await query.edit_message_text("❌ Голосование завершено или не найдено")
        return
    
    # Проверяем, что студент в правильной группе
    user_group = db.get_user_group(user_id)
    if user_group != poll.get("group"):
        await query.edit_message_text("❌ Вы не состоите в этой группе")
        return
    
    # Защита от повторного голосования
    existing = poll.get("responses", {}).get(str(user_id))
    if existing:
        resp_status = "присутствует" if existing.get("status") == "present" else "отсутствует"
        resp_reason = existing.get("reason", "")
        text = f"🗳 Ваш ответ уже учтён: {resp_status}"
        if resp_reason:
            text += f"\n💬 Причина: {resp_reason}"
        await query.edit_message_text(text)
        return

    if status == "present":
        # Просто отмечаем присутствие
        db.add_poll_response(poll_id, user_id, "present")
        await query.edit_message_text("✅ Отмечено: Я на месте")
    else:
        # Запрашиваем причину отсутствия
        context.user_data["poll_absent_id"] = poll_id
        context.user_data["poll_absent_user"] = user_id
        await query.edit_message_text("Укажите причину отсутствия:")

async def handle_absence_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка причины отсутствия"""
    poll_id = context.user_data.get("poll_absent_id")
    user_id = context.user_data.get("poll_absent_user")
    if not poll_id or not user_id:
        return False
    
    reason = (update.message.text or "").strip()
    if not reason:
        await update.message.reply_text("Пожалуйста, укажите причину отсутствия:")
        return True
    
    db.add_poll_response(poll_id, user_id, "absent", reason)
    context.user_data.pop("poll_absent_id", None)
    context.user_data.pop("poll_absent_user", None)
    
    await update.message.reply_text(f"✅ Отмечено отсутствие\nПричина: {reason}")
    return True

async def handle_full_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода ФИО студента"""
    if not context.user_data.get('waiting_for_full_name'):
        return False
    
    full_name = (update.message.text or '').strip()
    if not full_name:
        await update.message.reply_text("Пожалуйста, укажите ваше ФИО (например: Иванов Иван Иванович):")
        return True
    
    group = context.user_data.get('full_name_group')
    username = context.user_data.get('registration_username', 'Unknown')
    user_id = update.effective_user.id
    
    if group:
        # Регистрируем пользователя с ФИО
        db.add_user(user_id, username, group)
        
        # Обновляем ФИО пользователя
        if str(user_id) in db.users:
            db.users[str(user_id)]['full_name'] = full_name
            db.save_users()
        
        # Добавляем студента в список группы
        db.add_student(group, user_id, username, full_name)
        
        # Очищаем состояние
        context.user_data.pop('waiting_for_full_name', None)
        context.user_data.pop('full_name_group', None)
        context.user_data.pop('registration_username', None)
        
        await update.message.reply_text(
            f"🎉 **Круто! Теперь ты часть цивилизации!** 🎉\n\n"
            f"👤 **ФИО:** {full_name}\n"
            f"👥 **Группа:** {GROUPS[group]}\n\n"
            f"🚀 Добро пожаловать в наш бот! Теперь ты можешь:\n"
            f"• 🗳 Участвовать в голосованиях\n"
            f"• 📅 Получать расписание\n"
            f"• 📢 Читать объявления\n"
            f"• ❓ Задавать вопросы куратору\n\n"
            f"**Выбери действие в меню ниже:** ⬇️"
        )
        await show_main_menu(update, context, group)
    
    return True

async def student_polls_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню голосований для студентов"""
    query = update.callback_query
    await query.answer()
    group = query.data.replace("student_polls_", "")
    user_id = query.from_user.id
    
    # Проверяем, что студент в правильной группе
    user_group = db.get_user_group(user_id)
    if user_group != group:
        await query.edit_message_text("❌ Вы не состоите в этой группе")
        return
    
    # Получаем активное голосование группы
    polls = db.get_group_polls(group, limit=1)
    if not polls:
        await query.edit_message_text(f"🗳 Голосования группы {GROUPS[group]}\n\nПока нет активных голосований")
        return
    
    poll_id, poll = polls[0]
    
    # Проверяем, активно ли голосование
    if poll.get("status") != "active":
        await query.edit_message_text(f"🗳 Голосования группы {GROUPS[group]}\n\nНет активных голосований")
        return
    
    # Проверяем, уже ли студент голосовал
    responses = poll.get("responses", {})
    if str(user_id) in responses:
        response = responses[str(user_id)]
        status = "присутствует" if response.get("status") == "present" else "отсутствует"
        reason = response.get("reason", "")
        
        text = f"🗳 **Ваш ответ в голосовании**\n\n"
        text += f"✅ Статус: {status}\n"
        if reason:
            text += f"💬 Причина: {reason}\n"
        text += f"\nГолосование завершится автоматически."
        
        await query.edit_message_text(text, parse_mode='Markdown')
        return
    
    # Показываем кнопки голосования
    poll_text = f"🗳 **Голосование посещаемости**\n\nГруппа: {GROUPS[group]}\n\nОтметьтесь, пожалуйста:"
    
    keyboard = [
        [InlineKeyboardButton("✅ Я на месте", callback_data=f"poll_present_{poll_id}")],
        [InlineKeyboardButton("❌ Меня нет", callback_data=f"poll_absent_{poll_id}")]
    ]
    reply_markup = with_home_button(keyboard, group)
    
    await query.edit_message_text(poll_text, reply_markup=reply_markup, parse_mode='Markdown')

async def polls_results_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню результатов голосований"""
    query = update.callback_query
    await query.answer()
    group = query.data.replace("polls_results_", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ У вас нет прав для этой группы")
        return
    
    # Получаем последние голосования
    polls = db.get_group_polls(group, limit=10)
    if not polls:
        await query.edit_message_text(f"📊 Голосования группы {GROUPS[group]}\n\nПока нет голосований")
        return
    
    keyboard = []
    for poll_id, poll in polls:
        created_at = poll.get("created_at", "")
        status = poll.get("status", "unknown")
        responses_count = len(poll.get("responses", {}))
        
        # Форматируем дату
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            date_str = dt.strftime("%d.%m %H:%M")
        except:
            date_str = created_at[:16]
        
        status_emoji = "🟢" if status == "active" else "🔴"
        button_text = f"{status_emoji} {date_str} ({responses_count} ответов)"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"poll_view_{poll_id}")])
    
    reply_markup = with_home_button(keyboard, group)
    await query.edit_message_text(f"📊 Голосования группы {GROUPS[group]}\n\nВыберите голосование для просмотра:", reply_markup=reply_markup)

async def poll_view_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Детальный просмотр голосования"""
    query = update.callback_query
    await query.answer()
    poll_id = query.data.replace("poll_view_", "")
    
    poll = db.get_poll(poll_id)
    if not poll:
        await query.edit_message_text("❌ Голосование не найдено")
        return
    
    group = poll.get("group", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ У вас нет прав для просмотра этого голосования")
        return
    
    # Форматируем дату создания
    created_at = poll.get("created_at", "")
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        date_str = dt.strftime("%d.%m.%Y %H:%M")
    except:
        date_str = created_at
    
    status = poll.get("status", "unknown")
    duration = poll.get("duration_minutes", 0)
    responses = poll.get("responses", {})
    
    # Статистика
    present_count = sum(1 for r in responses.values() if r.get("status") == "present")
    absent_count = sum(1 for r in responses.values() if r.get("status") == "absent")
    total_responses = len(responses)
    
    # Получаем список студентов группы для сравнения
    students = db.get_group_students_data(group)
    total_students = len(students)
    not_responded = total_students - total_responses
    
    status_emoji = "🟢 Активно" if status == "active" else "🔴 Завершено"
    
    text = f"🗳 **Детали голосования**\n\n"
    text += f"📅 Дата: {date_str}\n"
    text += f"⏰ Длительность: {duration} минут\n"
    text += f"📊 Статус: {status_emoji}\n\n"
    text += f"**Статистика:**\n"
    text += f"✅ Присутствуют: {present_count}\n"
    text += f"❌ Отсутствуют: {absent_count}\n"
    text += f"❓ Не ответили: {not_responded}\n"
    text += f"👥 Всего студентов: {total_students}\n\n"
    
    if responses:
        text += "**Ответы студентов:**\n"
        for user_id_str, response in responses.items():
            try:
                user_id_int = int(user_id_str)
                user_info = db.users.get(user_id_str, {})
                username = user_info.get("username", f"ID{user_id_int}")
                
                # Ищем ФИО студента в списке группы
                full_name = ""
                students = db.get_group_students_data(group)
                for student in students:
                    if student.get("username") == username:
                        full_name = student.get("full_name", "")
                        break
                
                # Если не нашли по username, пробуем найти по user_id
                if not full_name:
                    for student in students:
                        if str(student.get("user_id", "")) == user_id_str:
                            full_name = student.get("full_name", "")
                            break
                
                # Формируем отображаемое имя
                display_name = full_name if full_name else f"@{username}"
                
                status_emoji = "✅" if response.get("status") == "present" else "❌"
                reason = response.get("reason", "")
                timestamp = response.get("timestamp", "")
                
                # Форматируем время ответа
                try:
                    resp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = resp_dt.strftime("%H:%M")
                except:
                    time_str = timestamp[:5]
                
                text += f"{status_emoji} {display_name} ({time_str})"
                if reason:
                    text += f"\n   💬 {reason}"
                text += "\n"
            except:
                continue
    
    keyboard = [
        [InlineKeyboardButton("📊 Экспорт в CSV", callback_data=f"poll_export_{poll_id}")],
        [InlineKeyboardButton("🔙 К списку голосований", callback_data=f"polls_results_{group}")]
    ]
    reply_markup = with_home_button(keyboard, group)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def poll_export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экспорт результатов голосования в CSV"""
    query = update.callback_query
    await query.answer()
    poll_id = query.data.replace("poll_export_", "")
    
    poll = db.get_poll(poll_id)
    if not poll:
        await query.edit_message_text("❌ Голосование не найдено")
        return
    
    group = poll.get("group", "")
    user_id = query.from_user.id
    if not db.is_curator(user_id, group):
        await query.edit_message_text("❌ У вас нет прав для экспорта этого голосования")
        return
    
    # Создаем CSV
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow(["ФИО", "Username", "Статус", "Причина отсутствия", "Время ответа"])
    
    # Получаем всех студентов группы
    students = db.get_group_students_data(group)
    responses = poll.get("responses", {})
    
    # Создаем словарь ответов для быстрого поиска по user_id
    responses_by_user_id = {}
    for user_id_str, response in responses.items():
        responses_by_user_id[user_id_str] = response
    
    # Записываем данные
    for student in students:
        full_name = student.get("full_name", "")
        username = student.get("username", "")
        student_user_id = str(student.get("user_id", ""))
        
        if student_user_id in responses_by_user_id:
            response = responses_by_user_id[student_user_id]
            status = "Присутствует" if response.get("status") == "present" else "Отсутствует"
            reason = response.get("reason", "")
            timestamp = response.get("timestamp", "")
        else:
            status = "Не ответил"
            reason = ""
            timestamp = ""
        
        writer.writerow([full_name, username, status, reason, timestamp])
    
    csv_content = output.getvalue()
    output.close()
    
    # Отправляем файл
    filename = f"poll_{poll_id}_{group}.csv"
    file_obj = io.BytesIO(csv_content.encode('utf-8-sig'))  # BOM для корректного отображения в Excel
    
    try:
        await context.bot.send_document(
            chat_id=user_id,
            document=file_obj,
            filename=filename,
            caption=f"📊 Результаты голосования {poll_id}\nГруппа: {GROUPS[group]}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки CSV: {e}")
        await query.edit_message_text("❌ Ошибка при создании файла")

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Маршрутизирует текст: ФИО -> редактирование студентов -> импорт студентов -> голосования -> прочее"""
    handled = await handle_full_name_input(update, context)
    if handled:
        return
    handled = await handle_edit_student_text(update, context)
    if handled:
        return
    handled = await handle_import_students_text(update, context)
    if handled:
        return
    handled = await handle_poll_duration(update, context)
    if handled:
        return
    handled = await handle_absence_reason(update, context)
    if handled:
        return
    await handle_message(update, context)

def main():
    """Запуск бота"""
    # Создаем приложение
    # Настраиваем таймауты и пулинг для Render
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )
    
    # Keepalive для Render free (не даём сервису заснуть)
    async def keepalive_job(context: ContextTypes.DEFAULT_TYPE):
        try:
            url = os.getenv('KEEPALIVE_URL') or os.getenv('RENDER_EXTERNAL_URL')
            if not url:
                return
            if not url.startswith('http'):
                url = f"https://{url}"
            async with httpx.AsyncClient(timeout=10) as client:
                await client.get(url)
        except Exception:
            pass

    # Глобальный обработчик ошибок
    application.add_error_handler(on_error)
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("today", today_schedule))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("resume", resume))
    application.add_handler(CommandHandler("import_students", import_students_cmd))
    application.add_handler(CommandHandler("students", students_cmd))
    
    # Добавляем обработчики callback'ов
    application.add_handler(CallbackQueryHandler(handle_group_selection, pattern="^join_"))
    application.add_handler(CallbackQueryHandler(handle_schedule, pattern="^schedule_"))
    application.add_handler(CallbackQueryHandler(handle_announcement, pattern="^announce_"))
    application.add_handler(CallbackQueryHandler(show_stats, pattern="^stats_"))
    application.add_handler(CallbackQueryHandler(change_group, pattern="^change_group$"))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu_"))
    application.add_handler(CallbackQueryHandler(view_schedule, pattern="^view_schedule_"))
    application.add_handler(CallbackQueryHandler(view_announcements, pattern="^view_announce_"))
    application.add_handler(CallbackQueryHandler(ask_question, pattern="^ask_question_"))
    application.add_handler(CallbackQueryHandler(view_questions, pattern="^view_questions_"))
    application.add_handler(CallbackQueryHandler(answer_question_menu, pattern="^answer_question_"))
    application.add_handler(CallbackQueryHandler(select_question_for_answer, pattern="^select_question_"))
    application.add_handler(CallbackQueryHandler(cancel_question, pattern="^cancel_question_"))
    application.add_handler(CallbackQueryHandler(cancel_answer, pattern="^cancel_answer_"))
    application.add_handler(CallbackQueryHandler(today_schedule, pattern="^today_schedule_"))
    application.add_handler(CallbackQueryHandler(students_menu, pattern="^students_menu_[^_]+$"))
    application.add_handler(CallbackQueryHandler(students_import_start, pattern="^students_import_[^_]+$"))
    application.add_handler(CallbackQueryHandler(students_list, pattern="^students_list_[^_]+$"))
    application.add_handler(CallbackQueryHandler(students_delete_menu, pattern="^students_delete_[^_]+$"))
    application.add_handler(CallbackQueryHandler(students_delete_confirm, pattern="^students_delete_pick_"))
    application.add_handler(CallbackQueryHandler(students_delete_do, pattern="^students_delete_do_"))
    application.add_handler(CallbackQueryHandler(students_edit_menu, pattern="^students_edit_[^_]+$"))
    application.add_handler(CallbackQueryHandler(students_edit_ask, pattern="^students_edit_pick_"))
    
    # Polls handlers
    application.add_handler(CallbackQueryHandler(polls_menu, pattern="^polls_menu_[^_]+$"))
    application.add_handler(CallbackQueryHandler(polls_create_start, pattern="^polls_create_[^_]+$"))
    application.add_handler(CallbackQueryHandler(polls_results_menu, pattern="^polls_results_[^_]+$"))
    application.add_handler(CallbackQueryHandler(poll_view_details, pattern="^poll_view_"))
    application.add_handler(CallbackQueryHandler(poll_export_csv, pattern="^poll_export_"))
    application.add_handler(CallbackQueryHandler(student_polls_menu, pattern="^student_polls_[^_]+$"))
    application.add_handler(CallbackQueryHandler(poll_response, pattern="^poll_(present|absent)_"))
    application.add_handler(MessageHandler((filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    
    # Запускаем бота
    print("Бот запущен! Нажмите Ctrl+C для остановки.")
    # Планируем keepalive пинги каждые 10 минут
    if application.job_queue:
        application.job_queue.run_repeating(keepalive_job, interval=600, first=30)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # Для Render Web Service - открываем порт
    import os
    port = int(os.environ.get('PORT', 8080))
    
    # Запускаем бота в фоне
    import asyncio
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot is running')
        
        def log_message(self, format, *args):
            pass  # Отключаем логи HTTP сервера
    
    # Запускаем HTTP сервер в отдельном потоке
    def run_server():
        server = HTTPServer(('0.0.0.0', port), Handler)
        server.serve_forever()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Запускаем бота
    main()
