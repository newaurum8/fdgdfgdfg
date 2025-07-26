import aiosqlite
import uuid
from datetime import datetime
from typing import Optional, List, Dict

class Database:
    def __init__(self, db_path: str = "guarantor_bot.db"):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    anonymous_id TEXT UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Таблица сделок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS deals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    deal_id TEXT UNIQUE NOT NULL,
                    buyer_id TEXT NOT NULL,
                    seller_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL,
                    status TEXT DEFAULT 'waiting_seller',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (buyer_id) REFERENCES users (anonymous_id),
                    FOREIGN KEY (seller_id) REFERENCES users (anonymous_id)
                )
            """)
            
            # Таблица сообщений в чатах сделок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS deal_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    deal_id TEXT NOT NULL,
                    sender_id TEXT NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (deal_id) REFERENCES deals (deal_id),
                    FOREIGN KEY (sender_id) REFERENCES users (anonymous_id)
                )
            """)
            
            # Таблица уведомлений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    deal_id TEXT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (anonymous_id),
                    FOREIGN KEY (deal_id) REFERENCES deals (deal_id)
                )
            """)
            
            await db.commit()

    async def add_user(self, user_id: int, username: str = None, first_name: str = None) -> str:
        """Добавление нового пользователя"""
        anonymous_id = str(uuid.uuid4())[:8]
        
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO users (user_id, anonymous_id, username, first_name)
                    VALUES (?, ?, ?, ?)
                """, (user_id, anonymous_id, username, first_name))
                await db.commit()
                return anonymous_id
            except aiosqlite.IntegrityError:
                # Пользователь уже существует
                async with db.execute("SELECT anonymous_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else None

    async def get_user_by_telegram_id(self, user_id: int) -> Optional[Dict]:
        """Получение пользователя по Telegram ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'user_id': row[1],
                        'anonymous_id': row[2],
                        'username': row[3],
                        'first_name': row[4],
                        'created_at': row[5],
                        'is_active': row[6]
                    }
                return None

    async def get_user_by_anonymous_id(self, anonymous_id: str) -> Optional[Dict]:
        """Получение пользователя по анонимному ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE anonymous_id = ?", (anonymous_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'user_id': row[1],
                        'anonymous_id': row[2],
                        'username': row[3],
                        'first_name': row[4],
                        'created_at': row[5],
                        'is_active': row[6]
                    }
                return None

    async def create_deal(self, buyer_id: str, seller_id: str, title: str, description: str, amount: float) -> str:
        """Создание новой сделки"""
        deal_id = str(uuid.uuid4())[:12]
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO deals (deal_id, buyer_id, seller_id, title, description, amount)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (deal_id, buyer_id, seller_id, title, description, amount))
            await db.commit()
            return deal_id

    async def get_deal(self, deal_id: str) -> Optional[Dict]:
        """Получение сделки по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM deals WHERE deal_id = ?", (deal_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'deal_id': row[1],
                        'buyer_id': row[2],
                        'seller_id': row[3],
                        'title': row[4],
                        'description': row[5],
                        'amount': row[6],
                        'status': row[7],
                        'created_at': row[8],
                        'updated_at': row[9]
                    }
                return None

    async def update_deal_status(self, deal_id: str, status: str):
        """Обновление статуса сделки"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE deals SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE deal_id = ?
            """, (status, deal_id))
            await db.commit()

    async def get_user_deals(self, anonymous_id: str) -> List[Dict]:
        """Получение всех сделок пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM deals 
                WHERE buyer_id = ? OR seller_id = ?
                ORDER BY created_at DESC
            """, (anonymous_id, anonymous_id)) as cursor:
                rows = await cursor.fetchall()
                
                deals = []
                for row in rows:
                    deals.append({
                        'id': row[0],
                        'deal_id': row[1],
                        'buyer_id': row[2],
                        'seller_id': row[3],
                        'title': row[4],
                        'description': row[5],
                        'amount': row[6],
                        'status': row[7],
                        'created_at': row[8],
                        'updated_at': row[9]
                    })
                return deals

    async def add_message(self, deal_id: str, sender_id: str, content: str, message_type: str = 'text'):
        """Добавление сообщения в чат сделки"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO deal_messages (deal_id, sender_id, message_type, content)
                VALUES (?, ?, ?, ?)
            """, (deal_id, sender_id, message_type, content))
            await db.commit()

    async def get_deal_messages(self, deal_id: str, limit: int = 50) -> List[Dict]:
        """Получение сообщений чата сделки"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM deal_messages 
                WHERE deal_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (deal_id, limit)) as cursor:
                rows = await cursor.fetchall()
                
                messages = []
                for row in reversed(rows):  # Разворачиваем для хронологического порядка
                    messages.append({
                        'id': row[0],
                        'deal_id': row[1],
                        'sender_id': row[2],
                        'message_type': row[3],
                        'content': row[4],
                        'timestamp': row[5]
                    })
                return messages

    async def add_notification(self, user_id: str, title: str, message: str, deal_id: str = None):
        """Добавление уведомления"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO notifications (user_id, deal_id, title, message)
                VALUES (?, ?, ?, ?)
            """, (user_id, deal_id, title, message))
            await db.commit()

    async def get_unread_notifications(self, user_id: str) -> List[Dict]:
        """Получение непрочитанных уведомлений"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM notifications 
                WHERE user_id = ? AND is_read = FALSE
                ORDER BY created_at DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                
                notifications = []
                for row in rows:
                    notifications.append({
                        'id': row[0],
                        'user_id': row[1],
                        'deal_id': row[2],
                        'title': row[3],
                        'message': row[4],
                        'is_read': row[5],
                        'created_at': row[6]
                    })
                return notifications

    async def mark_notifications_read(self, user_id: str):
        """Отметить уведомления как прочитанные"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE notifications SET is_read = TRUE
                WHERE user_id = ?
            """, (user_id,))
            await db.commit()