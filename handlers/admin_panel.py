from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from utils.keyboards import Keyboards
from database.database import db_manager
from database.models import (User, Post, Transaction, Chat, BotStatistics, 
                           AdminAction, UserStatus, TransactionStatus)
from config import Config
import logging
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import json

logger = logging.getLogger(__name__)

# Admin conversation states
(ADMIN_FIND_USER, ADMIN_BROADCAST_MESSAGE, ADMIN_MESSAGE_USER, 
 ADMIN_FIND_TRANSACTION) = range(4)

class AdminPanelHandler:
    
    @staticmethod
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main admin command - show admin panel"""
        user_id = update.effective_user.id
        
        if not Config.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав администратора.")
            return
        
        # Get quick stats
        with db_manager.get_session() as session:
            total_users = session.query(User).count()
            active_transactions = session.query(Transaction).filter(
                Transaction.status.in_([TransactionStatus.PENDING, TransactionStatus.IN_PROGRESS])
            ).count()
            today_posts = session.query(Post).filter(
                func.date(Post.created_at) == datetime.now().date()
            ).count()
        
        admin_text = f"""
🔧 **Админ-панель**

📊 **Быстрая статистика:**
👥 Всего пользователей: **{total_users}**
🤝 Активных сделок: **{active_transactions}**
📝 Постов сегодня: **{today_posts}**

