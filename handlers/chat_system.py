from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from utils.keyboards import Keyboards
from database.database import db_manager
from database.models import Chat, Post, Message, User, AntiSpamLog, ChatStatus
from config import Config
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatSystemHandler:
    
    @staticmethod
    async def handle_contact_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle contact seller button click"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("contact_"):
            chat_id = int(query.data.split("_")[1])
            
            with db_manager.get_session() as session:
                chat = session.query(Chat).filter(Chat.id == chat_id).first()
                
                if not chat:
                    await query.edit_message_text("❌ Чат не найден.")
                    return
                
                # Update chat status to active
                chat.status = ChatStatus.ACTIVE
                chat.last_message_at = datetime.now()
                
                # Send welcome message
                welcome_text = f"💬 Чат открыт!\n\n"
                welcome_text += f"📝 Объявление: #{chat.post.unique_id}\n"
                welcome_text += f"📋 {chat.post.title}\n\n"
                welcome_text += "Теперь вы можете общаться с продавцом. "
                welcome_text += "Все сообщения будут переданы через бота."
                
                await query.edit_message_text(
                    welcome_text,
                    reply_markup=Keyboards.chat_actions(chat_id)
                )
                
                # Notify seller about new chat
                await ChatSystemHandler._notify_seller_new_chat(context, chat)
    
    @staticmethod
    async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages in active chats"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check if user has active chats
        with db_manager.get_session() as session:
            active_chats = session.query(Chat).filter(
                ((Chat.user1_id == user_id) | (Chat.user2_id == user_id)),
                Chat.status == ChatStatus.ACTIVE,
                Chat.is_active == True
            ).all()
            
            if not active_chats:
                return  # Not in any active chat
            
            # If user has multiple active chats, use the most recent one
            # In production, you might want to implement chat selection
            current_chat = max(active_chats, key=lambda c: c.last_message_at)
            
            # Check for spam
            if await ChatSystemHandler._check_spam(update, context, message_text, user_id):
                return
            
            # Save message to database
            message = Message(
                chat_id=current_chat.id,
                sender_id=session.query(User).filter(User.telegram_id == user_id).first().id,
                message_text=message_text,
                message_type='text'
            )
            session.add(message)
            
            # Update chat timestamp
            current_chat.last_message_at = datetime.now()
            
            # Forward message to other participant
            other_user_id = current_chat.user1_id if current_chat.user2_id == session.query(User).filter(User.telegram_id == user_id).first().id else current_chat.user2_id
            other_user = session.query(User).filter(User.id == other_user_id).first()
            
            if other_user:
                try:
                    # Send auto-response on first message
                    sender = session.query(User).filter(User.telegram_id == user_id).first()
                    if not ChatSystemHandler._has_previous_messages(session, current_chat.id, sender.id):
                        await context.bot.send_message(
                            chat_id=user_id,
                            text="📨 Сообщение отправлено, ожидайте ответа."
                        )
                    
                    # Forward to recipient
                    forward_text = f"💬 Сообщение в чате #{current_chat.post.unique_id}:\n\n{message_text}"
                    await context.bot.send_message(
                        chat_id=other_user.telegram_id,
                        text=forward_text,
                        reply_markup=Keyboards.chat_actions(current_chat.id)
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to forward message: {e}")
    
    @staticmethod
    async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages in chats"""
        user_id = update.effective_user.id
        photo_file_id = update.message.photo[-1].file_id
        caption = update.message.caption or ""
        
        with db_manager.get_session() as session:
            active_chats = session.query(Chat).filter(
                ((Chat.user1_id == user_id) | (Chat.user2_id == user_id)),
                Chat.status == ChatStatus.ACTIVE,
                Chat.is_active == True
            ).all()
            
            if not active_chats:
                return
            
            current_chat = max(active_chats, key=lambda c: c.last_message_at)
            
            # Check for spam in caption
            if caption and await ChatSystemHandler._check_spam(update, context, caption, user_id):
                return
            
            # Save message to database
            message = Message(
                chat_id=current_chat.id,
                sender_id=session.query(User).filter(User.telegram_id == user_id).first().id,
                message_text=caption,
                message_type='photo',
                file_id=photo_file_id
            )
            session.add(message)
            
            # Update chat timestamp
            current_chat.last_message_at = datetime.now()
            
            # Forward photo to other participant
            other_user_id = current_chat.user1_id if current_chat.user2_id == session.query(User).filter(User.telegram_id == user_id).first().id else current_chat.user2_id
            other_user = session.query(User).filter(User.id == other_user_id).first()
            
            if other_user:
                try:
                    forward_caption = f"💬 Фото в чате #{current_chat.post.unique_id}"
                    if caption:
                        forward_caption += f":\n\n{caption}"
                    
                    await context.bot.send_photo(
                        chat_id=other_user.telegram_id,
                        photo=photo_file_id,
                        caption=forward_caption,
                        reply_markup=Keyboards.chat_actions(current_chat.id)
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to forward photo: {e}")
    
    @staticmethod
    async def handle_start_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle start transaction button"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("start_transaction_"):
            chat_id = int(query.data.split("_")[2])
            
            with db_manager.get_session() as session:
                chat = session.query(Chat).filter(Chat.id == chat_id).first()
                
                if not chat:
                    await query.edit_message_text("❌ Чат не найден.")
                    return
                
                # Check if transaction already exists
                if chat.transactions:
                    await query.edit_message_text(
                        "⚠️ Сделка для этого чата уже существует.",
                        reply_markup=Keyboards.chat_actions(chat_id)
                    )
                    return
                
                # Start escrow process
                from handlers.escrow_system import EscrowHandler
                await EscrowHandler.initiate_transaction(query, context, chat_id)
    
    @staticmethod
    async def handle_close_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle close chat button"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("close_chat_"):
            chat_id = int(query.data.split("_")[2])
            
            with db_manager.get_session() as session:
                chat = session.query(Chat).filter(Chat.id == chat_id).first()
                
                if not chat:
                    await query.edit_message_text("❌ Чат не найден.")
                    return
                
                # Check if there's an active transaction
                active_transaction = any(t.status.value in ['pending', 'payment_pending', 'in_progress'] for t in chat.transactions)
                
                if active_transaction:
                    await query.edit_message_text(
                        "⚠️ Нельзя закрыть чат с активной сделкой.",
                        reply_markup=Keyboards.chat_actions(chat_id)
                    )
                    return
                
                # Close chat
                chat.is_active = False
                chat.status = ChatStatus.COMPLETED
                
                await query.edit_message_text(
                    "✅ Чат закрыт.\n\n"
                    "Спасибо за использование нашего сервиса!"
                )
    
    @staticmethod
    async def _check_spam(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str, user_id: int) -> bool:
        """Check message for spam keywords"""
        message_lower = message_text.lower()
        triggered_keywords = []
        
        # Check for spam keywords
        for keyword in Config.SPAM_KEYWORDS:
            if keyword.lower() in message_lower:
                triggered_keywords.append(keyword)
        
        # Check for @ mentions (potential contacts)
        if '@' in message_text and not message_text.startswith('/'):
            triggered_keywords.append('@-mention')
        
        # Check for phone patterns
        phone_pattern = r'(\+?\d{1,4}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        if re.search(phone_pattern, message_text):
            triggered_keywords.append('phone-pattern')
        
        if triggered_keywords:
            await ChatSystemHandler._handle_spam_detection(update, context, message_text, user_id, triggered_keywords)
            return True
        
        return False
    
    @staticmethod
    async def _handle_spam_detection(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   message_text: str, user_id: int, keywords: list):
        """Handle detected spam"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                return
            
            # Log spam attempt
            spam_log = AntiSpamLog(
                user_id=user.id,
                message_text=message_text,
                triggered_keywords=', '.join(keywords),
                action_taken='warning'
            )
            session.add(spam_log)
            
            # Increase warning count
            user.warnings_count += 1
            
            # Determine action based on warning count
            if user.warnings_count >= 3:
                # Temporary ban
                from database.models import UserStatus
                user.status = UserStatus.BANNED
                spam_log.action_taken = 'banned'
                
                await update.message.reply_text(
                    "🚫 Вы временно заблокированы за попытки обойти систему гарантии.\n\n"
                    "Администратор рассмотрит ваш случай."
                )
                
                # Notify moderators
                await ChatSystemHandler._notify_moderators_spam(context, user, message_text, keywords, 'banned')
                
            else:
                await update.message.reply_text(
                    f"⚠️ Обнаружена попытка обойти систему гарантии!\n\n"
                    f"Предупреждение {user.warnings_count}/3\n"
                    "Все сделки должны проходить через бота для вашей безопасности."
                )
                
                # Notify moderators
                await ChatSystemHandler._notify_moderators_spam(context, user, message_text, keywords, 'warning')
    
    @staticmethod
    async def _notify_moderators_spam(context: ContextTypes.DEFAULT_TYPE, user, message_text: str, 
                                    keywords: list, action: str):
        """Notify moderators about spam detection"""
        try:
            notification = f"🚨 Обнаружен спам!\n\n"
            notification += f"👤 Пользователь: {user.first_name} (@{user.username or 'нет'})\n"
            notification += f"🆔 ID: {user.telegram_id}\n"
            notification += f"📝 Сообщение: {message_text[:200]}...\n"
            notification += f"🚩 Триггеры: {', '.join(keywords)}\n"
            notification += f"⚡ Действие: {action}\n"
            notification += f"⚠️ Предупреждений: {user.warnings_count}"
            
            await context.bot.send_message(
                chat_id=Config.MODERATOR_GROUP_ID,
                text=notification,
                reply_markup=Keyboards.admin_user_actions(user.id)
            )
            
        except Exception as e:
            logger.error(f"Failed to notify moderators: {e}")
    
    @staticmethod
    async def _notify_seller_new_chat(context: ContextTypes.DEFAULT_TYPE, chat):
        """Notify seller about new chat"""
        try:
            seller = chat.user1  # Post author
            buyer = chat.user2   # Interested user
            
            notification = f"💬 Новый чат!\n\n"
            notification += f"📝 Объявление: #{chat.post.unique_id}\n"
            notification += f"📋 {chat.post.title}\n"
            notification += f"👤 Покупатель: {buyer.first_name}\n\n"
            notification += "Кто-то интересуется вашим объявлением!"
            
            await context.bot.send_message(
                chat_id=seller.telegram_id,
                text=notification,
                reply_markup=Keyboards.chat_actions(chat.id)
            )
            
        except Exception as e:
            logger.error(f"Failed to notify seller: {e}")
    
    @staticmethod
    def _has_previous_messages(session, chat_id: int, sender_id: int) -> bool:
        """Check if user has sent messages in this chat before"""
        return session.query(Message).filter(
            Message.chat_id == chat_id,
            Message.sender_id == sender_id
        ).first() is not None
    
    @staticmethod
    async def show_chat_history(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
        """Show chat message history"""
        with db_manager.get_session() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            
            if not chat:
                await update.message.reply_text("❌ Чат не найден.")
                return
            
            # Check if user is participant
            user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
            if user.id not in [chat.user1_id, chat.user2_id]:
                await update.message.reply_text("❌ У вас нет доступа к этому чату.")
                return
            
            # Get recent messages
            messages = session.query(Message).filter(
                Message.chat_id == chat_id
            ).order_by(Message.created_at.desc()).limit(20).all()
            
            if not messages:
                await update.message.reply_text("💬 В этом чате пока нет сообщений.")
                return
            
            # Format message history
            history_text = f"💬 История чата #{chat.post.unique_id}\n\n"
            
            for msg in reversed(messages):  # Show oldest first
                sender = session.query(User).filter(User.id == msg.sender_id).first()
                sender_name = sender.first_name if sender else "Пользователь"
                
                timestamp = msg.created_at.strftime("%d.%m %H:%M")
                
                if msg.message_type == 'photo':
                    history_text += f"📸 {sender_name} ({timestamp}): [Фото]"
                    if msg.message_text:
                        history_text += f" {msg.message_text[:50]}..."
                    history_text += "\n"
                else:
                    history_text += f"💬 {sender_name} ({timestamp}): {msg.message_text[:100]}...\n"
                
                history_text += "\n"
            
            await update.message.reply_text(
                history_text,
                reply_markup=Keyboards.chat_actions(chat_id)
            )
    
    @staticmethod
    async def get_user_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get user's chat list with detailed info"""
        user_id = update.effective_user.id
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            if not user:
                return []
            
            # Get all chats where user participates
            chats = session.query(Chat).join(Post).filter(
                (Chat.user1_id == user.id) | (Chat.user2_id == user.id)
            ).order_by(Chat.last_message_at.desc()).all()
            
            chat_info = []
            for chat in chats:
                # Get last message
                last_message = session.query(Message).filter(
                    Message.chat_id == chat.id
                ).order_by(Message.created_at.desc()).first()
                
                # Get other participant
                other_user_id = chat.user1_id if chat.user2_id == user.id else chat.user2_id
                other_user = session.query(User).filter(User.id == other_user_id).first()
                
                chat_info.append({
                    'chat_id': chat.id,
                    'post_unique_id': chat.post.unique_id,
                    'post_title': chat.post.title,
                    'status': chat.status.value,
                    'other_user_name': other_user.first_name if other_user else 'Пользователь',
                    'last_message': last_message.message_text[:50] + "..." if last_message and last_message.message_text else "Нет сообщений",
                    'last_message_time': chat.last_message_at,
                    'is_active': chat.is_active
                })
            
            return chat_info