from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from utils.keyboards import Keyboards
from database.database import db_manager
from database.models import User
import logging

logger = logging.getLogger(__name__)

class MainMenuHandler:
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Register or update user in database
        await MainMenuHandler._register_user(user)
        
        # Check if there's a start parameter (e.g., post_12345)
        start_param = context.args[0] if context.args else None
        if start_param and start_param.startswith('post_'):
            post_unique_id = start_param.replace('post_', '')
            await MainMenuHandler._handle_post_open(update, context, post_unique_id)
            return
        
        # Show main menu
        await update.message.reply_text(
            "🎮 Добро пожаловать в игровой маркетплейс!\n\n"
            "Здесь вы можете безопасно покупать и продавать игровые аккаунты, "
            "предметы и валюту с гарантией сделки.\n\n"
            "Выберите действие:",
            reply_markup=Keyboards.main_menu()
        )
    
    @staticmethod
    async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle main menu selections"""
        text = update.message.text
        
        if text == "📢 Сделать объявление":
            await update.message.reply_text(
                "📢 Выберите тип объявления:",
                reply_markup=Keyboards.announcement_types()
            )
            
        elif text == "💬 Чаты":
            await MainMenuHandler._show_chats(update, context)
            
        elif text == "👤 Профиль":
            await MainMenuHandler._show_profile(update, context)
            
        elif text == "📘 FAQ":
            await MainMenuHandler._show_faq(update, context)
            
        elif text == "🛠 Поддержка":
            await MainMenuHandler._show_support(update, context)
    
    @staticmethod
    async def _register_user(telegram_user):
        """Register or update user in database"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_user.id).first()
            
            if not user:
                user = User(
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name
                )
                session.add(user)
                logger.info(f"New user registered: {telegram_user.id}")
            else:
                # Update user info
                user.username = telegram_user.username
                user.first_name = telegram_user.first_name
                user.last_name = telegram_user.last_name
    
    @staticmethod
    async def _handle_post_open(update: Update, context: ContextTypes.DEFAULT_TYPE, post_unique_id: str):
        """Handle opening a post from channel"""
        with db_manager.get_session() as session:
            from database.models import Post, Chat
            
            post = session.query(Post).filter(Post.unique_id == post_unique_id).first()
            if not post:
                await update.message.reply_text("❌ Объявление не найдено.")
                return
            
            # Check if chat already exists
            user_id = update.effective_user.id
            existing_chat = session.query(Chat).filter(
                Chat.post_id == post.id,
                Chat.user2_id == user_id
            ).first()
            
            if existing_chat:
                await update.message.reply_text(
                    f"💬 Чат уже существует для объявления #{post.unique_id}",
                    reply_markup=Keyboards.contact_seller(existing_chat.id)
                )
            else:
                # Create new chat
                new_chat = Chat(
                    post_id=post.id,
                    user1_id=post.user_id,
                    user2_id=user_id
                )
                session.add(new_chat)
                session.flush()
                
                await update.message.reply_text(
                    f"💬 Создан чат для объявления #{post.unique_id}\n"
                    f"📝 {post.title}\n\n"
                    "Нажмите кнопку ниже, чтобы связаться с продавцом:",
                    reply_markup=Keyboards.contact_seller(new_chat.id)
                )
    
    @staticmethod
    async def _show_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's chats"""
        user_id = update.effective_user.id
        
        with db_manager.get_session() as session:
            from database.models import Chat, Post
            
            # Get user's chats
            chats = session.query(Chat).join(Post).filter(
                (Chat.user1_id == user_id) | (Chat.user2_id == user_id),
                Chat.is_active == True
            ).all()
            
            if not chats:
                await update.message.reply_text(
                    "💬 У вас пока нет активных чатов.\n\n"
                    "Чтобы начать общение, откройте объявление из канала "
                    "и нажмите кнопку 'Открыть в боте'."
                )
                return
            
            # Format chats list
            message = "💬 Ваши активные чаты:\n\n"
            for chat in chats:
                status_emoji = {
                    'waiting': '⏳',
                    'active': '💬',
                    'transaction': '🤝',
                    'completed': '✅'
                }.get(chat.status.value, '💬')
                
                status_text = {
                    'waiting': 'ожидание',
                    'active': 'активный',
                    'transaction': 'сделка',
                    'completed': 'завершён'
                }.get(chat.status.value, 'активный')
                
                message += f"{status_emoji} #{chat.post.unique_id}\n"
                message += f"📝 {chat.post.title[:50]}...\n"
                message += f"📊 Статус: {status_text}\n\n"
            
            await update.message.reply_text(message)
    
    @staticmethod
    async def _show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user profile"""
        user_id = update.effective_user.id
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                await update.message.reply_text("❌ Пользователь не найден.")
                return
            
            # Calculate statistics
            from datetime import datetime, timedelta
            recent_transactions = user.total_transactions  # This would need proper calculation
            
            # Status badge
            status_badge = "✅ Хороший продавец" if user.is_verified_seller else ""
            if user.status.value == "suspicious":
                status_badge = "⚠️ Подозрительный"
            elif user.status.value == "banned":
                status_badge = "🚫 Заблокирован"
            
            # Format profile message
            display_name = user.nickname or user.first_name or "Пользователь"
            
            message = f"👤 Профиль: {display_name}\n\n"
            message += f"🤝 Количество сделок: {user.total_transactions}\n"
            message += f"💰 Сумма через гаранта: {user.total_amount:.2f} грн\n"
            message += f"⭐ Средняя оценка: {user.average_rating:.1f}/5.0\n"
            if status_badge:
                message += f"🏷 {status_badge}\n"
            message += f"\n📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}"
            
            await update.message.reply_text(message)
            
            # Show user's posts
            await MainMenuHandler._show_user_posts(update, context, user.id)
    
    @staticmethod
    async def _show_user_posts(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show user's active and inactive posts"""
        with db_manager.get_session() as session:
            from database.models import Post
            
            posts = session.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()
            
            if not posts:
                await update.message.reply_text("📝 У вас пока нет объявлений.")
                return
            
            active_posts = [p for p in posts if p.is_active]
            inactive_posts = [p for p in posts if not p.is_active]
            
            message = "📝 Мои объявления:\n\n"
            
            if active_posts:
                message += "🟢 Активные:\n"
                for post in active_posts:
                    time_left = ""
                    if post.expires_at:
                        hours_left = (post.expires_at - datetime.now()).total_seconds() / 3600
                        if hours_left > 0:
                            time_left = f" (осталось {int(hours_left)}ч)"
                    
                    price_text = ""
                    if post.price_type.value == "fixed" and post.price:
                        price_text = f" - {post.price} грн"
                    elif post.price_type.value == "negotiable":
                        price_text = " - договорная"
                    
                    message += f"#{post.unique_id} {post.title[:30]}...{price_text}{time_left}\n"
                
                message += "\n"
            
            if inactive_posts:
                message += "🔴 Неактивные:\n"
                for post in inactive_posts[:5]:  # Show only last 5
                    message += f"#{post.unique_id} {post.title[:30]}...\n"
            
            await update.message.reply_text(message)
    
    @staticmethod
    async def _show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show FAQ section"""
        faq_text = """
