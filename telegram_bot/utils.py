import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MessageFormatter:
    """Форматирование сообщений"""
    
    @staticmethod
    def format_deal_status(status: str) -> str:
        """Форматирование статуса сделки с эмодзи"""
        status_map = {
            'waiting_seller': '⏳ Ожидает принятия продавцом',
            'active': '🔄 Активная сделка',
            'goods_sent': '📦 Товар отправлен',
            'completed': '✅ Сделка завершена',
            'cancelled': '❌ Сделка отменена',
            'dispute': '⚠️ Открыт спор'
        }
        return status_map.get(status, f"❓ {status}")
    
    @staticmethod
    def format_amount(amount: float) -> str:
        """Форматирование суммы"""
        return f"{amount:,.2f} ₽"
    
    @staticmethod
    def format_datetime(dt_string: str) -> str:
        """Форматирование даты и времени"""
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return dt_string
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Обрезка текста с многоточием"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

class Validator:
    """Валидация данных"""
    
    @staticmethod
    def validate_anonymous_id(anonymous_id: str) -> bool:
        """Проверка корректности анонимного ID"""
        return bool(re.match(r'^[a-zA-Z0-9]{8}$', anonymous_id))
    
    @staticmethod
    def validate_amount(amount_str: str) -> Optional[float]:
        """Проверка и парсинг суммы"""
        try:
            amount = float(amount_str.replace(',', '.').strip())
            if 0 < amount <= 1000000:
                return amount
        except ValueError:
            pass
        return None
    
    @staticmethod
    def validate_title(title: str) -> bool:
        """Проверка названия сделки"""
        return 3 <= len(title.strip()) <= 100
    
    @staticmethod
    def validate_description(description: str) -> bool:
        """Проверка описания сделки"""
        return 10 <= len(description.strip()) <= 1000

class Security:
    """Функции безопасности"""
    
    @staticmethod
    def hash_user_data(user_id: int, username: str = "") -> str:
        """Хеширование данных пользователя для анонимизации"""
        data = f"{user_id}:{username}:{datetime.now().timestamp()}"
        return hashlib.md5(data.encode()).hexdigest()[:8]
    
    @staticmethod
    def is_safe_content(content: str) -> bool:
        """Проверка контента на безопасность"""
        # Простая проверка на потенциально опасный контент
        dangerous_patterns = [
            r'https?://.*',  # Ссылки
            r'@\w+',  # Упоминания
            r'[+]\d{11,15}',  # Номера телефонов
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        return True

class Statistics:
    """Статистика и аналитика"""
    
    @staticmethod
    def calculate_user_stats(deals: List[Dict]) -> Dict:
        """Расчет статистики пользователя"""
        stats = {
            'total_deals': len(deals),
            'completed_deals': 0,
            'active_deals': 0,
            'cancelled_deals': 0,
            'total_amount': 0.0,
            'avg_amount': 0.0,
            'success_rate': 0.0
        }
        
        if not deals:
            return stats
        
        for deal in deals:
            if deal['status'] == 'completed':
                stats['completed_deals'] += 1
                stats['total_amount'] += deal['amount']
            elif deal['status'] in ['active', 'goods_sent']:
                stats['active_deals'] += 1
            elif deal['status'] == 'cancelled':
                stats['cancelled_deals'] += 1
        
        if stats['completed_deals'] > 0:
            stats['avg_amount'] = stats['total_amount'] / stats['completed_deals']
        
        if stats['total_deals'] > 0:
            stats['success_rate'] = (stats['completed_deals'] / stats['total_deals']) * 100
        
        return stats

class ChatManager:
    """Управление чатами сделок"""
    
    def __init__(self):
        self.active_chats = {}  # user_id: deal_id
    
    def enter_chat(self, user_id: int, deal_id: str):
        """Войти в чат сделки"""
        self.active_chats[user_id] = deal_id
    
    def exit_chat(self, user_id: int):
        """Выйти из чата сделки"""
        if user_id in self.active_chats:
            del self.active_chats[user_id]
    
    def get_active_chat(self, user_id: int) -> Optional[str]:
        """Получить активный чат пользователя"""
        return self.active_chats.get(user_id)
    
    def is_in_chat(self, user_id: int) -> bool:
        """Проверить, находится ли пользователь в чате"""
        return user_id in self.active_chats

class NotificationManager:
    """Управление уведомлениями"""
    
    @staticmethod
    def create_deal_notification(deal_title: str, amount: float, action: str) -> Dict:
        """Создание уведомления о сделке"""
        action_messages = {
            'created': f"Создана новая сделка: {deal_title} на сумму {MessageFormatter.format_amount(amount)}",
            'accepted': f"Сделка принята: {deal_title}",
            'declined': f"Сделка отклонена: {deal_title}",
            'goods_sent': f"Товар отправлен по сделке: {deal_title}",
            'completed': f"Сделка завершена: {deal_title}",
            'dispute': f"Открыт спор по сделке: {deal_title}"
        }
        
        return {
            'title': action_messages.get(action, f"Обновление сделки: {deal_title}"),
            'message': action_messages.get(action, "Произошло обновление сделки")
        }
    
    @staticmethod
    def create_message_notification(deal_title: str, sender_role: str) -> Dict:
        """Создание уведомления о новом сообщении"""
        return {
            'title': "Новое сообщение",
            'message': f"Получено сообщение от {'покупателя' if sender_role == 'buyer' else 'продавца'} в сделке: {deal_title}"
        }

class FileHandler:
    """Обработка файлов"""
    
    @staticmethod
    def get_file_info(file_name: str, file_size: int) -> Dict:
        """Получение информации о файле"""
        # Определение типа файла по расширению
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.zip', '.rar']
        
        file_ext = '.' + file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        if file_ext in image_extensions:
            file_type = 'image'
        elif file_ext in document_extensions:
            file_type = 'document'
        else:
            file_type = 'other'
        
        # Форматирование размера файла
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        return {
            'name': file_name,
            'size': file_size,
            'size_str': size_str,
            'type': file_type,
            'extension': file_ext
        }

class TimeUtils:
    """Утилиты для работы со временем"""
    
    @staticmethod
    def time_ago(dt_string: str) -> str:
        """Возвращает время в формате 'X минут назад'"""
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            delta = now - dt
            
            if delta.days > 0:
                return f"{delta.days} дн. назад"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"{hours} ч. назад"
            elif delta.seconds > 60:
                minutes = delta.seconds // 60
                return f"{minutes} мин. назад"
            else:
                return "только что"
        except:
            return dt_string
    
    @staticmethod
    def add_hours(dt_string: str, hours: int) -> str:
        """Добавляет часы к дате"""
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            new_dt = dt + timedelta(hours=hours)
            return new_dt.isoformat()
        except:
            return dt_string

# Глобальные экземпляры
chat_manager = ChatManager()
message_formatter = MessageFormatter()
validator = Validator()
security = Security()
notification_manager = NotificationManager()
file_handler = FileHandler()
time_utils = TimeUtils()