from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
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

class AdminPanelHandler:
    
    @staticmethod
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main admin command"""
        user_id = update.effective_user.id
        
        if not Config.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав администратора.")
            return
        
        admin_text = """
🔧 Панель администратора

Доступные команды:
/stats - Статистика бота
/users - Управление пользователями
/transactions - Управление сделками
/broadcast - Рассылка сообщений
/settings - Настройки бота

📊 Быстрая статистика:
        """
        
        # Add quick stats
        with db_manager.get_session() as session:
            total_users = session.query(User).count()
            active_transactions = session.query(Transaction).filter(
                Transaction.status.in_([TransactionStatus.PENDING, TransactionStatus.IN_PROGRESS])
            ).count()
            today_posts = session.query(Post).filter(
                func.date(Post.created_at) == datetime.now().date()
            ).count()
            
            admin_text += f"\n👥 Всего пользователей: {total_users}"
            admin_text += f"\n🤝 Активных сделок: {active_transactions}"
            admin_text += f"\n📝 Постов сегодня: {today_posts}"
        
        await update.message.reply_text(admin_text)
    
    @staticmethod
    async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed statistics"""
        user_id = update.effective_user.id
        
        if not Config.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав администратора.")
            return
        
        with db_manager.get_session() as session:
            # Calculate various statistics
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # User statistics
            total_users = session.query(User).count()
            new_users_today = session.query(User).filter(
                func.date(User.created_at) == today
            ).count()
            new_users_week = session.query(User).filter(
                User.created_at >= week_ago
            ).count()
            new_users_month = session.query(User).filter(
                User.created_at >= month_ago
            ).count()
            
            # Transaction statistics
            total_transactions = session.query(Transaction).count()
            completed_transactions = session.query(Transaction).filter(
                Transaction.status == TransactionStatus.COMPLETED
            ).count()
            cancelled_transactions = session.query(Transaction).filter(
                Transaction.status == TransactionStatus.CANCELLED
            ).count()
            
            # Calculate transaction success rate
            success_rate = (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0
            
            # Revenue statistics
            total_revenue = session.query(func.sum(Transaction.commission)).filter(
                Transaction.status == TransactionStatus.COMPLETED
            ).scalar() or 0
            
            # Post statistics
            total_posts = session.query(Post).count()
            active_posts = session.query(Post).filter(Post.is_active == True).count()
            
            # Today's statistics
            today_transactions = session.query(Transaction).filter(
                func.date(Transaction.created_at) == today
            ).count()
            today_revenue = session.query(func.sum(Transaction.commission)).filter(
                and_(
                    func.date(Transaction.created_at) == today,
                    Transaction.status == TransactionStatus.COMPLETED
                )
            ).scalar() or 0
            
            # Weekly statistics
            week_transactions = session.query(Transaction).filter(
                Transaction.created_at >= week_ago
            ).count()
            week_revenue = session.query(func.sum(Transaction.commission)).filter(
                and_(
                    Transaction.created_at >= week_ago,
                    Transaction.status == TransactionStatus.COMPLETED
                )
            ).scalar() or 0
            
            # Monthly statistics
            month_transactions = session.query(Transaction).filter(
                Transaction.created_at >= month_ago
            ).count()
            month_revenue = session.query(func.sum(Transaction.commission)).filter(
                and_(
                    Transaction.created_at >= month_ago,
                    Transaction.status == TransactionStatus.COMPLETED
                )
            ).scalar() or 0
            
            # Top sellers this month
            top_sellers = session.query(
                User.first_name, User.username, func.count(Transaction.id).label('transaction_count')
            ).join(Transaction, User.id == Transaction.seller_id).filter(
                and_(
                    Transaction.created_at >= month_ago,
                    Transaction.status == TransactionStatus.COMPLETED
                )
            ).group_by(User.id).order_by(func.count(Transaction.id).desc()).limit(5).all()
        
        stats_text = f"""
📊 Детальная статистика

👥 ПОЛЬЗОВАТЕЛИ:
• Всего: {total_users}
• Сегодня: {new_users_today}
• За неделю: {new_users_week}
• За месяц: {new_users_month}

🤝 СДЕЛКИ:
• Всего: {total_transactions}
• Завершено: {completed_transactions}
• Отменено: {cancelled_transactions}
• Успешность: {success_rate:.1f}%

💰 ДОХОД:
• Общий: {total_revenue:.2f} грн
• Сегодня: {today_revenue:.2f} грн
• За неделю: {week_revenue:.2f} грн
• За месяц: {month_revenue:.2f} грн

📝 ОБЪЯВЛЕНИЯ:
• Всего: {total_posts}
• Активных: {active_posts}

📈 АКТИВНОСТЬ:
• Сделки сегодня: {today_transactions}
• Сделки за неделю: {week_transactions}
• Сделки за месяц: {month_transactions}

🏆 ТОП ПРОДАВЦЫ (месяц):
        """
        
        for i, seller in enumerate(top_sellers, 1):
            username = f"@{seller.username}" if seller.username else "нет"
            stats_text += f"\n{i}. {seller.first_name} ({username}) - {seller.transaction_count} сделок"
        
        await update.message.reply_text(stats_text)
    
    @staticmethod
    async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """User management command"""
        user_id = update.effective_user.id
        
        if not Config.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав администратора.")
            return
        
        if context.args:
            target_user_id = context.args[0]
            
            # Check if it's a numeric ID or username
            if target_user_id.isdigit():
                await AdminPanelHandler._show_user_details_by_id(update, context, int(target_user_id))
            elif target_user_id.startswith('@'):
                await AdminPanelHandler._show_user_details_by_username(update, context, target_user_id[1:])
            else:
                await update.message.reply_text(
                    "❌ Неверный формат. Используйте:\n"
                    "/users [user_id] или /users @username"
                )
        else:
            await AdminPanelHandler._show_users_list(update, context)
    
    @staticmethod
    async def _show_user_details_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE, telegram_id: int):
        """Show user details by Telegram ID"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                await update.message.reply_text("❌ Пользователь не найден.")
                return
            
            await AdminPanelHandler._display_user_details(update, context, user)
    
    @staticmethod
    async def _show_user_details_by_username(update: Update, context: ContextTypes.DEFAULT_TYPE, username: str):
        """Show user details by username"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            
            if not user:
                await update.message.reply_text("❌ Пользователь не найден.")
                return
            
            await AdminPanelHandler._display_user_details(update, context, user)
    
    @staticmethod
    async def _display_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
        """Display detailed user information"""
        with db_manager.get_session() as session:
            # Get user's posts count
            posts_count = session.query(Post).filter(Post.user_id == user.id).count()
            active_posts = session.query(Post).filter(
                and_(Post.user_id == user.id, Post.is_active == True)
            ).count()
            
            # Get user's transaction count as seller and buyer
            seller_transactions = session.query(Transaction).filter(Transaction.seller_id == user.id).count()
            buyer_transactions = session.query(Transaction).filter(Transaction.buyer_id == user.id).count()
            
            # Get recent admin actions
            recent_actions = session.query(AdminAction).filter(
                AdminAction.target_user_id == user.id
            ).order_by(AdminAction.created_at.desc()).limit(3).all()
            
            # Status info
            status_emoji = {
                UserStatus.ACTIVE: "✅",
                UserStatus.SUSPICIOUS: "⚠️",
                UserStatus.BANNED: "🚫"
            }
            
            user_info = f"""
👤 Информация о пользователе

🆔 ID: {user.telegram_id}
👤 Имя: {user.first_name} {user.last_name or ''}
📱 Username: @{user.username or 'нет'}
🏷 Ник: {user.nickname or 'нет'}
📞 Телефон: {user.phone or 'нет'}

📊 Статус: {status_emoji.get(user.status, '❓')} {user.status.value}
⭐ Рейтинг: {user.average_rating:.1f}/5.0
🏆 Проверенный продавец: {'✅' if user.is_verified_seller else '❌'}

📈 Статистика:
• Всего сделок: {user.total_transactions}
• Как продавец: {seller_transactions}
• Как покупатель: {buyer_transactions}
• Общая сумма: {user.total_amount:.2f} грн
• Объявлений: {posts_count} (активных: {active_posts})
• Предупреждений: {user.warnings_count}

📅 Даты:
• Регистрация: {user.created_at.strftime('%d.%m.%Y %H:%M')}
• Последняя активность: {user.last_activity.strftime('%d.%m.%Y %H:%M') if user.last_activity else 'неизвестно'}
            """
            
            if recent_actions:
                user_info += "\n🔧 Последние действия админов:\n"
                for action in recent_actions:
                    user_info += f"• {action.action_type} - {action.created_at.strftime('%d.%m %H:%M')}\n"
            
            await update.message.reply_text(
                user_info,
                reply_markup=Keyboards.admin_user_actions(user.id)
            )
    
    @staticmethod
    async def _show_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show list of users with filters"""
        users_text = """