Выберите действие:
        """
        
        await update.message.reply_text(
            admin_text,
            reply_markup=Keyboards.admin_main_panel(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin panel callbacks"""
        query = update.callback_query
        await query.answer()
        
        if not Config.is_admin(query.from_user.id):
            await query.edit_message_text("❌ У вас нет прав администратора.")
            return
        
        data = query.data
        
        # Main menu handlers
        if data == "admin_stats":
            await AdminPanelHandler._show_stats_menu(query, context)
        elif data == "admin_users":
            await AdminPanelHandler._show_users_menu(query, context)
        elif data == "admin_transactions":
            await AdminPanelHandler._show_transactions_menu(query, context)
        elif data == "admin_broadcast":
            await AdminPanelHandler._show_broadcast_menu(query, context)
        elif data == "admin_settings":
            await AdminPanelHandler._show_settings_menu(query, context)
        elif data == "admin_reports":
            await AdminPanelHandler._show_reports_menu(query, context)
        elif data == "admin_back_main":
            await AdminPanelHandler._show_main_panel(query, context)
        
        # Stats handlers
        elif data.startswith("admin_stats_"):
            await AdminPanelHandler._handle_stats(query, context, data)
        
        # Users handlers
        elif data.startswith("admin_users_"):
            await AdminPanelHandler._handle_users(query, context, data)
        elif data == "admin_find_user":
            await AdminPanelHandler._start_user_search(query, context)
        
        # Transactions handlers
        elif data.startswith("admin_trans_"):
            await AdminPanelHandler._handle_transactions(query, context, data)
        elif data == "admin_find_transaction":
            await AdminPanelHandler._start_transaction_search(query, context)
        
        # Broadcast handlers
        elif data.startswith("admin_broadcast_"):
            await AdminPanelHandler._handle_broadcast(query, context, data)
        
        # User management handlers
        elif data.startswith("admin_ban_") or data.startswith("admin_unban_"):
            await AdminPanelHandler._handle_user_ban(query, context, data)
        elif data.startswith("admin_suspicious_") or data.startswith("admin_unsuspicious_"):
            await AdminPanelHandler._handle_user_suspicious(query, context, data)
        elif data.startswith("admin_user_stats_"):
            await AdminPanelHandler._show_user_detailed_stats(query, context, data)
        elif data.startswith("admin_message_"):
            await AdminPanelHandler._start_user_message(query, context, data)
        
        # Transaction management handlers
        elif data.startswith("admin_verify_"):
            await AdminPanelHandler._handle_verification(query, context, data)
        elif data.startswith("admin_payout_"):
            await AdminPanelHandler._handle_payout(query, context, data)
        elif data.startswith("admin_extend_time_"):
            await AdminPanelHandler._show_time_extend_options(query, context, data)
        elif data.startswith("admin_extend_") and data.count("_") >= 3:
            await AdminPanelHandler._handle_time_extension(query, context, data)
        
        # Pagination handlers
        elif data.startswith("admin_page_"):
            await AdminPanelHandler._handle_pagination(query, context, data)
    
    @staticmethod
    async def _show_main_panel(query, context):
        """Show main admin panel"""
        # Get quick stats
        with db_manager.get_session() as session:
            total_users = session.query(User).count()
            active_transactions = session.query(Transaction).filter(
                Transaction.status.in_([TransactionStatus.PENDING, TransactionStatus.IN_PROGRESS])
            ).count()
            today_posts = session.query(Post).filter(
                func.date(Post.created_at) == datetime.now().date()
            ).count()
        
        admin_text = f"""
🔧 **Админ-панель**

📊 **Быстрая статистика:**
👥 Всего пользователей: **{total_users}**
🤝 Активных сделок: **{active_transactions}**
📝 Постов сегодня: **{today_posts}**

Выберите действие:
        """
        
        await query.edit_message_text(
            admin_text,
            reply_markup=Keyboards.admin_main_panel(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _show_stats_menu(query, context):
        """Show statistics menu"""
        await query.edit_message_text(
            "📊 **Статистика бота**\n\nВыберите период:",
            reply_markup=Keyboards.admin_stats_menu(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _show_users_menu(query, context):
        """Show users management menu"""
        await query.edit_message_text(
            "👥 **Управление пользователями**\n\nВыберите действие:",
            reply_markup=Keyboards.admin_users_menu(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _show_transactions_menu(query, context):
        """Show transactions management menu"""
        with db_manager.get_session() as session:
            pending_verification = session.query(Transaction).filter(
                Transaction.status == TransactionStatus.VERIFICATION_PENDING
            ).count()
            pending_payment = session.query(Transaction).filter(
                Transaction.status == TransactionStatus.PAYMENT_PENDING
            ).count()
            completed_pending = session.query(Transaction).filter(
                Transaction.status == TransactionStatus.COMPLETED
            ).count()
        
        text = f"""
🤝 **Управление сделками**

📊 **Текущий статус:**
⏳ Ожидают проверки: **{pending_verification}**
💰 Ожидают оплаты: **{pending_payment}**
✅ Ожидают подтверждения: **{completed_pending}**

Выберите действие:
        """
        
        await query.edit_message_text(
            text,
            reply_markup=Keyboards.admin_transactions_menu(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _show_broadcast_menu(query, context):
        """Show broadcast menu"""
        await query.edit_message_text(
            "📢 **Рассылка сообщений**\n\nВыберите аудиторию:",
            reply_markup=Keyboards.admin_broadcast_menu(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _show_settings_menu(query, context):
        """Show settings menu"""
        settings_text = f"""
⚙️ **Настройки бота**

💰 **Текущие цены:**
• Пост: {Config.POST_PRICE} грн
• Закрепление: {Config.PIN_PRICE} грн
• Продление: {Config.EXTEND_PRICE} грн
• Комиссия: {Config.ESCROW_COMMISSION*100}%

⏰ **Временные лимиты:**
• Длительность поста: {Config.POST_DURATION_HOURS}ч
• Предупреждение: {Config.WARNING_HOURS}ч
• Таймаут сделки: {Config.TRANSACTION_TIMEOUT_HOURS}ч

Выберите раздел для просмотра:
        """
        
        await query.edit_message_text(
            settings_text,
            reply_markup=Keyboards.admin_settings_menu(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _show_reports_menu(query, context):
        """Show reports menu"""
        await query.edit_message_text(
            "📈 **Отчёты**\n\nВыберите тип отчёта:",
            reply_markup=Keyboards.admin_reports_menu(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _handle_stats(query, context, data):
        """Handle statistics requests"""
        period = data.split("_")[-1]
        
        with db_manager.get_session() as session:
            today = datetime.now().date()
            
            if period == "today":
                start_date = today
                title = "Статистика за сегодня"
            elif period == "week":
                start_date = today - timedelta(days=7)
                title = "Статистика за неделю"
            elif period == "month":
                start_date = today - timedelta(days=30)
                title = "Статистика за месяц"
            elif period == "all":
                start_date = None
                title = "Общая статистика"
            elif period == "revenue":
                await AdminPanelHandler._show_revenue_stats(query, context)
                return
            
            # Calculate statistics
            if start_date:
                new_users = session.query(User).filter(User.created_at >= start_date).count()
                new_posts = session.query(Post).filter(Post.created_at >= start_date).count()
                completed_transactions = session.query(Transaction).filter(
                    and_(Transaction.completed_at >= start_date, Transaction.status == TransactionStatus.COMPLETED)
                ).count()
                revenue = session.query(func.sum(Transaction.commission)).filter(
                    and_(Transaction.completed_at >= start_date, Transaction.status == TransactionStatus.COMPLETED)
                ).scalar() or 0
            else:
                new_users = session.query(User).count()
                new_posts = session.query(Post).count()
                completed_transactions = session.query(Transaction).filter(
                    Transaction.status == TransactionStatus.COMPLETED
                ).count()
                revenue = session.query(func.sum(Transaction.commission)).filter(
                    Transaction.status == TransactionStatus.COMPLETED
                ).scalar() or 0
        
        stats_text = f"""
📊 **{title}**

👥 **Пользователи:** {new_users}
📝 **Посты:** {new_posts}
🤝 **Завершённые сделки:** {completed_transactions}
💰 **Доход:** {revenue:.2f} грн

📈 **Средний чек:** {(revenue/completed_transactions):.2f} грн (если есть сделки)
        """
        
        await query.edit_message_text(
            stats_text,
            reply_markup=Keyboards.admin_stats_menu(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _show_revenue_stats(query, context):
        """Show detailed revenue statistics"""
        with db_manager.get_session() as session:
            today = datetime.now().date()
            
            # Revenue breakdown
            commission_revenue = session.query(func.sum(Transaction.commission)).filter(
                Transaction.status == TransactionStatus.COMPLETED
            ).scalar() or 0
            
            posts_revenue = session.query(Post).count() * Config.POST_PRICE
            
            # Today's revenue
            today_commission = session.query(func.sum(Transaction.commission)).filter(
                and_(
                    func.date(Transaction.completed_at) == today,
                    Transaction.status == TransactionStatus.COMPLETED
                )
            ).scalar() or 0
            
            today_posts = session.query(Post).filter(
                func.date(Post.created_at) == today
            ).count()
            today_posts_revenue = today_posts * Config.POST_PRICE
        
        revenue_text = f"""
💰 **Детальная статистика доходов**

🎯 **Общий доход:**
• От комиссий: **{commission_revenue:.2f} грн**
• От постов: **{posts_revenue:.2f} грн**
• **Итого: {commission_revenue + posts_revenue:.2f} грн**

📅 **Сегодня:**
• От комиссий: **{today_commission:.2f} грн**
• От постов: **{today_posts_revenue:.2f} грн**
• **Итого: {today_commission + today_posts_revenue:.2f} грн**

📊 **Структура доходов:**
• Комиссии: {(commission_revenue/(commission_revenue+posts_revenue)*100):.1f}%
• Посты: {(posts_revenue/(commission_revenue+posts_revenue)*100):.1f}%
        """
        
        await query.edit_message_text(
            revenue_text,
            reply_markup=Keyboards.admin_stats_menu(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _handle_users(query, context, data):
        """Handle user management requests"""
        filter_type = data.split("_")[-1]
        page = 0  # Default page
        
        with db_manager.get_session() as session:
            if filter_type == "banned":
                users = session.query(User).filter(User.status == UserStatus.BANNED).offset(page*10).limit(10).all()
                title = "🚫 Заблокированные пользователи"
            elif filter_type == "suspicious":
                users = session.query(User).filter(User.status == UserStatus.SUSPICIOUS).offset(page*10).limit(10).all()
                title = "⚠️ Подозрительные пользователи"
            elif filter_type == "active":
                users = session.query(User).filter(
                    and_(
                        User.status == UserStatus.ACTIVE,
                        User.last_activity >= datetime.now() - timedelta(days=7)
                    )
                ).order_by(User.last_activity.desc()).offset(page*10).limit(10).all()
                title = "✅ Активные пользователи (неделя)"
            elif filter_type == "top":
                users = session.query(User).filter(
                    User.total_transactions > 0
                ).order_by(User.total_transactions.desc()).offset(page*10).limit(10).all()
                title = "🏆 Топ продавцы"
        
        if not users:
            await query.edit_message_text(
                f"{title}\n\n❌ Пользователи не найдены.",
                reply_markup=Keyboards.admin_users_menu()
            )
            return
        
        user_list = f"{title}\n\n"
        
        for i, user in enumerate(users, 1):
            status_emoji = {
                UserStatus.ACTIVE: "✅",
                UserStatus.SUSPICIOUS: "⚠️",
                UserStatus.BANNED: "🚫"
            }.get(user.status, "❓")
            
            username = f"@{user.username}" if user.username else "нет"
            user_list += f"{status_emoji} **{i}.** {user.first_name} ({username})\n"
            user_list += f"   🆔 `{user.telegram_id}` | 🤝 {user.total_transactions} сделок\n\n"
        
        # Add pagination keyboard
        total_count = session.query(User).filter(
            User.status == (UserStatus.BANNED if filter_type == "banned" else 
                          UserStatus.SUSPICIOUS if filter_type == "suspicious" else UserStatus.ACTIVE)
        ).count()
        total_pages = (total_count + 9) // 10
        
        keyboard = Keyboards.admin_pagination(f"users_{filter_type}", page, total_pages) if total_pages > 1 else Keyboards.admin_users_menu()
        
        await query.edit_message_text(
            user_list,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _start_user_search(query, context):
        """Start user search conversation"""
        await query.edit_message_text(
            "🔍 **Поиск пользователя**\n\n"
            "Отправьте Telegram ID или @username пользователя:",
            parse_mode='Markdown'
        )
        return ADMIN_FIND_USER
    
    @staticmethod
    async def handle_user_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user search input"""
        search_term = update.message.text.strip()
        
        with db_manager.get_session() as session:
            user = None
            
            if search_term.isdigit():
                # Search by Telegram ID
                user = session.query(User).filter(User.telegram_id == int(search_term)).first()
            elif search_term.startswith('@'):
                # Search by username
                username = search_term[1:]
                user = session.query(User).filter(User.username == username).first()
            
            if not user:
                await update.message.reply_text(
                    "❌ Пользователь не найден.\n\n"
                    "Попробуйте ещё раз или отправьте /cancel для отмены.",
                    reply_markup=Keyboards.admin_users_menu()
                )
                return ADMIN_FIND_USER
            
            # Show user details
            await AdminPanelHandler._show_user_details(update, context, user)
        
        return ConversationHandler.END
    
    @staticmethod
    async def _show_user_details(update, context, user):
        """Show detailed user information"""
        with db_manager.get_session() as session:
            # Get user's statistics
            posts_count = session.query(Post).filter(Post.user_id == user.id).count()
            active_posts = session.query(Post).filter(
                and_(Post.user_id == user.id, Post.is_active == True)
            ).count()
            
            seller_transactions = session.query(Transaction).filter(Transaction.seller_id == user.id).count()
            buyer_transactions = session.query(Transaction).filter(Transaction.buyer_id == user.id).count()
            
            # Recent admin actions
            recent_actions = session.query(AdminAction).filter(
                AdminAction.target_user_id == user.id
            ).order_by(AdminAction.created_at.desc()).limit(3).all()
            
            status_emoji = {
                UserStatus.ACTIVE: "✅",
                UserStatus.SUSPICIOUS: "⚠️",
                UserStatus.BANNED: "🚫"
            }.get(user.status, "❓")
            
            user_info = f"""
👤 **Информация о пользователе**

🆔 **ID:** `{user.telegram_id}`
👤 **Имя:** {user.first_name} {user.last_name or ''}
📱 **Username:** @{user.username or 'нет'}
🏷 **Ник:** {user.nickname or 'нет'}

📊 **Статус:** {status_emoji} {user.status.value}
⭐ **Рейтинг:** {user.average_rating:.1f}/5.0
🏆 **Проверенный:** {'✅' if user.is_verified_seller else '❌'}

📈 **Статистика:**
• Всего сделок: **{user.total_transactions}**
• Как продавец: **{seller_transactions}**
• Как покупатель: **{buyer_transactions}**
• Общая сумма: **{user.total_amount:.2f} грн**
• Объявлений: **{posts_count}** (активных: **{active_posts}**)
• Предупреждений: **{user.warnings_count}**

📅 **Даты:**
• Регистрация: {user.created_at.strftime('%d.%m.%Y %H:%M')}
• Последняя активность: {user.last_activity.strftime('%d.%m.%Y %H:%M') if user.last_activity else 'неизвестно'}
            """
            
            if recent_actions:
                user_info += "\n🔧 **Последние действия админов:**\n"
                for action in recent_actions:
                    user_info += f"• {action.action_type} - {action.created_at.strftime('%d.%m %H:%M')}\n"
        
        keyboard = Keyboards.admin_user_management(user.id, user.status.value)
        
        if hasattr(update, 'message'):
            await update.message.reply_text(user_info, reply_markup=keyboard, parse_mode='Markdown')
        else:
            await update.edit_message_text(user_info, reply_markup=keyboard, parse_mode='Markdown')
    
    @staticmethod
    async def _handle_user_ban(query, context, data):
        """Handle user ban/unban"""
        action = "ban" if "ban_" in data and "unban_" not in data else "unban"
        user_id = int(data.split("_")[-1])
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                await query.edit_message_text("❌ Пользователь не найден.")
                return
            
            if action == "ban":
                user.status = UserStatus.BANNED
                message = f"🚫 Пользователь {user.first_name} заблокирован."
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text="🚫 Ваш аккаунт заблокирован администратором.\n\n"
                             "Для разблокировки обратитесь в поддержку."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify banned user: {e}")
            else:
                user.status = UserStatus.ACTIVE
                user.warnings_count = 0
                message = f"✅ Пользователь {user.first_name} разблокирован."
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text="✅ Ваш аккаунт разблокирован!\n\n"
                             "Теперь вы можете пользоваться всеми функциями бота."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify unbanned user: {e}")
            
            # Log admin action
            admin_action = AdminAction(
                admin_id=query.from_user.id,
                target_user_id=user_id,
                action_type=f'{action}_user',
                reason=f'{"Заблокирован" if action == "ban" else "Разблокирован"} администратором'
            )
            session.add(admin_action)
        
        await query.edit_message_text(
            message,
            reply_markup=Keyboards.admin_user_management(user_id, user.status.value)
        )
    
    @staticmethod
    async def _handle_user_suspicious(query, context, data):
        """Handle marking user as suspicious"""
        action = "suspicious" if "suspicious_" in data and "unsuspicious_" not in data else "unsuspicious"
        user_id = int(data.split("_")[-1])
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                await query.edit_message_text("❌ Пользователь не найден.")
                return
            
            if action == "suspicious":
                user.status = UserStatus.SUSPICIOUS
                message = f"⚠️ Пользователь {user.first_name} помечен как подозрительный."
            else:
                user.status = UserStatus.ACTIVE
                message = f"✅ С пользователя {user.first_name} снята пометка 'подозрительный'."
            
            # Log admin action
            admin_action = AdminAction(
                admin_id=query.from_user.id,
                target_user_id=user_id,
                action_type=f'mark_{action}',
                reason=f'{"Помечен как подозрительный" if action == "suspicious" else "Снята пометка подозрительный"}'
            )
            session.add(admin_action)
        
        await query.edit_message_text(
            message,
            reply_markup=Keyboards.admin_user_management(user_id, user.status.value)
        )
    
    @staticmethod
    async def cancel_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel admin conversation"""
        await update.message.reply_text(
            "❌ Действие отменено.",
            reply_markup=Keyboards.admin_main_panel()
        )
        return ConversationHandler.END
    
    # Additional admin methods for missing functionality
    @staticmethod
    async def _start_transaction_search(query, context):
        """Start transaction search conversation"""
        await query.edit_message_text(
            "🔍 **Поиск сделки**\n\n"
            "Отправьте ID сделки:",
            parse_mode='Markdown'
        )
        return ADMIN_FIND_TRANSACTION
    
    @staticmethod
    async def handle_transaction_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle transaction search input"""
        try:
            transaction_id = int(update.message.text.strip())
            
            with db_manager.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                
                if not transaction:
                    await update.message.reply_text(
                        "❌ Сделка не найдена.\n\n"
                        "Попробуйте ещё раз или отправьте /cancel для отмены."
                    )
                    return ADMIN_FIND_TRANSACTION
                
                # Show transaction details
                await AdminPanelHandler._show_transaction_details(update, context, transaction)
            
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат ID сделки.\n\n"
                "Введите числовой ID сделки:"
            )
            return ADMIN_FIND_TRANSACTION
        
        return ConversationHandler.END
    
    @staticmethod
    async def _show_transaction_details(update, context, transaction):
        """Show detailed transaction information"""
        with db_manager.get_session() as session:
            seller = session.query(User).filter(User.id == transaction.seller_id).first()
            buyer = session.query(User).filter(User.id == transaction.buyer_id).first()
            
            status_emoji = {
                TransactionStatus.PENDING: "⏳",
                TransactionStatus.PAYMENT_PENDING: "💰",
                TransactionStatus.VERIFICATION_PENDING: "🎥",
                TransactionStatus.IN_PROGRESS: "🤝",
                TransactionStatus.COMPLETED: "✅",
                TransactionStatus.CANCELLED: "❌",
                TransactionStatus.DISPUTED: "⚖️"
            }.get(transaction.status, "❓")
            
            transaction_info = f"""
🤝 **Детали сделки #{transaction.id}**

📊 **Статус:** {status_emoji} {transaction.status.value}
💰 **Сумма:** {transaction.amount:.2f} грн
🏦 **Комиссия:** {transaction.commission:.2f} грн
👤 **Плательщик комиссии:** {transaction.commission_payer}

👥 **Участники:**
• **Продавец:** {seller.first_name} (@{seller.username or 'нет'})
• **Покупатель:** {buyer.first_name} (@{buyer.username or 'нет'})

💳 **Оплата:**
• **Метод:** {transaction.payment_method}
• **Проверен:** {'✅' if transaction.is_verified else '❌'}

📅 **Даты:**
• **Создана:** {transaction.created_at.strftime('%d.%m.%Y %H:%M')}
• **Дедлайн оплаты:** {transaction.payment_deadline.strftime('%d.%m.%Y %H:%M') if transaction.payment_deadline else 'нет'}
• **Дедлайн завершения:** {transaction.completion_deadline.strftime('%d.%m.%Y %H:%M') if transaction.completion_deadline else 'нет'}
• **Завершена:** {transaction.completed_at.strftime('%d.%m.%Y %H:%M') if transaction.completed_at else 'нет'}
            """
            
            keyboard = Keyboards.admin_transaction_management(transaction.id, transaction.status.value)
            
            if hasattr(update, 'message'):
                await update.message.reply_text(transaction_info, reply_markup=keyboard, parse_mode='Markdown')
            else:
                await update.edit_message_text(transaction_info, reply_markup=keyboard, parse_mode='Markdown')
    
    @staticmethod
    async def _handle_transactions(query, context, data):
        """Handle transaction management requests"""
        filter_type = data.split("_")[-1]
        
        with db_manager.get_session() as session:
            if filter_type == "pending":
                transactions = session.query(Transaction).filter(
                    Transaction.status == TransactionStatus.VERIFICATION_PENDING
                ).order_by(Transaction.created_at.desc()).limit(10).all()
                title = "⏳ Ожидающие проверки"
            elif filter_type == "payment":
                transactions = session.query(Transaction).filter(
                    Transaction.status == TransactionStatus.PAYMENT_PENDING
                ).order_by(Transaction.created_at.desc()).limit(10).all()
                title = "💰 Ожидающие оплаты"
            elif filter_type == "completed":
                transactions = session.query(Transaction).filter(
                    Transaction.status == TransactionStatus.COMPLETED
                ).order_by(Transaction.completed_at.desc()).limit(10).all()
                title = "✅ Завершённые"
            elif filter_type == "cancelled":
                transactions = session.query(Transaction).filter(
                    Transaction.status == TransactionStatus.CANCELLED
                ).order_by(Transaction.created_at.desc()).limit(10).all()
                title = "❌ Отменённые"
        
        if not transactions:
            await query.edit_message_text(
                f"{title}\n\n❌ Сделки не найдены.",
                reply_markup=Keyboards.admin_transactions_menu()
            )
            return
        
        transactions_text = f"{title}\n\n"
        
        for i, transaction in enumerate(transactions, 1):
            seller = session.query(User).filter(User.id == transaction.seller_id).first()
            buyer = session.query(User).filter(User.id == transaction.buyer_id).first()
            
            transactions_text += f"**{i}.** ID: {transaction.id}\n"
            transactions_text += f"💰 {transaction.amount:.2f} грн\n"
            transactions_text += f"👤 {seller.first_name} → {buyer.first_name}\n"
            transactions_text += f"📅 {transaction.created_at.strftime('%d.%m %H:%M')}\n\n"
        
        await query.edit_message_text(
            transactions_text,
            reply_markup=Keyboards.admin_transactions_menu(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _handle_broadcast(query, context, data):
        """Handle broadcast requests"""
        broadcast_type = data.split("_")[-1]
        
        await query.edit_message_text(
            f"📢 **Рассылка сообщения**\n\n"
            f"Аудитория: {broadcast_type}\n\n"
            "Отправьте текст сообщения для рассылки:",
            parse_mode='Markdown'
        )
        
        context.user_data['broadcast_type'] = broadcast_type
        return ADMIN_BROADCAST_MESSAGE
    
    @staticmethod
    async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast message input"""
        message_text = update.message.text
        broadcast_type = context.user_data.get('broadcast_type', 'all')
        
        with db_manager.get_session() as session:
            # Get target users based on broadcast type
            if broadcast_type == "all":
                users = session.query(User).all()
                target_desc = "всем пользователям"
            elif broadcast_type == "active":
                users = session.query(User).filter(
                    User.status == UserStatus.ACTIVE,
                    User.last_activity >= datetime.now() - timedelta(days=7)
                ).all()
                target_desc = "активным пользователям"
            elif broadcast_type == "sellers":
                users = session.query(User).filter(
                    User.total_transactions > 0
                ).order_by(User.total_transactions.desc()).limit(100).all()
                target_desc = "топ продавцам"
            else:
                users = session.query(User).filter(User.status == UserStatus.ACTIVE).all()
                target_desc = "активным пользователям"
            
            sent_count = 0
            failed_count = 0
            
            status_message = await update.message.reply_text(
                f"📢 Начинаю рассылку {target_desc}...\n"
                f"Всего получателей: {len(users)}"
            )
            
            for user in users:
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text=f"📢 **Сообщение от администрации:**\n\n{message_text}",
                        parse_mode='Markdown'
                    )
                    sent_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send broadcast to {user.telegram_id}: {e}")
            
            # Log admin action
            admin_action = AdminAction(
                admin_id=update.effective_user.id,
                action_type='broadcast',
                reason=f'Рассылка {target_desc}: {message_text[:50]}...',
                details=json.dumps({
                    'sent': sent_count,
                    'failed': failed_count,
                    'type': broadcast_type,
                    'message': message_text
                })
            )
            session.add(admin_action)
        
        await status_message.edit_text(
            f"📢 **Рассылка завершена!**\n\n"
            f"✅ Отправлено: **{sent_count}**\n"
            f"❌ Ошибки: **{failed_count}**\n"
            f"🎯 Аудитория: {target_desc}",
            reply_markup=Keyboards.admin_main_panel(),
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END
    
    @staticmethod
    async def _show_user_detailed_stats(query, context, data):
        """Show detailed user statistics"""
        user_id = int(data.split("_")[-1])
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                await query.edit_message_text("❌ Пользователь не найден.")
                return
            
            # Get detailed statistics
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Transaction stats
            total_as_seller = session.query(Transaction).filter(Transaction.seller_id == user_id).count()
            total_as_buyer = session.query(Transaction).filter(Transaction.buyer_id == user_id).count()
            
            completed_as_seller = session.query(Transaction).filter(
                and_(Transaction.seller_id == user_id, Transaction.status == TransactionStatus.COMPLETED)
            ).count()
            
            # Revenue generated for platform
            revenue_generated = session.query(func.sum(Transaction.commission)).filter(
                and_(Transaction.seller_id == user_id, Transaction.status == TransactionStatus.COMPLETED)
            ).scalar() or 0
            
            # Recent activity
            recent_posts = session.query(Post).filter(
                and_(Post.user_id == user_id, Post.created_at >= week_ago)
            ).count()
            
            recent_transactions = session.query(Transaction).filter(
                and_(
                    (Transaction.seller_id == user_id) | (Transaction.buyer_id == user_id),
                    Transaction.created_at >= week_ago
                )
            ).count()
            
            stats_text = f"""
📊 **Детальная статистика**
👤 **{user.first_name}**

🤝 **СДЕЛКИ:**
• Как продавец: **{total_as_seller}**
• Как покупатель: **{total_as_buyer}**
• Успешно завершено: **{completed_as_seller}**
• Успешность: **{(completed_as_seller/total_as_seller*100) if total_as_seller > 0 else 0:.1f}%**

💰 **ДОХОД ПЛАТФОРМЕ:**
• Комиссий сгенерировано: **{revenue_generated:.2f} грн**

📈 **АКТИВНОСТЬ (неделя):**
• Новых объявлений: **{recent_posts}**
• Новых сделок: **{recent_transactions}**

⚠️ **БЕЗОПАСНОСТЬ:**
• Предупреждений: **{user.warnings_count}**
• Статус: **{user.status.value}**
            """
            
            await query.edit_message_text(
                stats_text,
                reply_markup=Keyboards.admin_user_management(user_id, user.status.value),
                parse_mode='Markdown'
            )
    
    @staticmethod
    async def _start_user_message(query, context, data):
        """Start sending message to user"""
        user_id = int(data.split("_")[-1])
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                await query.edit_message_text("❌ Пользователь не найден.")
                return
            
            await query.edit_message_text(
                f"💬 **Отправка сообщения пользователю**\n\n"
                f"👤 {user.first_name} (@{user.username or 'нет'})\n\n"
                "Введите текст сообщения:",
                parse_mode='Markdown'
            )
            
            context.user_data['message_target_user_id'] = user_id
            return ADMIN_MESSAGE_USER
    
    @staticmethod
    async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin message to user"""
        user_id = context.user_data.get('message_target_user_id')
        message_text = update.message.text
        
        if not user_id:
            await update.message.reply_text("❌ Ошибка: пользователь не найден.")
            return ConversationHandler.END
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                await update.message.reply_text("❌ Пользователь не найден.")
                return ConversationHandler.END
            
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"📬 **Сообщение от администрации:**\n\n{message_text}",
                    parse_mode='Markdown'
                )
                
                # Log admin action
                admin_action = AdminAction(
                    admin_id=update.effective_user.id,
                    target_user_id=user_id,
                    action_type='send_message',
                    reason=f'Отправлено сообщение: {message_text[:50]}...'
                )
                session.add(admin_action)
                
                await update.message.reply_text(
                    f"✅ Сообщение отправлено пользователю {user.first_name}",
                    reply_markup=Keyboards.admin_main_panel()
                )
                
            except Exception as e:
                logger.error(f"Failed to send admin message to user {user.telegram_id}: {e}")
                await update.message.reply_text(
                    f"❌ Не удалось отправить сообщение пользователю {user.first_name}.\n"
                    "Возможно, пользователь заблокировал бота.",
                    reply_markup=Keyboards.admin_main_panel()
                )
        
        return ConversationHandler.END
    
    @staticmethod
    async def _handle_verification(query, context, data):
        """Handle verification approval/rejection"""
        action = data.split("_")[1]  # approve or reject
        transaction_id = int(data.split("_")[-1])
        
        with db_manager.get_session() as session:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            
            if not transaction:
                await query.edit_message_text("❌ Сделка не найдена.")
                return
            
            if action == "approve":
                transaction.status = TransactionStatus.IN_PROGRESS
                transaction.is_verified = True
                message = f"✅ Проверка продавца подтверждена для сделки #{transaction_id}"
                
                # Start transaction phase
                from handlers.escrow_system import EscrowHandler
                await EscrowHandler._start_transaction_phase(context, transaction)
                
            else:  # reject
                transaction.status = TransactionStatus.CANCELLED
                message = f"❌ Проверка продавца отклонена для сделки #{transaction_id}"
                
                # Notify parties
                from handlers.escrow_system import EscrowHandler
                await EscrowHandler._notify_transaction_cancelled(
                    context, transaction, "Проверка продавца не пройдена"
                )
            
            await query.edit_message_text(
                message,
                reply_markup=Keyboards.admin_transactions_menu()
            )
    
    @staticmethod
    async def _handle_payout(query, context, data):
        """Handle transaction payout"""
        transaction_id = int(data.split("_")[-1])
        
        with db_manager.get_session() as session:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            
            if not transaction:
                await query.edit_message_text("❌ Сделка не найдена.")
                return
            
            # Process payout
            from handlers.escrow_system import EscrowHandler
            await EscrowHandler._process_seller_payment(context, transaction)
            await EscrowHandler._start_rating_process(context, transaction)
            
            await query.edit_message_text(
                f"✅ Выплата по сделке #{transaction_id} обработана!",
                reply_markup=Keyboards.admin_transactions_menu()
            )
    
    @staticmethod
    async def _show_time_extend_options(query, context, data):
        """Show time extension options"""
        transaction_id = int(data.split("_")[-1])
        
        await query.edit_message_text(
            f"⏰ **Продление времени сделки #{transaction_id}**\n\n"
            "Выберите на сколько продлить:",
            reply_markup=Keyboards.admin_time_extend_options(transaction_id),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def _handle_time_extension(query, context, data):
        """Handle time extension"""
        parts = data.split("_")
        hours = int(parts[2][:-1])  # Remove 'h' suffix
        transaction_id = int(parts[3])
        
        with db_manager.get_session() as session:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            
            if not transaction:
                await query.edit_message_text("❌ Сделка не найдена.")
                return
            
            # Extend completion deadline
            if transaction.completion_deadline:
                transaction.completion_deadline += timedelta(hours=hours)
            else:
                transaction.completion_deadline = datetime.now() + timedelta(hours=hours)
            
            await query.edit_message_text(
                f"✅ Время сделки #{transaction_id} продлено на {hours} часов",
                reply_markup=Keyboards.admin_transactions_menu()
            )
    
    @staticmethod
    async def _handle_pagination(query, context, data):
        """Handle pagination for admin lists"""
        parts = data.split("_")
        data_type = parts[2]
        page = int(parts[3])
        
        # Redirect to appropriate handler with new page
        if data_type.startswith("users"):
            filter_type = data_type.split("_")[1] if "_" in data_type else "active"
            await AdminPanelHandler._handle_users(query, context, f"admin_users_{filter_type}")
        elif data_type.startswith("trans"):
            filter_type = data_type.split("_")[1] if "_" in data_type else "pending"
            await AdminPanelHandler._handle_transactions(query, context, f"admin_trans_{filter_type}")