📘 Часто задаваемые вопросы

❓ Как продать?
1. Нажмите "📢 Сделать объявление"
2. Выберите "▶️ Сделать объявление"
3. Заполните форму и опубликуйте
4. Ждите покупателей в чатах

❓ Как купить?
1. Найдите объявление в канале
2. Нажмите "📩 Открыть в боте"
3. Свяжитесь с продавцом
4. Начните сделку с гарантом

❓ Что такое гарант?
Гарант - это система защиты сделок. Деньги блокируются до получения товара покупателем.

❓ Как оставить жалобу?
Во время сделки нажмите "🆘 Мне нужна помощь" или обратитесь в поддержку.

❓ Как получить оплату?
Укажите реквизиты UA-карты или криптокошелька при создании сделки.
        """
        
        await update.message.reply_text(faq_text)
    
    @staticmethod
    async def _show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show support options"""
        support_text = """
🛠 Поддержка

Если у вас возникли вопросы или проблемы:

📞 Свяжитесь с администратором: @admin_username
💬 Опишите вашу проблему подробно
🕐 Ответим в течение 24 часов

📋 Для быстрого решения укажите:
• Ваш ID пользователя
• Номер объявления или сделки
• Описание проблемы

⚡ Экстренные случаи:
• Мошенничество
• Технические проблемы с платежами
• Споры по сделкам

Обращайтесь в любое время!
        """
        
        await update.message.reply_text(support_text)