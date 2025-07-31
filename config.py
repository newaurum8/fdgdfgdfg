import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Config:
    # Bot configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    MODERATOR_GROUP_ID = int(os.getenv('MODERATOR_GROUP_ID', '0'))
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
    
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL')
    
    # Admin configuration
    ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
    
    # Pricing
    ESCROW_COMMISSION = float(os.getenv('ESCROW_COMMISSION', '0.05'))
    MIN_TRANSACTION_AMOUNT = int(os.getenv('MIN_TRANSACTION_AMOUNT', '50'))
    POST_PRICE = int(os.getenv('POST_PRICE', '30'))
    PIN_PRICE = int(os.getenv('PIN_PRICE', '99'))
    EXTEND_PRICE = int(os.getenv('EXTEND_PRICE', '25'))
    
    # Payment provider
    PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')
    
    # Post settings
    POST_DURATION_HOURS = 24  # How long posts stay active
    WARNING_HOURS = 2  # Hours before expiry to send warning
    
    # Transaction limits
    MAX_DAILY_CANCELLATIONS = 3
    TRANSACTION_TIMEOUT_HOURS = 3
    
    # Auction settings
    AUCTION_TIMERS = [30, 60, 120]  # minutes
    
    # Anti-spam keywords
    SPAM_KEYWORDS = [
        'без гаранта', 'давай бег гаранта', 'напрямую', 'переведи сразу',
        'обойдем бота', 'мой телеграм', '@', 'телефон', 'viber', 'whatsapp'
    ]
    
    # Verification phrases for video check
    VERIFICATION_PHRASES = [
        'Добро пожаловать в игровой мир',
        'Я подтверждаю свою личность',
        'Безопасная сделка через бота',
        'Проверка продавца пройдена',
        'Гарант защищает сделку'
    ]
    
    # File limits
    MAX_PHOTOS = 10
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        return user_id in cls.ADMIN_IDS