👥 Управление пользователями

Для получения информации о пользователе:
/users [telegram_id] - по ID
/users @username - по username

📊 Быстрые фильтры:
/users banned - заблокированные
/users suspicious - подозрительные
/users active - активные
/users top - топ продавцы
        """
        
        # Handle filter arguments
        if context.args and context.args[0] in ['banned', 'suspicious', 'active', 'top']:
            filter_type = context.args[0]
            await AdminPanelHandler._show_filtered_users(update, context, filter_type)
        else:
            await update.message.reply_text(users_text)
    
    @staticmethod
    async def _show_filtered_users(update: Update, context: ContextTypes.DEFAULT_TYPE, filter_type: str):
        """Show filtered list of users"""
        with db_manager.get_session() as session:
            if filter_type == 'banned':
                users = session.query(User).filter(User.status == UserStatus.BANNED).limit(20).all()
                title = "🚫 Заблокированные пользователи:"
                
            elif filter_type == 'suspicious':
                users = session.query(User).filter(User.status == UserStatus.SUSPICIOUS).limit(20).all()
                title = "⚠️ Подозрительные пользователи:"
                
            elif filter_type == 'active':
                users = session.query(User).filter(
                    and_(
                        User.status == UserStatus.ACTIVE,
                        User.last_activity >= datetime.now() - timedelta(days=7)
                    )
                ).order_by(User.last_activity.desc()).limit(20).all()
                title = "✅ Активные пользователи (за неделю):"
                
            elif filter_type == 'top':
                users = session.query(User).filter(
                    User.total_transactions > 0
                ).order_by(User.total_transactions.desc()).limit(20).all()
                title = "🏆 Топ продавцы:"
            
            if not users:
                await update.message.reply_text(f"👥 {title}\n\nПользователи не найдены.")
                return
            
            user_list = f"👥 {title}\n\n"
            
            for user in users:
                status_emoji = {
                    UserStatus.ACTIVE: "✅",
                    UserStatus.SUSPICIOUS: "⚠️",
                    UserStatus.BANNED: "🚫"
                }
                
                username = f"@{user.username}" if user.username else "нет"
                user_list += f"{status_emoji.get(user.status, '❓')} {user.first_name} ({username})\n"
                user_list += f"   🆔 {user.telegram_id} | 🤝 {user.total_transactions} сделок\n\n"
            
            await update.message.reply_text(user_list)
    
    @staticmethod
    async def handle_admin_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin actions on users"""
        query = update.callback_query
        await query.answer()
        
        if not Config.is_admin(query.from_user.id):
            await query.edit_message_text("❌ У вас нет прав администратора.")
            return
        
        if query.data.startswith("admin_ban_"):
            user_id = int(query.data.split("_")[2])
            await AdminPanelHandler._ban_user(query, context, user_id)
            
        elif query.data.startswith("admin_unban_"):
            user_id = int(query.data.split("_")[2])
            await AdminPanelHandler._unban_user(query, context, user_id)
            
        elif query.data.startswith("admin_suspicious_"):
            user_id = int(query.data.split("_")[2])
            await AdminPanelHandler._mark_suspicious(query, context, user_id)
            
        elif query.data.startswith("admin_balance_"):
            user_id = int(query.data.split("_")[2])
            await AdminPanelHandler._change_balance(query, context, user_id)
            
        elif query.data.startswith("admin_stats_"):
            user_id = int(query.data.split("_")[2])
            await AdminPanelHandler._show_user_stats(query, context, user_id)
    
    @staticmethod
    async def _ban_user(query, context, user_id: int):
        """Ban a user"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if user:
                user.status = UserStatus.BANNED
                
                # Log admin action
                admin_action = AdminAction(
                    admin_id=query.from_user.id,
                    target_user_id=user_id,
                    action_type='ban_user',
                    reason='Заблокирован администратором'
                )
                session.add(admin_action)
                
                await query.edit_message_text(
                    f"🚫 Пользователь {user.first_name} заблокирован."
                )
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text="🚫 Ваш аккаунт заблокирован администратором.\n\n"
                             "Для разблокировки обратитесь в поддержку."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify banned user: {e}")
    
    @staticmethod
    async def _unban_user(query, context, user_id: int):
        """Unban a user"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if user:
                user.status = UserStatus.ACTIVE
                user.warnings_count = 0  # Reset warnings
                
                # Log admin action
                admin_action = AdminAction(
                    admin_id=query.from_user.id,
                    target_user_id=user_id,
                    action_type='unban_user',
                    reason='Разблокирован администратором'
                )
                session.add(admin_action)
                
                await query.edit_message_text(
                    f"✅ Пользователь {user.first_name} разблокирован."
                )
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text="✅ Ваш аккаунт разблокирован!\n\n"
                             "Теперь вы можете пользоваться всеми функциями бота."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify unbanned user: {e}")
    
    @staticmethod
    async def _mark_suspicious(query, context, user_id: int):
        """Mark user as suspicious"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if user:
                user.status = UserStatus.SUSPICIOUS
                
                # Log admin action
                admin_action = AdminAction(
                    admin_id=query.from_user.id,
                    target_user_id=user_id,
                    action_type='mark_suspicious',
                    reason='Помечен как подозрительный'
                )
                session.add(admin_action)
                
                await query.edit_message_text(
                    f"⚠️ Пользователь {user.first_name} помечен как подозрительный."
                )
    
    @staticmethod
    async def _change_balance(query, context, user_id: int):
        """Request balance change for user"""
        await query.edit_message_text(
            "💰 Функция изменения баланса\n\n"
            "В данной версии бота управление балансом происходит через внешние платежные системы.\n"
            "Для изменения баланса пользователя обратитесь к финансовому администратору."
        )
    
    @staticmethod
    async def _show_user_stats(query, context, user_id: int):
        """Show detailed user statistics"""
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
            
            # Revenue generated
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
📊 Детальная статистика пользователя
👤 {user.first_name}

🤝 СДЕЛКИ:
• Как продавец: {total_as_seller}
• Как покупатель: {total_as_buyer}
• Успешно завершено: {completed_as_seller}
• Успешность: {(completed_as_seller/total_as_seller*100) if total_as_seller > 0 else 0:.1f}%

💰 ДОХОД ПЛАТФОРМЕ:
• Комиссий сгенерировано: {revenue_generated:.2f} грн

📈 АКТИВНОСТЬ (неделя):
• Новых объявлений: {recent_posts}
• Новых сделок: {recent_transactions}

⚠️ БЕЗОПАСНОСТЬ:
• Предупреждений: {user.warnings_count}
• Статус: {user.status.value}
            """
            
            await query.edit_message_text(stats_text)
    
    @staticmethod
    async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all users"""
        user_id = update.effective_user.id
        
        if not Config.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав администратора.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "📢 Рассылка сообщений\n\n"
                "Использование: /broadcast [сообщение]\n\n"
                "Сообщение будет отправлено всем активным пользователям бота."
            )
            return
        
        message_text = " ".join(context.args)
        
        with db_manager.get_session() as session:
            # Get all active users
            users = session.query(User).filter(User.status == UserStatus.ACTIVE).all()
            
            sent_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text=f"📢 Сообщение от администрации:\n\n{message_text}"
                    )
                    sent_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send broadcast to {user.telegram_id}: {e}")
            
            # Log admin action
            admin_action = AdminAction(
                admin_id=user_id,
                action_type='broadcast',
                reason=f'Рассылка: {message_text[:100]}...',
                details=json.dumps({
                    'sent': sent_count,
                    'failed': failed_count,
                    'message': message_text
                })
            )
            session.add(admin_action)
        
        await update.message.reply_text(
            f"📢 Рассылка завершена!\n\n"
            f"✅ Отправлено: {sent_count}\n"
            f"❌ Ошибки: {failed_count}"
        )
    
    @staticmethod
    async def admin_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage transactions"""
        user_id = update.effective_user.id
        
        if not Config.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав администратора.")
            return
        
        with db_manager.get_session() as session:
            if context.args and context.args[0] == 'pending':
                # Show pending transactions
                pending_transactions = session.query(Transaction).filter(
                    Transaction.status.in_([
                        TransactionStatus.VERIFICATION_PENDING,
                        TransactionStatus.PAYMENT_PENDING,
                        TransactionStatus.COMPLETED
                    ])
                ).order_by(Transaction.created_at.desc()).limit(10).all()
                
                if not pending_transactions:
                    await update.message.reply_text("📋 Нет ожидающих транзакций.")
                    return
                
                transactions_text = "📋 Ожидающие транзакции:\n\n"
                
                for transaction in pending_transactions:
                    seller = session.query(User).filter(User.id == transaction.seller_id).first()
                    buyer = session.query(User).filter(User.id == transaction.buyer_id).first()
                    
                    status_emoji = {
                        TransactionStatus.VERIFICATION_PENDING: "🎥",
                        TransactionStatus.PAYMENT_PENDING: "💰",
                        TransactionStatus.COMPLETED: "✅"
                    }
                    
                    transactions_text += f"{status_emoji.get(transaction.status, '❓')} ID: {transaction.id}\n"
                    transactions_text += f"💰 {transaction.amount} грн\n"
                    transactions_text += f"👤 {seller.first_name} → {buyer.first_name}\n"
                    transactions_text += f"📅 {transaction.created_at.strftime('%d.%m %H:%M')}\n\n"
                
                await update.message.reply_text(transactions_text)
            
            else:
                # Show transaction statistics
                total_transactions = session.query(Transaction).count()
                pending_verification = session.query(Transaction).filter(
                    Transaction.status == TransactionStatus.VERIFICATION_PENDING
                ).count()
                pending_payment = session.query(Transaction).filter(
                    Transaction.status == TransactionStatus.PAYMENT_PENDING
                ).count()
                awaiting_approval = session.query(Transaction).filter(
                    Transaction.status == TransactionStatus.COMPLETED
                ).count()
                
                transactions_info = f"""
🤝 Управление сделками

📊 Статистика:
• Всего сделок: {total_transactions}
• Ожидают проверки: {pending_verification}
• Ожидают оплаты: {pending_payment}
• Ожидают подтверждения: {awaiting_approval}

🔧 Команды:
/transactions pending - показать ожидающие
/transactions [ID] - детали сделки
                """
                
                await update.message.reply_text(transactions_info)
    
    @staticmethod
    async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show and modify bot settings"""
        user_id = update.effective_user.id
        
        if not Config.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав администратора.")
            return
        
        settings_text = f"""
