import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from database import Database
from keyboards import Keyboards
from states import DealCreationStates, DealChatStates, DisputeStates, FindDealStates

router = Router()
logger = logging.getLogger(__name__)

# Глобальная переменная для хранения пользователей в чатах
user_chat_states = {}

class Handlers:
    def __init__(self, db: Database):
        self.db = db

    async def cmd_start(self, message: Message, state: FSMContext):
        """Обработчик команды /start"""
        await state.clear()
        
        # Регистрация или получение пользователя
        user = await self.db.get_user_by_telegram_id(message.from_user.id)
        if not user:
            anonymous_id = await self.db.add_user(
                message.from_user.id,
                message.from_user.username,
                message.from_user.first_name
            )
        else:
            anonymous_id = user['anonymous_id']

        welcome_text = f"""🔒 Добро пожаловать в анонимный гарант-бот!

👤 Ваш анонимный ID: `{anonymous_id}`

🔐 Особенности бота:
• Полная анонимность - никто не увидит ваш @username
• Безопасные сделки через гаранта
• Встроенный чат для общения
• История всех операций

🚀 Начните с создания сделки или просмотра активных!"""

        await message.answer(
            welcome_text,
            reply_markup=Keyboards.main_menu(),
            parse_mode="Markdown"
        )

    async def handle_main_menu(self, message: Message, state: FSMContext):
        """Обработчик главного меню"""
        await state.clear()
        
        if message.text == "💼 Мои сделки":
            await self.show_my_deals(message)
        elif message.text == "🆕 Создать сделку":
            await self.start_deal_creation(message, state)
        elif message.text == "🔍 Найти сделку":
            await self.start_find_deal(message, state)
        elif message.text == "📊 Профиль":
            await self.show_profile(message)
        elif message.text == "🔔 Уведомления":
            await self.show_notifications(message)
        elif message.text == "ℹ️ Помощь":
            await self.show_help(message)

    async def show_my_deals(self, message: Message):
        """Показать мои сделки"""
        user = await self.db.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден.")
            return

        deals = await self.db.get_user_deals(user['anonymous_id'])
        
        if not deals:
            await message.answer(
                "📋 У вас пока нет сделок.\n\n"
                "Используйте кнопку '🆕 Создать сделку' чтобы начать!",
                reply_markup=Keyboards.main_menu()
            )
            return

        await message.answer(
            f"📋 Ваши сделки ({len(deals)} шт.):\n\n"
            "Выберите фильтр для просмотра:",
            reply_markup=Keyboards.my_deals_filter()
        )

    async def start_deal_creation(self, message: Message, state: FSMContext):
        """Начать создание сделки"""
        await message.answer(
            "🆕 Создание новой сделки\n\n"
            "Введите анонимный ID продавца:\n"
            "📝 Формат: 8 символов (например: a1b2c3d4)",
            reply_markup=Keyboards.cancel_action()
        )
        await state.set_state(DealCreationStates.waiting_seller_id)

    async def process_seller_id(self, message: Message, state: FSMContext):
        """Обработка ввода ID продавца"""
        seller_id = message.text.strip()
        
        if len(seller_id) != 8:
            await message.answer(
                "❌ Неверный формат ID!\n"
                "ID должен содержать 8 символов. Попробуйте снова:"
            )
            return

        # Проверяем существование продавца
        seller = await self.db.get_user_by_anonymous_id(seller_id)
        if not seller:
            await message.answer(
                "❌ Пользователь с таким ID не найден!\n"
                "Проверьте правильность ID и попробуйте снова:"
            )
            return

        # Проверяем, что это не сам пользователь
        user = await self.db.get_user_by_telegram_id(message.from_user.id)
        if user['anonymous_id'] == seller_id:
            await message.answer(
                "❌ Нельзя создать сделку с самим собой!\n"
                "Введите ID другого пользователя:"
            )
            return

        await state.update_data(seller_id=seller_id)
        await message.answer(
            "📝 Введите название товара/услуги:\n"
            "Например: 'Игровой аккаунт Steam' или 'Дизайн логотипа'"
        )
        await state.set_state(DealCreationStates.waiting_title)

    async def process_deal_title(self, message: Message, state: FSMContext):
        """Обработка названия сделки"""
        title = message.text.strip()
        
        if len(title) < 3:
            await message.answer("❌ Название слишком короткое! Минимум 3 символа.")
            return
        
        if len(title) > 100:
            await message.answer("❌ Название слишком длинное! Максимум 100 символов.")
            return

        await state.update_data(title=title)
        await message.answer(
            "📄 Введите описание товара/услуги:\n"
            "Опишите детально что покупаете и ваши требования."
        )
        await state.set_state(DealCreationStates.waiting_description)

    async def process_deal_description(self, message: Message, state: FSMContext):
        """Обработка описания сделки"""
        description = message.text.strip()
        
        if len(description) < 10:
            await message.answer("❌ Описание слишком короткое! Минимум 10 символов.")
            return

        await state.update_data(description=description)
        await message.answer(
            "💰 Введите сумму сделки в рублях:\n"
            "Например: 1500 или 150.50"
        )
        await state.set_state(DealCreationStates.waiting_amount)

    async def process_deal_amount(self, message: Message, state: FSMContext):
        """Обработка суммы сделки"""
        try:
            amount = float(message.text.strip().replace(',', '.'))
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
            if amount > 1000000:
                raise ValueError("Слишком большая сумма")
        except ValueError:
            await message.answer(
                "❌ Неверный формат суммы!\n"
                "Введите число больше 0. Например: 1500 или 150.50"
            )
            return

        data = await state.get_data()
        await state.update_data(amount=amount)

        # Показываем подтверждение
        confirmation_text = f"""✅ Подтверждение создания сделки:

📝 Название: {data['title']}
📄 Описание: {data['description'][:100]}{'...' if len(data['description']) > 100 else ''}
👤 Продавец ID: {data['seller_id']}
💰 Сумма: {amount:,.2f} ₽

⚠️ После создания продавец получит уведомление и сможет принять или отклонить сделку."""

        await message.answer(
            confirmation_text,
            reply_markup=Keyboards.confirm_deal_creation(data['seller_id'])
        )
        await state.set_state(DealCreationStates.confirmation)

    async def confirm_deal_creation(self, callback: CallbackQuery, state: FSMContext):
        """Подтверждение создания сделки"""
        if not callback.data.startswith("confirm_create_deal:"):
            return

        data = await state.get_data()
        user = await self.db.get_user_by_telegram_id(callback.from_user.id)
        
        # Создаем сделку
        deal_id = await self.db.create_deal(
            buyer_id=user['anonymous_id'],
            seller_id=data['seller_id'],
            title=data['title'],
            description=data['description'],
            amount=data['amount']
        )

        # Уведомляем продавца
        seller = await self.db.get_user_by_anonymous_id(data['seller_id'])
        await self.db.add_notification(
            user_id=data['seller_id'],
            title="Новая сделка!",
            message=f"Покупатель предлагает сделку: {data['title']} за {data['amount']:,.2f} ₽",
            deal_id=deal_id
        )

        await callback.message.edit_text(
            f"✅ Сделка создана!\n\n"
            f"🆔 ID сделки: `{deal_id}`\n"
            f"📝 Название: {data['title']}\n"
            f"💰 Сумма: {data['amount']:,.2f} ₽\n\n"
            f"Продавец получил уведомление. Ожидайте ответа!",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_main()
        )
        
        await state.clear()

    async def start_find_deal(self, message: Message, state: FSMContext):
        """Начать поиск сделки"""
        await message.answer(
            "🔍 Поиск сделки\n\n"
            "Введите ID сделки для просмотра:",
            reply_markup=Keyboards.cancel_action()
        )
        await state.set_state(FindDealStates.waiting_deal_id)

    async def process_find_deal(self, message: Message, state: FSMContext):
        """Обработка поиска сделки"""
        deal_id = message.text.strip()
        
        deal = await self.db.get_deal(deal_id)
        if not deal:
            await message.answer(
                "❌ Сделка с таким ID не найдена!\n"
                "Проверьте правильность ID и попробуйте снова:"
            )
            return

        user = await self.db.get_user_by_telegram_id(message.from_user.id)
        
        # Проверяем права доступа к сделке
        if user['anonymous_id'] not in [deal['buyer_id'], deal['seller_id']]:
            await message.answer("❌ У вас нет доступа к этой сделке!")
            await state.clear()
            return

        await self.show_deal_details(message, deal_id, user['anonymous_id'])
        await state.clear()

    async def show_deal_details(self, message: Message, deal_id: str, user_anonymous_id: str):
        """Показать детали сделки"""
        deal = await self.db.get_deal(deal_id)
        if not deal:
            await message.answer("❌ Сделка не найдена!")
            return

        # Определяем роль пользователя
        if user_anonymous_id == deal['buyer_id']:
            user_role = 'buyer'
            other_party = 'seller'
            other_id = deal['seller_id']
        else:
            user_role = 'seller'
            other_party = 'buyer'
            other_id = deal['buyer_id']

        status_descriptions = {
            'waiting_seller': '⏳ Ожидает принятия продавцом',
            'active': '🔄 Активная сделка',
            'goods_sent': '📦 Товар отправлен',
            'completed': '✅ Сделка завершена',
            'cancelled': '❌ Сделка отменена',
            'dispute': '⚠️ Открыт спор'
        }

        deal_text = f"""📋 Детали сделки

🆔 ID: `{deal['deal_id']}`
📝 Название: {deal['title']}
📄 Описание: {deal['description']}
💰 Сумма: {deal['amount']:,.2f} ₽

👤 Ваша роль: {'Покупатель' if user_role == 'buyer' else 'Продавец'}
👥 {other_party.title()}: {other_id}

📊 Статус: {status_descriptions.get(deal['status'], deal['status'])}
📅 Создана: {deal['created_at']}
🔄 Обновлена: {deal['updated_at']}"""

        keyboard = Keyboards.deal_actions(deal_id, user_role, deal['status'])
        
        await message.answer(
            deal_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    async def show_profile(self, message: Message):
        """Показать профиль пользователя"""
        user = await self.db.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден.")
            return

        deals = await self.db.get_user_deals(user['anonymous_id'])
        
        # Статистика по сделкам
        stats = {
            'total': len(deals),
            'completed': len([d for d in deals if d['status'] == 'completed']),
            'active': len([d for d in deals if d['status'] in ['active', 'goods_sent']]),
            'waiting': len([d for d in deals if d['status'] == 'waiting_seller'])
        }

        profile_text = f"""📊 Ваш профиль

👤 Анонимный ID: `{user['anonymous_id']}`
📅 Регистрация: {user['created_at']}

📈 Статистика сделок:
• Всего сделок: {stats['total']}
• Завершено: {stats['completed']}
• Активных: {stats['active']}
• Ожидающих: {stats['waiting']}

🔒 Статус: {'✅ Активен' if user['is_active'] else '❌ Заблокирован'}"""

        await message.answer(
            profile_text,
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_main()
        )

    async def show_notifications(self, message: Message):
        """Показать уведомления"""
        user = await self.db.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден.")
            return

        notifications = await self.db.get_unread_notifications(user['anonymous_id'])
        
        if not notifications:
            await message.answer(
                "🔔 Уведомления\n\n"
                "У вас нет новых уведомлений.",
                reply_markup=Keyboards.back_to_main()
            )
            return

        text = f"🔔 Новые уведомления ({len(notifications)}):\n\n"
        
        for notif in notifications[:10]:  # Показываем только 10 последних
            text += f"📌 {notif['title']}\n"
            text += f"💬 {notif['message'][:100]}{'...' if len(notif['message']) > 100 else ''}\n"
            text += f"⏰ {notif['created_at']}\n\n"

        await message.answer(
            text,
            reply_markup=Keyboards.back_to_main()
        )
        
        # Отмечаем уведомления как прочитанные
        await self.db.mark_notifications_read(user['anonymous_id'])

    async def show_help(self, message: Message):
        """Показать справку"""
        help_text = """ℹ️ Справка по боту

🔐 Анонимность:
• Ваш @username никому не виден
• Используются только анонимные ID
• Вся переписка конфиденциальна

💼 Создание сделок:
1. Узнайте анонимный ID продавца
2. Создайте сделку с описанием
3. Дождитесь принятия продавцом
4. Общайтесь через встроенный чат
5. Подтверждайте этапы сделки

🔄 Статусы сделок:
⏳ Ожидает принятия - продавец еще не ответил
🔄 Активная - сделка принята, идет выполнение
📦 Товар отправлен - продавец отправил товар
✅ Завершена - покупатель подтвердил получение
❌ Отменена - сделка отменена
⚠️ Спор - открыт спор по сделке

🛡️ Безопасность:
• Гарант защищает обе стороны
• Все сообщения сохраняются
• Возможность открытия споров
• Администрация разбирает конфликты

❓ Нужна помощь? Обратитесь к администратору."""

        await message.answer(
            help_text,
            reply_markup=Keyboards.back_to_main()
        )

    # Обработчики callback-запросов
    async def handle_callback(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик всех callback-запросов"""
        data = callback.data
        
        try:
            if data.startswith("accept_deal:"):
                await self.accept_deal(callback)
            elif data.startswith("decline_deal:"):
                await self.decline_deal(callback)
            elif data.startswith("goods_sent:"):
                await self.mark_goods_sent(callback)
            elif data.startswith("confirm_receipt:"):
                await self.confirm_receipt(callback)
            elif data.startswith("open_chat:"):
                await self.open_deal_chat(callback, state)
            elif data.startswith("view_deal:"):
                deal_id = data.split(":")[1]
                user = await self.db.get_user_by_telegram_id(callback.from_user.id)
                await self.show_deal_details(callback.message, deal_id, user['anonymous_id'])
            elif data == "cancel_action":
                await state.clear()
                await callback.message.edit_text(
                    "❌ Действие отменено.",
                    reply_markup=Keyboards.back_to_main()
                )
            elif data == "main_menu":
                await callback.message.delete()
                await callback.message.answer(
                    "🏠 Главное меню",
                    reply_markup=Keyboards.main_menu()
                )
            
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error handling callback {data}: {e}")
            await callback.answer("❌ Произошла ошибка. Попробуйте позже.")

    async def accept_deal(self, callback: CallbackQuery):
        """Принять сделку"""
        deal_id = callback.data.split(":")[1]
        deal = await self.db.get_deal(deal_id)
        
        if not deal:
            await callback.answer("❌ Сделка не найдена!")
            return

        user = await self.db.get_user_by_telegram_id(callback.from_user.id)
        
        if user['anonymous_id'] != deal['seller_id']:
            await callback.answer("❌ Вы не можете принять эту сделку!")
            return

        if deal['status'] != 'waiting_seller':
            await callback.answer("❌ Сделка уже обработана!")
            return

        # Обновляем статус
        await self.db.update_deal_status(deal_id, 'active')
        
        # Уведомляем покупателя
        await self.db.add_notification(
            user_id=deal['buyer_id'],
            title="Сделка принята!",
            message=f"Продавец принял сделку: {deal['title']}",
            deal_id=deal_id
        )

        await callback.message.edit_text(
            f"✅ Сделка принята!\n\n"
            f"📋 {deal['title']}\n"
            f"💰 {deal['amount']:,.2f} ₽\n\n"
            f"Теперь вы можете общаться с покупателем через чат сделки.",
            reply_markup=Keyboards.deal_actions(deal_id, 'seller', 'active')
        )

    async def decline_deal(self, callback: CallbackQuery):
        """Отклонить сделку"""
        deal_id = callback.data.split(":")[1]
        deal = await self.db.get_deal(deal_id)
        
        if not deal:
            await callback.answer("❌ Сделка не найдена!")
            return

        user = await self.db.get_user_by_telegram_id(callback.from_user.id)
        
        if user['anonymous_id'] != deal['seller_id']:
            await callback.answer("❌ Вы не можете отклонить эту сделку!")
            return

        # Обновляем статус
        await self.db.update_deal_status(deal_id, 'cancelled')
        
        # Уведомляем покупателя
        await self.db.add_notification(
            user_id=deal['buyer_id'],
            title="Сделка отклонена",
            message=f"Продавец отклонил сделку: {deal['title']}",
            deal_id=deal_id
        )

        await callback.message.edit_text(
            f"❌ Сделка отклонена.\n\n"
            f"📋 {deal['title']}\n"
            f"💰 {deal['amount']:,.2f} ₽",
            reply_markup=Keyboards.back_to_main()
        )

    async def mark_goods_sent(self, callback: CallbackQuery):
        """Отметить товар как отправленный"""
        deal_id = callback.data.split(":")[1]
        deal = await self.db.get_deal(deal_id)
        
        if not deal:
            await callback.answer("❌ Сделка не найдена!")
            return

        user = await self.db.get_user_by_telegram_id(callback.from_user.id)
        
        if user['anonymous_id'] != deal['seller_id']:
            await callback.answer("❌ Только продавец может отметить товар как отправленный!")
            return

        # Обновляем статус
        await self.db.update_deal_status(deal_id, 'goods_sent')
        
        # Уведомляем покупателя
        await self.db.add_notification(
            user_id=deal['buyer_id'],
            title="Товар отправлен!",
            message=f"Продавец отправил товар по сделке: {deal['title']}",
            deal_id=deal_id
        )

        await callback.message.edit_text(
            f"📦 Товар отмечен как отправленный!\n\n"
            f"📋 {deal['title']}\n"
            f"💰 {deal['amount']:,.2f} ₽\n\n"
            f"Покупатель получил уведомление. Ожидайте подтверждения получения.",
            reply_markup=Keyboards.deal_actions(deal_id, 'seller', 'goods_sent')
        )

    async def confirm_receipt(self, callback: CallbackQuery):
        """Подтвердить получение товара"""
        deal_id = callback.data.split(":")[1]
        deal = await self.db.get_deal(deal_id)
        
        if not deal:
            await callback.answer("❌ Сделка не найдена!")
            return

        user = await self.db.get_user_by_telegram_id(callback.from_user.id)
        
        if user['anonymous_id'] != deal['buyer_id']:
            await callback.answer("❌ Только покупатель может подтвердить получение!")
            return

        # Обновляем статус
        await self.db.update_deal_status(deal_id, 'completed')
        
        # Уведомляем продавца
        await self.db.add_notification(
            user_id=deal['seller_id'],
            title="Сделка завершена!",
            message=f"Покупатель подтвердил получение товара: {deal['title']}",
            deal_id=deal_id
        )

        await callback.message.edit_text(
            f"✅ Сделка успешно завершена!\n\n"
            f"📋 {deal['title']}\n"
            f"💰 {deal['amount']:,.2f} ₽\n\n"
            f"Спасибо за использование нашего сервиса!",
            reply_markup=Keyboards.back_to_main()
        )

    async def open_deal_chat(self, callback: CallbackQuery, state: FSMContext):
        """Открыть чат сделки"""
        deal_id = callback.data.split(":")[1]
        deal = await self.db.get_deal(deal_id)
        
        if not deal:
            await callback.answer("❌ Сделка не найдена!")
            return

        user = await self.db.get_user_by_telegram_id(callback.from_user.id)
        
        # Проверяем права доступа
        if user['anonymous_id'] not in [deal['buyer_id'], deal['seller_id']]:
            await callback.answer("❌ У вас нет доступа к этому чату!")
            return

        # Получаем последние сообщения
        messages = await self.db.get_deal_messages(deal_id, limit=20)
        
        chat_text = f"💬 Чат сделки: {deal['title']}\n\n"
        
        if not messages:
            chat_text += "Сообщений пока нет. Начните общение!"
        else:
            for msg in messages[-10:]:  # Показываем последние 10 сообщений
                sender_role = "Вы" if msg['sender_id'] == user['anonymous_id'] else "Собеседник"
                timestamp = msg['timestamp'][:16]  # Убираем секунды
                chat_text += f"[{timestamp}] {sender_role}: {msg['content']}\n"

        # Сохраняем состояние чата
        user_chat_states[callback.from_user.id] = deal_id

        await callback.message.edit_text(
            chat_text,
            reply_markup=Keyboards.deal_chat_actions(deal_id)
        )

    async def handle_chat_message(self, message: Message):
        """Обработка сообщений в чате сделки"""
        user_id = message.from_user.id
        
        if user_id not in user_chat_states:
            return  # Пользователь не в чате сделки

        deal_id = user_chat_states[user_id]
        user = await self.db.get_user_by_telegram_id(user_id)
        
        # Добавляем сообщение в базу
        await self.db.add_message(
            deal_id=deal_id,
            sender_id=user['anonymous_id'],
            content=message.text,
            message_type='text'
        )

        # Уведомляем другую сторону
        deal = await self.db.get_deal(deal_id)
        other_party = deal['seller_id'] if user['anonymous_id'] == deal['buyer_id'] else deal['buyer_id']
        
        await self.db.add_notification(
            user_id=other_party,
            title="Новое сообщение",
            message=f"Сообщение в чате сделки: {deal['title']}",
            deal_id=deal_id
        )

        await message.answer(
            "✅ Сообщение отправлено!",
            reply_markup=Keyboards.deal_chat_actions(deal_id)
        )


def setup_handlers(dp, db: Database):
    """Настройка обработчиков"""
    handlers = Handlers(db)
    
    # Команды
    dp.message.register(handlers.cmd_start, Command("start"))
    
    # Главное меню
    dp.message.register(
        handlers.handle_main_menu,
        F.text.in_(["💼 Мои сделки", "🆕 Создать сделку", "🔍 Найти сделку", 
                   "📊 Профиль", "🔔 Уведомления", "ℹ️ Помощь"])
    )
    
    # Создание сделки
    dp.message.register(handlers.process_seller_id, DealCreationStates.waiting_seller_id)
    dp.message.register(handlers.process_deal_title, DealCreationStates.waiting_title)
    dp.message.register(handlers.process_deal_description, DealCreationStates.waiting_description)
    dp.message.register(handlers.process_deal_amount, DealCreationStates.waiting_amount)
    
    # Поиск сделки
    dp.message.register(handlers.process_find_deal, FindDealStates.waiting_deal_id)
    
    # Сообщения в чате (когда пользователь в состоянии чата)
    dp.message.register(handlers.handle_chat_message, F.text)
    
    # Callback-запросы
    dp.callback_query.register(handlers.handle_callback)