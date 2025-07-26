from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Dict

class Keyboards:
    @staticmethod
    def main_menu():
        """Главное меню"""
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="💼 Мои сделки")],
                [KeyboardButton(text="🆕 Создать сделку"), KeyboardButton(text="🔍 Найти сделку")],
                [KeyboardButton(text="📊 Профиль"), KeyboardButton(text="🔔 Уведомления")],
                [KeyboardButton(text="ℹ️ Помощь")]
            ],
            resize_keyboard=True,
            persistent=True
        )
        return keyboard

    @staticmethod
    def deal_actions(deal_id: str, user_role: str, deal_status: str):
        """Клавиатура действий со сделкой"""
        buttons = []
        
        if deal_status == 'waiting_seller' and user_role == 'seller':
            buttons.append([InlineKeyboardButton(text="✅ Принять сделку", callback_data=f"accept_deal:{deal_id}")])
            buttons.append([InlineKeyboardButton(text="❌ Отклонить сделку", callback_data=f"decline_deal:{deal_id}")])
        
        elif deal_status == 'active':
            if user_role == 'seller':
                buttons.append([InlineKeyboardButton(text="📦 Товар отправлен", callback_data=f"goods_sent:{deal_id}")])
            elif user_role == 'buyer':
                buttons.append([InlineKeyboardButton(text="✅ Товар получен", callback_data=f"goods_received:{deal_id}")])
            
        elif deal_status == 'goods_sent' and user_role == 'buyer':
            buttons.append([InlineKeyboardButton(text="✅ Подтвердить получение", callback_data=f"confirm_receipt:{deal_id}")])
            buttons.append([InlineKeyboardButton(text="⚠️ Есть проблемы", callback_data=f"report_problem:{deal_id}")])
        
        # Всегда доступные действия
        buttons.append([InlineKeyboardButton(text="💬 Открыть чат", callback_data=f"open_chat:{deal_id}")])
        buttons.append([InlineKeyboardButton(text="📋 Детали сделки", callback_data=f"deal_details:{deal_id}")])
        
        if deal_status in ['active', 'goods_sent']:
            buttons.append([InlineKeyboardButton(text="🚨 Открыть спор", callback_data=f"open_dispute:{deal_id}")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def deal_chat_actions(deal_id: str):
        """Клавиатура для чата сделки"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📝 Написать сообщение", callback_data=f"write_message:{deal_id}")],
                [InlineKeyboardButton(text="📷 Отправить фото", callback_data=f"send_photo:{deal_id}")],
                [InlineKeyboardButton(text="📁 Отправить файл", callback_data=f"send_file:{deal_id}")],
                [InlineKeyboardButton(text="🔙 Назад к сделке", callback_data=f"back_to_deal:{deal_id}")],
            ]
        )
        return keyboard

    @staticmethod
    def confirm_deal_creation(seller_id: str):
        """Подтверждение создания сделки"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Создать сделку", callback_data=f"confirm_create_deal:{seller_id}")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_deal_creation")],
            ]
        )
        return keyboard

    @staticmethod
    def dispute_actions(deal_id: str):
        """Действия при споре"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📝 Описать проблему", callback_data=f"describe_problem:{deal_id}")],
                [InlineKeyboardButton(text="📷 Прикрепить доказательства", callback_data=f"attach_evidence:{deal_id}")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_deal:{deal_id}")],
            ]
        )
        return keyboard

    @staticmethod
    def my_deals_filter():
        """Фильтр для моих сделок"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Активные", callback_data="filter_deals:active")],
                [InlineKeyboardButton(text="⏳ Ожидающие", callback_data="filter_deals:waiting")],
                [InlineKeyboardButton(text="✅ Завершенные", callback_data="filter_deals:completed")],
                [InlineKeyboardButton(text="📋 Все сделки", callback_data="filter_deals:all")],
            ]
        )
        return keyboard

    @staticmethod
    def deal_list(deals: List[Dict], page: int = 0, deals_per_page: int = 5):
        """Список сделок с пагинацией"""
        buttons = []
        start_idx = page * deals_per_page
        end_idx = start_idx + deals_per_page
        
        for deal in deals[start_idx:end_idx]:
            status_emoji = {
                'waiting_seller': '⏳',
                'active': '🔄',
                'goods_sent': '📦',
                'completed': '✅',
                'cancelled': '❌',
                'dispute': '⚠️'
            }.get(deal['status'], '❓')
            
            deal_text = f"{status_emoji} {deal['title'][:20]}... - {deal['amount']}₽"
            buttons.append([InlineKeyboardButton(text=deal_text, callback_data=f"view_deal:{deal['deal_id']}")])
        
        # Пагинация
        pagination_buttons = []
        if page > 0:
            pagination_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page_deals:{page-1}"))
        if end_idx < len(deals):
            pagination_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"page_deals:{page+1}"))
        
        if pagination_buttons:
            buttons.append(pagination_buttons)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def back_to_main():
        """Кнопка возврата в главное меню"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
            ]
        )
        return keyboard

    @staticmethod
    def cancel_action():
        """Кнопка отмены действия"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")]
            ]
        )
        return keyboard

    @staticmethod
    def notification_actions(notification_id: int, deal_id: str = None):
        """Действия с уведомлением"""
        buttons = []
        
        if deal_id:
            buttons.append([InlineKeyboardButton(text="👀 Посмотреть сделку", callback_data=f"view_deal:{deal_id}")])
        
        buttons.append([InlineKeyboardButton(text="✅ Отметить прочитанным", callback_data=f"mark_read:{notification_id}")])
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_notifications")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)