⚙️ Настройки бота

💰 ЦЕНЫ:
• Стоимость поста: {Config.POST_PRICE} грн
• Стоимость закрепления: {Config.PIN_PRICE} грн
• Стоимость продления: {Config.EXTEND_PRICE} грн
• Комиссия эскроу: {Config.ESCROW_COMMISSION*100}%

⏰ ВРЕМЕННЫЕ ЛИМИТЫ:
• Длительность поста: {Config.POST_DURATION_HOURS} часов
• Предупреждение о закрытии: {Config.WARNING_HOURS} часов
• Таймаут сделки: {Config.TRANSACTION_TIMEOUT_HOURS} часов

🛡 АНТИСПАМ:
• Макс. отмен в день: {Config.MAX_DAILY_CANCELLATIONS}
• Мин. сумма сделки: {Config.MIN_TRANSACTION_AMOUNT} грн

📊 ФАЙЛЫ:
• Макс. фото: {Config.MAX_PHOTOS}
• Макс. размер файла: {Config.MAX_FILE_SIZE // (1024*1024)} MB

Для изменения настроек обратитесь к разработчику.
        """
        
        await update.message.reply_text(settings_text)
    
    @staticmethod
    async def update_daily_statistics(session):
        """Update daily statistics (called by scheduler)"""
        today = datetime.now().date()
        
        # Check if today's stats already exist
        existing_stats = session.query(BotStatistics).filter(
            func.date(BotStatistics.date) == today
        ).first()
        
        if existing_stats:
            return  # Already updated today
        
        # Calculate today's statistics
        yesterday = today - timedelta(days=1)
        
        new_users = session.query(User).filter(
            func.date(User.created_at) == yesterday
        ).count()
        
        active_users = session.query(User).filter(
            and_(
                User.last_activity >= yesterday,
                User.last_activity < today
            )
        ).count()
        
        new_posts = session.query(Post).filter(
            func.date(Post.created_at) == yesterday
        ).count()
        
        completed_transactions = session.query(Transaction).filter(
            and_(
                func.date(Transaction.completed_at) == yesterday,
                Transaction.status == TransactionStatus.COMPLETED
            )
        ).count()
        
        cancelled_transactions = session.query(Transaction).filter(
            and_(
                func.date(Transaction.created_at) == yesterday,
                Transaction.status == TransactionStatus.CANCELLED
            )
        ).count()
        
        transaction_volume = session.query(func.sum(Transaction.amount)).filter(
            and_(
                func.date(Transaction.completed_at) == yesterday,
                Transaction.status == TransactionStatus.COMPLETED
            )
        ).scalar() or 0
        
        commission_earned = session.query(func.sum(Transaction.commission)).filter(
            and_(
                func.date(Transaction.completed_at) == yesterday,
                Transaction.status == TransactionStatus.COMPLETED
            )
        ).scalar() or 0
        
        post_revenue = new_posts * Config.POST_PRICE
        
        # Create statistics record
        daily_stats = BotStatistics(
            date=yesterday,
            new_users=new_users,
            active_users=active_users,
            new_posts=new_posts,
            completed_transactions=completed_transactions,
            cancelled_transactions=cancelled_transactions,
            total_transaction_volume=transaction_volume,
            commission_earned=commission_earned,
            post_revenue=post_revenue
        )
        
        session.add(daily_stats)
        session.commit()
        
        logger.info(f"Daily statistics updated for {yesterday}")
    
    @staticmethod
    async def generate_daily_report(context: ContextTypes.DEFAULT_TYPE):
        """Generate and send daily report to admins"""
        with db_manager.get_session() as session:
            yesterday = datetime.now().date() - timedelta(days=1)
            
            stats = session.query(BotStatistics).filter(
                func.date(BotStatistics.date) == yesterday
            ).first()
            
            if not stats:
                return
            
            report_text = f"""
📊 Дневной отчет за {yesterday.strftime('%d.%m.%Y')}

👥 ПОЛЬЗОВАТЕЛИ:
• Новых: {stats.new_users}
• Активных: {stats.active_users}

📝 ОБЪЯВЛЕНИЯ:
• Новых постов: {stats.new_posts}
• Доход от постов: {stats.post_revenue:.2f} грн

🤝 СДЕЛКИ:
• Завершено: {stats.completed_transactions}
• Отменено: {stats.cancelled_transactions}
• Объем сделок: {stats.total_transaction_volume:.2f} грн
• Комиссий получено: {stats.commission_earned:.2f} грн

💰 ОБЩИЙ ДОХОД: {(stats.commission_earned + stats.post_revenue):.2f} грн
            """
            
            # Send to all admins
            for admin_id in Config.ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=report_text
                    )
                except Exception as e:
                    logger.error(f"Failed to send daily report to admin {admin_id}: {e}")