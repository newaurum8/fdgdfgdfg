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