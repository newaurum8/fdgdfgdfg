from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional
from config import Config

class Keyboards:
    
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Main menu keyboard"""
        keyboard = [
            ["📢 Сделать объявление", "💬 Чаты"],
            ["👤 Профиль", "📘 FAQ"],
            ["🛠 Поддержка"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def announcement_types() -> InlineKeyboardMarkup:
        """Announcement types selection"""
        keyboard = [
            [InlineKeyboardButton("▶️ Сделать объявление", callback_data="announce_create")],
            [InlineKeyboardButton("🔍 Найти", callback_data="announce_search")],
            [InlineKeyboardButton("📣 Аукцион", callback_data="announce_auction")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def sell_or_buy() -> InlineKeyboardMarkup:
        """Sell or buy selection"""
        keyboard = [
            [InlineKeyboardButton("💰 Продать", callback_data="type_sell")],
            [InlineKeyboardButton("🛒 Купить", callback_data="type_buy")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_announce")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def price_type() -> InlineKeyboardMarkup:
        """Price type selection"""
        keyboard = [
            [InlineKeyboardButton("💵 Указать цену", callback_data="price_fixed")],
            [InlineKeyboardButton("💬 Договорная", callback_data="price_negotiable")],
            [InlineKeyboardButton("🆓 Без цены", callback_data="price_none")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_step")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def yes_no(yes_callback: str, no_callback: str) -> InlineKeyboardMarkup:
        """Generic yes/no keyboard"""
        keyboard = [
            [InlineKeyboardButton("✅ Да", callback_data=yes_callback)],
            [InlineKeyboardButton("❌ Нет", callback_data=no_callback)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def post_actions(post_id: int) -> InlineKeyboardMarkup:
        """Actions for a post"""
        keyboard = [
            [InlineKeyboardButton("🔁 Продлить", callback_data=f"extend_post_{post_id}")],
            [InlineKeyboardButton("❌ Удалить", callback_data=f"delete_post_{post_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def auction_timer() -> InlineKeyboardMarkup:
        """Auction timer selection"""
        keyboard = []
        for timer in Config.AUCTION_TIMERS:
            if timer < 60:
                label = f"{timer} мин"
            else:
                label = f"{timer // 60} час"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"timer_{timer}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_step")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def open_in_bot(post_unique_id: str) -> InlineKeyboardMarkup:
        """Open in bot button for channel posts"""
        keyboard = [
            [InlineKeyboardButton("📩 Открыть в боте", url=f"https://t.me/{Config.BOT_TOKEN.split(':')[0]}?start=post_{post_unique_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def contact_seller(chat_id: int) -> InlineKeyboardMarkup:
        """Contact seller button"""
        keyboard = [
            [InlineKeyboardButton("💬 Связаться с продавцом", callback_data=f"contact_{chat_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def chat_actions(chat_id: int) -> InlineKeyboardMarkup:
        """Chat action buttons"""
        keyboard = [
            [InlineKeyboardButton("🤝 Начать сделку", callback_data=f"start_transaction_{chat_id}")],
            [InlineKeyboardButton("❌ Закрыть чат", callback_data=f"close_chat_{chat_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def transaction_actions(transaction_id: int) -> InlineKeyboardMarkup:
        """Transaction action buttons"""
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить завершение", callback_data=f"confirm_transaction_{transaction_id}")],
            [InlineKeyboardButton("❌ Отказаться от сделки", callback_data=f"cancel_transaction_{transaction_id}")],
            [InlineKeyboardButton("🆘 Мне нужна помощь", callback_data=f"help_transaction_{transaction_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def commission_split() -> InlineKeyboardMarkup:
        """Commission payment options"""
        keyboard = [
            [InlineKeyboardButton("🤵 Продавец платит", callback_data="commission_seller")],
            [InlineKeyboardButton("🛒 Покупатель платит", callback_data="commission_buyer")],
            [InlineKeyboardButton("⚖️ Поровну (50/50)", callback_data="commission_split")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_step")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def payment_methods() -> InlineKeyboardMarkup:
        """Payment method selection"""
        keyboard = [
            [InlineKeyboardButton("💳 UA-карта", callback_data="payment_ua_card")],
            [InlineKeyboardButton("₿ Крипта (TON)", callback_data="payment_crypto_ton")],
            [InlineKeyboardButton("💰 Крипта (USDT)", callback_data="payment_crypto_usdt")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_step")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def rating_keyboard() -> InlineKeyboardMarkup:
        """Rating selection 1-5"""
        keyboard = []
        for i in range(1, 6):
            stars = "⭐" * i
            keyboard.append([InlineKeyboardButton(f"{stars} {i}", callback_data=f"rating_{i}")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_user_actions(user_id: int) -> InlineKeyboardMarkup:
        """Admin actions for user management"""
        keyboard = [
            [InlineKeyboardButton("🚫 Заблокировать", callback_data=f"admin_ban_{user_id}")],
            [InlineKeyboardButton("⚠️ Пометить подозрительным", callback_data=f"admin_suspicious_{user_id}")],
            [InlineKeyboardButton("✅ Разблокировать", callback_data=f"admin_unban_{user_id}")],
            [InlineKeyboardButton("💰 Изменить баланс", callback_data=f"admin_balance_{user_id}")],
            [InlineKeyboardButton("📊 Статистика", callback_data=f"admin_stats_{user_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_transaction_actions(transaction_id: int) -> InlineKeyboardMarkup:
        """Admin actions for transaction management"""
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить и выплатить", callback_data=f"admin_confirm_{transaction_id}")],
            [InlineKeyboardButton("❌ Отклонить", callback_data=f"admin_reject_{transaction_id}")],
            [InlineKeyboardButton("⏰ Продлить время", callback_data=f"admin_extend_{transaction_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def auction_actions(post_id: int) -> InlineKeyboardMarkup:
        """Auction management buttons"""
        keyboard = [
            [InlineKeyboardButton("💰 Сделать ставку", callback_data=f"auction_bid_{post_id}")],
            [InlineKeyboardButton("🏁 Завершить аукцион", callback_data=f"auction_end_{post_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def bid_actions(bid_id: int) -> InlineKeyboardMarkup:
        """Bid management buttons"""
        keyboard = [
            [InlineKeyboardButton("✅ Принять", callback_data=f"bid_accept_{bid_id}")],
            [InlineKeyboardButton("❌ Отклонить", callback_data=f"bid_reject_{bid_id}")],
            [InlineKeyboardButton("👤 Посмотреть профиль", callback_data=f"bid_profile_{bid_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def games_pagination(games: List, page: int = 0, page_size: int = 8) -> InlineKeyboardMarkup:
        """Paginated games selection"""
        keyboard = []
        start_idx = page * page_size
        end_idx = start_idx + page_size
        
        # Add game buttons
        for i in range(start_idx, min(end_idx, len(games))):
            game = games[i]
            keyboard.append([InlineKeyboardButton(game.name, callback_data=f"game_{game.id}")])
        
        # Add pagination buttons
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"games_page_{page-1}"))
        if end_idx < len(games):
            nav_row.append(InlineKeyboardButton("➡️", callback_data=f"games_page_{page+1}"))
        if nav_row:
            keyboard.append(nav_row)
            
        # Add "no game" option and back button
        keyboard.append([InlineKeyboardButton("🚫 Нет игры в списке", callback_data="game_none")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_step")])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def admin_main_panel() -> InlineKeyboardMarkup:
        """Admin main panel keyboard"""
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users")],
            [InlineKeyboardButton("🤝 Управление сделками", callback_data="admin_transactions")],
            [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings")],
            [InlineKeyboardButton("📈 Отчёты", callback_data="admin_reports")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_users_menu() -> InlineKeyboardMarkup:
        """Admin users management menu"""
        keyboard = [
            [InlineKeyboardButton("🔍 Найти пользователя", callback_data="admin_find_user")],
            [InlineKeyboardButton("🚫 Заблокированные", callback_data="admin_users_banned")],
            [InlineKeyboardButton("⚠️ Подозрительные", callback_data="admin_users_suspicious")],
            [InlineKeyboardButton("✅ Активные", callback_data="admin_users_active")],
            [InlineKeyboardButton("🏆 Топ продавцы", callback_data="admin_users_top")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_transactions_menu() -> InlineKeyboardMarkup:
        """Admin transactions management menu"""
        keyboard = [
            [InlineKeyboardButton("⏳ Ожидающие проверки", callback_data="admin_trans_pending")],
            [InlineKeyboardButton("💰 Ожидающие оплаты", callback_data="admin_trans_payment")],
            [InlineKeyboardButton("✅ Завершённые", callback_data="admin_trans_completed")],
            [InlineKeyboardButton("❌ Отменённые", callback_data="admin_trans_cancelled")],
            [InlineKeyboardButton("🔍 Найти сделку", callback_data="admin_find_transaction")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_stats_menu() -> InlineKeyboardMarkup:
        """Admin statistics menu"""
        keyboard = [
            [InlineKeyboardButton("📅 Сегодня", callback_data="admin_stats_today")],
            [InlineKeyboardButton("📊 Неделя", callback_data="admin_stats_week")],
            [InlineKeyboardButton("📈 Месяц", callback_data="admin_stats_month")],
            [InlineKeyboardButton("🎯 Общая статистика", callback_data="admin_stats_all")],
            [InlineKeyboardButton("💰 Доходы", callback_data="admin_stats_revenue")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_broadcast_menu() -> InlineKeyboardMarkup:
        """Admin broadcast menu"""
        keyboard = [
            [InlineKeyboardButton("📢 Всем пользователям", callback_data="admin_broadcast_all")],
            [InlineKeyboardButton("✅ Активным пользователям", callback_data="admin_broadcast_active")],
            [InlineKeyboardButton("🏆 Топ продавцам", callback_data="admin_broadcast_sellers")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_settings_menu() -> InlineKeyboardMarkup:
        """Admin settings menu"""
        keyboard = [
            [InlineKeyboardButton("💰 Цены", callback_data="admin_settings_prices")],
            [InlineKeyboardButton("⏰ Временные лимиты", callback_data="admin_settings_timers")],
            [InlineKeyboardButton("🛡️ Антиспам", callback_data="admin_settings_antispam")],
            [InlineKeyboardButton("📊 Файлы", callback_data="admin_settings_files")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_reports_menu() -> InlineKeyboardMarkup:
        """Admin reports menu"""
        keyboard = [
            [InlineKeyboardButton("📄 Дневной отчёт", callback_data="admin_report_daily")],
            [InlineKeyboardButton("📊 Недельный отчёт", callback_data="admin_report_weekly")],
            [InlineKeyboardButton("📈 Месячный отчёт", callback_data="admin_report_monthly")],
            [InlineKeyboardButton("📧 Настройка рассылки отчётов", callback_data="admin_report_settings")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_user_management(user_id: int, current_status: str) -> InlineKeyboardMarkup:
        """Enhanced admin user management keyboard"""
        keyboard = []
        
        # Status management buttons based on current status
        if current_status == "banned":
            keyboard.append([InlineKeyboardButton("✅ Разблокировать", callback_data=f"admin_unban_{user_id}")])
        else:
            keyboard.append([InlineKeyboardButton("🚫 Заблокировать", callback_data=f"admin_ban_{user_id}")])
        
        if current_status != "suspicious":
            keyboard.append([InlineKeyboardButton("⚠️ Пометить подозрительным", callback_data=f"admin_suspicious_{user_id}")])
        else:
            keyboard.append([InlineKeyboardButton("✅ Убрать пометку", callback_data=f"admin_unsuspicious_{user_id}")])
        
        # Additional actions
        keyboard.extend([
            [InlineKeyboardButton("📊 Детальная статистика", callback_data=f"admin_user_stats_{user_id}")],
            [InlineKeyboardButton("💬 Отправить сообщение", callback_data=f"admin_message_{user_id}")],
            [InlineKeyboardButton("📝 Посты пользователя", callback_data=f"admin_user_posts_{user_id}")],
            [InlineKeyboardButton("🤝 Сделки пользователя", callback_data=f"admin_user_transactions_{user_id}")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="admin_users")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_transaction_management(transaction_id: int, status: str) -> InlineKeyboardMarkup:
        """Enhanced admin transaction management keyboard"""
        keyboard = []
        
        if status == "verification_pending":
            keyboard.extend([
                [InlineKeyboardButton("✅ Подтвердить проверку", callback_data=f"admin_verify_approve_{transaction_id}")],
                [InlineKeyboardButton("❌ Отклонить проверку", callback_data=f"admin_verify_reject_{transaction_id}")]
            ])
        elif status == "completed":
            keyboard.extend([
                [InlineKeyboardButton("💰 Подтвердить и выплатить", callback_data=f"admin_payout_{transaction_id}")],
                [InlineKeyboardButton("❌ Отменить сделку", callback_data=f"admin_cancel_{transaction_id}")]
            ])
        elif status == "in_progress":
            keyboard.extend([
                [InlineKeyboardButton("⏰ Продлить время", callback_data=f"admin_extend_time_{transaction_id}")],
                [InlineKeyboardButton("🆘 Вмешаться в сделку", callback_data=f"admin_intervene_{transaction_id}")]
            ])
        
        # Common actions
        keyboard.extend([
            [InlineKeyboardButton("📊 Детали сделки", callback_data=f"admin_transaction_details_{transaction_id}")],
            [InlineKeyboardButton("💬 Связаться с участниками", callback_data=f"admin_contact_parties_{transaction_id}")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="admin_transactions")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_pagination(data_type: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
        """Admin pagination keyboard"""
        keyboard = []
        
        # Navigation buttons
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Пред", callback_data=f"admin_page_{data_type}_{page-1}"))
        
        nav_row.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="admin_page_info"))
        
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("След ➡️", callback_data=f"admin_page_{data_type}_{page+1}"))
        
        keyboard.append(nav_row)
        
        # Back button
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"admin_{data_type}")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_confirmation(action: str, target_id: int = None) -> InlineKeyboardMarkup:
        """Admin confirmation keyboard"""
        confirm_data = f"admin_confirm_{action}"
        cancel_data = f"admin_cancel_{action}"
        
        if target_id:
            confirm_data += f"_{target_id}"
            cancel_data += f"_{target_id}"
        
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data=confirm_data)],
            [InlineKeyboardButton("❌ Отменить", callback_data=cancel_data)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_time_extend_options(transaction_id: int) -> InlineKeyboardMarkup:
        """Time extension options for transactions"""
        keyboard = [
            [InlineKeyboardButton("⏰ +1 час", callback_data=f"admin_extend_1h_{transaction_id}")],
            [InlineKeyboardButton("⏰ +3 часа", callback_data=f"admin_extend_3h_{transaction_id}")],
            [InlineKeyboardButton("⏰ +6 часов", callback_data=f"admin_extend_6h_{transaction_id}")],
            [InlineKeyboardButton("⏰ +12 часов", callback_data=f"admin_extend_12h_{transaction_id}")],
            [InlineKeyboardButton("⏰ +24 часа", callback_data=f"admin_extend_24h_{transaction_id}")],
            [InlineKeyboardButton("⬅️ Назад", callback_data=f"admin_transaction_details_{transaction_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)