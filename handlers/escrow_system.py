from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.keyboards import Keyboards
from database.database import db_manager
from database.models import Transaction, Chat, User, TransactionStatus
from config import Config
import random
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Conversation states for escrow
(PRICE_CONFIRMATION, COMMISSION_SELECTION, PAYMENT_DETAILS, 
 PAYMENT_PROCESSING, VERIFICATION_VIDEO, TRANSACTION_PROGRESS,
 RATING_REVIEW) = range(7)

class EscrowHandler:
    
    @staticmethod
    async def initiate_transaction(query, context, chat_id: int):
        """Stage 1: Initiate transaction"""
        with db_manager.get_session() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            
            if not chat:
                await query.edit_message_text("❌ Чат не найден.")
                return ConversationHandler.END
            
            # Check if post has a fixed price
            if chat.post.price and chat.post.price_type.value == "fixed":
                await query.edit_message_text(
                    f"🤝 Начинаем сделку!\n\n"
                    f"📝 Товар: {chat.post.title}\n"
                    f"💰 Цена: {chat.post.price} грн\n\n"
                    f"Вы согласны с этой ценой?",
                    reply_markup=Keyboards.yes_no(f"confirm_price_{chat_id}_{chat.post.price}", f"suggest_price_{chat_id}")
                )
            else:
                await query.edit_message_text(
                    f"🤝 Начинаем сделку!\n\n"
                    f"📝 Товар: {chat.post.title}\n"
                    f"💰 Цена: договорная\n\n"
                    "Введите желаемую цену в гривнах:"
                )
                context.user_data['pending_chat_id'] = chat_id
                return PRICE_CONFIRMATION
    
    @staticmethod
    async def handle_price_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle price confirmation or input"""
        query = update.callback_query
        
        if query:
            await query.answer()
            
            if query.data.startswith("confirm_price_"):
                parts = query.data.split("_")
                chat_id = int(parts[2])
                price = float(parts[3])
                
                context.user_data['transaction_chat_id'] = chat_id
                context.user_data['transaction_price'] = price
                
                # Notify other party
                await EscrowHandler._notify_other_party_price(query, context, chat_id, price)
                return COMMISSION_SELECTION
                
            elif query.data.startswith("suggest_price_"):
                chat_id = int(query.data.split("_")[2])
                await query.edit_message_text(
                    "💰 Введите желаемую цену в гривнах:"
                )
                context.user_data['pending_chat_id'] = chat_id
                return PRICE_CONFIRMATION
                
            elif query.data.startswith("accept_price_"):
                parts = query.data.split("_")
                chat_id = int(parts[2])
                price = float(parts[3])
                
                context.user_data['transaction_chat_id'] = chat_id
                context.user_data['transaction_price'] = price
                
                await query.edit_message_text(
                    f"✅ Цена {price} грн согласована!\n\n"
                    "Переходим к выбору способа оплаты комиссии."
                )
                
                await EscrowHandler._show_commission_options(query, context)
                return COMMISSION_SELECTION
                
            elif query.data.startswith("reject_price_"):
                await query.edit_message_text(
                    "❌ Цена отклонена. Предложите свою цену:"
                )
                chat_id = int(query.data.split("_")[2])
                context.user_data['pending_chat_id'] = chat_id
                return PRICE_CONFIRMATION
        
        else:
            # Handle text input for price
            try:
                price = float(update.message.text)
                if price < Config.MIN_TRANSACTION_AMOUNT:
                    await update.message.reply_text(
                        f"❌ Минимальная сумма сделки: {Config.MIN_TRANSACTION_AMOUNT} грн"
                    )
                    return PRICE_CONFIRMATION
                
                chat_id = context.user_data.get('pending_chat_id')
                if not chat_id:
                    await update.message.reply_text("❌ Ошибка. Начните сделку заново.")
                    return ConversationHandler.END
                
                context.user_data['transaction_price'] = price
                context.user_data['transaction_chat_id'] = chat_id
                
                # Notify other party about price proposal
                await EscrowHandler._notify_other_party_price(update, context, chat_id, price)
                return COMMISSION_SELECTION
                
            except ValueError:
                await update.message.reply_text(
                    "❌ Пожалуйста, введите корректную цену (только число):"
                )
                return PRICE_CONFIRMATION
    
    @staticmethod
    async def _notify_other_party_price(update_or_query, context, chat_id: int, price: float):
        """Notify other party about price proposal"""
        with db_manager.get_session() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            
            current_user_id = update_or_query.from_user.id
            current_user = session.query(User).filter(User.telegram_id == current_user_id).first()
            
            # Determine other party
            other_user_id = chat.user1_id if chat.user2_id == current_user.id else chat.user2_id
            other_user = session.query(User).filter(User.id == other_user_id).first()
            
            if other_user:
                try:
                    notification = f"💰 Предложение по сделке\n\n"
                    notification += f"📝 Товар: {chat.post.title}\n"
                    notification += f"💵 Предложенная цена: {price} грн\n"
                    notification += f"👤 От: {current_user.first_name}\n\n"
                    notification += "Принимаете эту цену?"
                    
                    await context.bot.send_message(
                        chat_id=other_user.telegram_id,
                        text=notification,
                        reply_markup=Keyboards.yes_no(
                            f"accept_price_{chat_id}_{price}",
                            f"reject_price_{chat_id}"
                        )
                    )
                except Exception as e:
                    logger.error(f"Failed to notify other party: {e}")
    
    @staticmethod
    async def _show_commission_options(query, context):
        """Stage 2: Show commission payment options"""
        price = context.user_data.get('transaction_price', 0)
        commission = price * Config.ESCROW_COMMISSION
        
        commission_text = f"💳 Комиссия за гарантию: {commission:.2f} грн ({Config.ESCROW_COMMISSION*100}%)\n\n"
        commission_text += "Кто будет оплачивать комиссию?"
        
        await query.edit_message_text(
            commission_text,
            reply_markup=Keyboards.commission_split()
        )
    
    @staticmethod
    async def handle_commission_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle commission payment selection"""
        query = update.callback_query
        await query.answer()
        
        price = context.user_data.get('transaction_price', 0)
        commission = price * Config.ESCROW_COMMISSION
        
        if query.data == "commission_seller":
            context.user_data['commission_payer'] = 'seller'
            total_seller = price + commission
            await query.edit_message_text(
                f"✅ Продавец оплачивает комиссию\n\n"
                f"💰 Покупатель платит: {price} грн\n"
                f"💳 Продавец получит: {price} грн\n"
                f"🏦 Комиссия с продавца: {commission:.2f} грн\n\n"
                "Переходим к указанию реквизитов продавца."
            )
            
        elif query.data == "commission_buyer":
            context.user_data['commission_payer'] = 'buyer'
            total_buyer = price + commission
            await query.edit_message_text(
                f"✅ Покупатель оплачивает комиссию\n\n"
                f"💰 Покупатель платит: {total_buyer:.2f} грн\n"
                f"💳 Продавец получит: {price} грн\n"
                f"🏦 Комиссия с покупателя: {commission:.2f} грн\n\n"
                "Переходим к указанию реквизитов продавца."
            )
            
        elif query.data == "commission_split":
            context.user_data['commission_payer'] = 'split'
            half_commission = commission / 2
            total_buyer = price + half_commission
            await query.edit_message_text(
                f"✅ Комиссия делится поровну\n\n"
                f"💰 Покупатель платит: {total_buyer:.2f} грн\n"
                f"💳 Продавец получит: {price - half_commission:.2f} грн\n"
                f"🏦 Комиссия с каждого: {half_commission:.2f} грн\n\n"
                "Переходим к указанию реквизитов продавца."
            )
        
        # Show payment methods for seller
        await EscrowHandler._request_seller_payment_details(query, context)
        return PAYMENT_DETAILS
    
    @staticmethod
    async def _request_seller_payment_details(query, context):
        """Stage 3: Request seller payment details"""
        await query.edit_message_text(
            "💳 Продавец, выберите способ получения средств:",
            reply_markup=Keyboards.payment_methods()
        )
    
    @staticmethod
    async def handle_payment_method_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment method selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "payment_ua_card":
            context.user_data['payment_method'] = 'ua_card'
            await query.edit_message_text(
                "💳 Введите номер UA-карты (16 цифр):"
            )
            
        elif query.data == "payment_crypto_ton":
            context.user_data['payment_method'] = 'crypto_ton'
            await query.edit_message_text(
                "₿ Введите TON кошелек:"
            )
            
        elif query.data == "payment_crypto_usdt":
            context.user_data['payment_method'] = 'crypto_usdt'
            await query.edit_message_text(
                "💰 Введите USDT кошелек (TRC20):"
            )
        
        return PAYMENT_DETAILS
    
    @staticmethod
    async def handle_payment_details_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment details input"""
        payment_info = update.message.text
        payment_method = context.user_data.get('payment_method')
        
        # Validate payment info based on method
        if payment_method == 'ua_card':
            if not payment_info.isdigit() or len(payment_info) != 16:
                await update.message.reply_text(
                    "❌ Неверный формат карты. Введите 16 цифр:"
                )
                return PAYMENT_DETAILS
                
        elif payment_method in ['crypto_ton', 'crypto_usdt']:
            if len(payment_info) < 20:
                await update.message.reply_text(
                    "❌ Неверный формат кошелька. Проверьте адрес:"
                )
                return PAYMENT_DETAILS
        
        context.user_data['payment_info'] = payment_info
        
        # Confirm payment details
        method_names = {
            'ua_card': 'UA-карта',
            'crypto_ton': 'TON кошелек',
            'crypto_usdt': 'USDT кошелек'
        }
        
        await update.message.reply_text(
            f"💳 Проверьте реквизиты:\n\n"
            f"Способ: {method_names[payment_method]}\n"
            f"Реквизиты: {payment_info}\n\n"
            "Все верно?",
            reply_markup=Keyboards.yes_no("confirm_payment_details", "edit_payment_details")
        )
        
        return PAYMENT_PROCESSING
    
    @staticmethod
    async def handle_payment_details_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment details confirmation"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_payment_details":
            # Create transaction record
            await EscrowHandler._create_transaction_record(query, context)
            return VERIFICATION_VIDEO
            
        elif query.data == "edit_payment_details":
            await query.edit_message_text(
                "💳 Введите реквизиты заново:",
                reply_markup=Keyboards.payment_methods()
            )
            return PAYMENT_DETAILS
    
    @staticmethod
    async def _create_transaction_record(query, context):
        """Create transaction in database and request payment"""
        chat_id = context.user_data.get('transaction_chat_id')
        price = context.user_data.get('transaction_price')
        commission_payer = context.user_data.get('commission_payer')
        payment_method = context.user_data.get('payment_method')
        payment_info = context.user_data.get('payment_info')
        
        with db_manager.get_session() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            
            # Determine seller and buyer
            current_user = session.query(User).filter(User.telegram_id == query.from_user.id).first()
            if current_user.id == chat.user1_id:  # Post author is seller
                seller_id = chat.user1_id
                buyer_id = chat.user2_id
            else:
                seller_id = chat.user2_id
                buyer_id = chat.user1_id
            
            commission = price * Config.ESCROW_COMMISSION
            
            # Create transaction
            transaction = Transaction(
                chat_id=chat_id,
                seller_id=seller_id,
                buyer_id=buyer_id,
                amount=price,
                commission=commission,
                commission_payer=commission_payer,
                payment_method=payment_method,
                seller_payment_info=json.dumps({
                    'method': payment_method,
                    'details': payment_info
                }),
                status=TransactionStatus.PAYMENT_PENDING,
                payment_deadline=datetime.now() + timedelta(hours=24),
                completion_deadline=datetime.now() + timedelta(hours=Config.TRANSACTION_TIMEOUT_HOURS + 24)
            )
            
            session.add(transaction)
            session.flush()
            
            # Update chat status
            from database.models import ChatStatus
            chat.status = ChatStatus.TRANSACTION
            
            context.user_data['transaction_id'] = transaction.id
            
            # Calculate payment amounts
            await EscrowHandler._request_payment(query, context, transaction)
    
    @staticmethod
    async def _request_payment(query, context, transaction):
        """Stage 4: Request payment from buyer"""
        commission = transaction.commission
        
        if transaction.commission_payer == 'buyer':
            total_to_pay = transaction.amount + commission
            commission_text = f"🏦 Комиссия: {commission:.2f} грн"
        elif transaction.commission_payer == 'seller':
            total_to_pay = transaction.amount
            commission_text = f"🏦 Комиссия оплачивает продавец"
        else:  # split
            half_commission = commission / 2
            total_to_pay = transaction.amount + half_commission
            commission_text = f"🏦 Ваша часть комиссии: {half_commission:.2f} грн"
        
        await query.edit_message_text(
            f"💰 Этап 4: Оплата\n\n"
            f"💵 Сумма к оплате: {total_to_pay:.2f} грн\n"
            f"{commission_text}\n\n"
            f"⏰ Срок оплаты: 24 часа\n\n"
            "Переведите указанную сумму на наши реквизиты и подтвердите платеж.\n\n"
            "🏦 Реквизиты для оплаты:\n"
            "Карта: 1234 5678 9012 3456\n"
            "Получатель: ООО Игровой Маркет"
        )
        
        # Notify both parties
        await EscrowHandler._notify_payment_status(context, transaction, 'payment_requested')
    
    @staticmethod
    async def _notify_payment_status(context, transaction, status):
        """Notify both parties about payment status"""
        with db_manager.get_session() as session:
            seller = session.query(User).filter(User.id == transaction.seller_id).first()
            buyer = session.query(User).filter(User.id == transaction.buyer_id).first()
            
            if status == 'payment_requested':
                # Notify buyer
                try:
                    await context.bot.send_message(
                        chat_id=buyer.telegram_id,
                        text=f"💰 Ожидается ваша оплата\n\n"
                             f"Сумма: {transaction.amount + (transaction.commission if transaction.commission_payer == 'buyer' else 0):.2f} грн\n"
                             f"⏰ Срок: 24 часа"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify buyer: {e}")
                
                # Notify seller
                try:
                    await context.bot.send_message(
                        chat_id=seller.telegram_id,
                        text="💰 Покупатель уведомлен об оплате. Ожидайте поступления средств."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify seller: {e}")
            
            elif status == 'payment_received':
                # Notify both parties
                try:
                    await context.bot.send_message(
                        chat_id=buyer.telegram_id,
                        text="✅ Платеж получен! Средства зарезервированы."
                    )
                    await context.bot.send_message(
                        chat_id=seller.telegram_id,
                        text="✅ Платеж получен! Переходим к проверке продавца."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify payment received: {e}")
    
    @staticmethod
    async def handle_payment_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment confirmation (admin function)"""
        # This would be called by admin when payment is received
        transaction_id = context.user_data.get('transaction_id')
        
        with db_manager.get_session() as session:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            
            if transaction:
                transaction.status = TransactionStatus.VERIFICATION_PENDING
                
                # Generate random verification phrase
                verification_phrase = random.choice(Config.VERIFICATION_PHRASES)
                transaction.verification_phrase = verification_phrase
                
                await EscrowHandler._request_seller_verification(update, context, transaction)
    
    @staticmethod
    async def _request_seller_verification(update, context, transaction):
        """Stage 5: Request seller verification video"""
        with db_manager.get_session() as session:
            seller = session.query(User).filter(User.id == transaction.seller_id).first()
            
            try:
                verification_text = f"🎥 Этап 5: Проверка продавца\n\n"
                verification_text += f"Запишите видео-кружок, держа документ в руках и произнесите фразу:\n\n"
                verification_text += f"🗣 \"{transaction.verification_phrase}\"\n\n"
                verification_text += "Видео поступит модераторам для проверки."
                
                await context.bot.send_message(
                    chat_id=seller.telegram_id,
                    text=verification_text
                )
            except Exception as e:
                logger.error(f"Failed to request verification: {e}")
    
    @staticmethod
    async def handle_verification_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle verification video upload"""
        if update.message.video_note:
            user_id = update.effective_user.id
            video_file_id = update.message.video_note.file_id
            
            with db_manager.get_session() as session:
                # Find pending verification transaction
                user = session.query(User).filter(User.telegram_id == user_id).first()
                transaction = session.query(Transaction).filter(
                    Transaction.seller_id == user.id,
                    Transaction.status == TransactionStatus.VERIFICATION_PENDING
                ).first()
                
                if transaction:
                    transaction.verification_video_file_id = video_file_id
                    
                    await update.message.reply_text(
                        "✅ Видео получено! Отправлено модераторам на проверку.\n\n"
                        "Ожидайте подтверждения."
                    )
                    
                    # Send to moderators
                    await EscrowHandler._send_verification_to_moderators(context, transaction)
                else:
                    await update.message.reply_text(
                        "❌ Активная сделка с ожидающей проверкой не найдена."
                    )
        else:
            await update.message.reply_text(
                "❌ Пожалуйста, отправьте видео-кружок для проверки."
            )
    
    @staticmethod
    async def _send_verification_to_moderators(context, transaction):
        """Send verification video to moderators"""
        try:
            with db_manager.get_session() as session:
                seller = session.query(User).filter(User.id == transaction.seller_id).first()
                
                verification_text = f"🎥 Проверка продавца\n\n"
                verification_text += f"👤 Продавец: {seller.first_name} (@{seller.username or 'нет'})\n"
                verification_text += f"🆔 ID: {seller.telegram_id}\n"
                verification_text += f"💰 Сумма сделки: {transaction.amount} грн\n"
                verification_text += f"🗣 Требуемая фраза: \"{transaction.verification_phrase}\"\n\n"
                verification_text += "Проверьте видео и подтвердите личность продавца."
                
                await context.bot.send_video_note(
                    chat_id=Config.MODERATOR_GROUP_ID,
                    video_note=transaction.verification_video_file_id,
                    caption=verification_text,
                    reply_markup=Keyboards.admin_transaction_actions(transaction.id)
                )
        except Exception as e:
            logger.error(f"Failed to send verification to moderators: {e}")
    
    @staticmethod
    async def handle_verification_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle verification approval by moderator"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("admin_confirm_"):
            transaction_id = int(query.data.split("_")[2])
            
            with db_manager.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                
                if transaction:
                    transaction.status = TransactionStatus.IN_PROGRESS
                    transaction.is_verified = True
                    
                    await query.edit_message_text(
                        f"✅ Проверка продавца подтверждена!\n\n"
                        f"Сделка переведена в активную фазу."
                    )
                    
                    # Start transaction timer
                    await EscrowHandler._start_transaction_phase(context, transaction)
        
        elif query.data.startswith("admin_reject_"):
            transaction_id = int(query.data.split("_")[2])
            
            with db_manager.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                
                if transaction:
                    transaction.status = TransactionStatus.CANCELLED
                    
                    await query.edit_message_text(
                        f"❌ Проверка продавца отклонена.\n\n"
                        f"Сделка отменена, средства возвращаются покупателю."
                    )
                    
                    # Notify parties about cancellation
                    await EscrowHandler._notify_transaction_cancelled(context, transaction, "Проверка продавца не пройдена")
    
    @staticmethod
    async def _start_transaction_phase(context, transaction):
        """Stage 6: Start active transaction phase"""
        with db_manager.get_session() as session:
            seller = session.query(User).filter(User.id == transaction.seller_id).first()
            buyer = session.query(User).filter(User.id == transaction.buyer_id).first()
            
            try:
                # Notify both parties
                transaction_text = f"🤝 Этап 6: Активная сделка\n\n"
                transaction_text += f"✅ Все проверки пройдены!\n"
                transaction_text += f"⏰ У вас есть {Config.TRANSACTION_TIMEOUT_HOURS} часа на завершение сделки.\n\n"
                transaction_text += "Используйте кнопки ниже для управления сделкой:"
                
                await context.bot.send_message(
                    chat_id=seller.telegram_id,
                    text=transaction_text,
                    reply_markup=Keyboards.transaction_actions(transaction.id)
                )
                
                await context.bot.send_message(
                    chat_id=buyer.telegram_id,
                    text=transaction_text,
                    reply_markup=Keyboards.transaction_actions(transaction.id)
                )
                
            except Exception as e:
                logger.error(f"Failed to start transaction phase: {e}")
    
    @staticmethod
    async def handle_transaction_completion(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle transaction completion confirmation"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("confirm_transaction_"):
            transaction_id = int(query.data.split("_")[2])
            user_id = query.from_user.id
            
            with db_manager.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                user = session.query(User).filter(User.telegram_id == user_id).first()
                
                if not transaction:
                    await query.edit_message_text("❌ Сделка не найдена.")
                    return
                
                # Check if both parties confirmed
                redis_client = db_manager.get_redis()
                confirmation_key = f"transaction_confirmations_{transaction_id}"
                
                # Add user confirmation
                redis_client.sadd(confirmation_key, str(user.id))
                redis_client.expire(confirmation_key, 3600)  # 1 hour expiry
                
                confirmations = redis_client.smembers(confirmation_key)
                
                if len(confirmations) >= 2:
                    # Both parties confirmed
                    transaction.status = TransactionStatus.COMPLETED
                    transaction.completed_at = datetime.now()
                    
                    await query.edit_message_text(
                        "✅ Обе стороны подтвердили завершение сделки!\n\n"
                        "Сделка передана гаранту для финального подтверждения."
                    )
                    
                    # Send to moderators for final approval
                    await EscrowHandler._request_final_approval(context, transaction)
                    
                else:
                    await query.edit_message_text(
                        "✅ Ваше подтверждение принято.\n\n"
                        "Ожидаем подтверждения от другой стороны."
                    )
        
        elif query.data.startswith("cancel_transaction_"):
            transaction_id = int(query.data.split("_")[2])
            
            await query.edit_message_text(
                "❌ Вы действительно хотите отменить сделку?\n\n"
                "Это действие нельзя будет отменить.",
                reply_markup=Keyboards.yes_no(f"final_cancel_{transaction_id}", f"keep_transaction_{transaction_id}")
            )
        
        elif query.data.startswith("help_transaction_"):
            transaction_id = int(query.data.split("_")[2])
            
            await query.edit_message_text(
                "🆘 Запрос помощи отправлен администратору.\n\n"
                "Опишите вашу проблему:"
            )
            
            # Notify moderators
            await EscrowHandler._notify_help_request(context, transaction_id, query.from_user.id)
    
    @staticmethod
    async def _request_final_approval(context, transaction):
        """Request final approval from moderators"""
        try:
            with db_manager.get_session() as session:
                seller = session.query(User).filter(User.id == transaction.seller_id).first()
                buyer = session.query(User).filter(User.id == transaction.buyer_id).first()
                
                approval_text = f"🏁 Финальное подтверждение сделки\n\n"
                approval_text += f"💰 Сумма: {transaction.amount} грн\n"
                approval_text += f"🤵 Продавец: {seller.first_name} (@{seller.username or 'нет'})\n"
                approval_text += f"🛒 Покупатель: {buyer.first_name} (@{buyer.username or 'нет'})\n"
                approval_text += f"📅 Дата: {transaction.completed_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                approval_text += "Обе стороны подтвердили завершение сделки."
                
                await context.bot.send_message(
                    chat_id=Config.MODERATOR_GROUP_ID,
                    text=approval_text,
                    reply_markup=Keyboards.admin_transaction_actions(transaction.id)
                )
        except Exception as e:
            logger.error(f"Failed to request final approval: {e}")
    
    @staticmethod
    async def handle_final_transaction_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle final transaction approval by moderator"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("admin_confirm_"):
            transaction_id = int(query.data.split("_")[2])
            
            with db_manager.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                
                if transaction:
                    await query.edit_message_text(
                        f"✅ Сделка подтверждена и завершена!\n\n"
                        f"Средства переведены продавцу."
                    )
                    
                    # Process payment to seller
                    await EscrowHandler._process_seller_payment(context, transaction)
                    
                    # Start rating process
                    await EscrowHandler._start_rating_process(context, transaction)
    
    @staticmethod
    async def _process_seller_payment(context, transaction):
        """Process payment to seller"""
        # In real implementation, this would integrate with payment processor
        with db_manager.get_session() as session:
            seller = session.query(User).filter(User.id == transaction.seller_id).first()
            buyer = session.query(User).filter(User.id == transaction.buyer_id).first()
            
            # Calculate final amounts
            commission = transaction.commission
            if transaction.commission_payer == 'seller':
                seller_receives = transaction.amount - commission
            elif transaction.commission_payer == 'split':
                seller_receives = transaction.amount - (commission / 2)
            else:
                seller_receives = transaction.amount
            
            # Update user statistics
            seller.total_transactions += 1
            seller.total_amount += transaction.amount
            buyer.total_transactions += 1
            buyer.total_amount += transaction.amount
            
            try:
                await context.bot.send_message(
                    chat_id=seller.telegram_id,
                    text=f"💰 Средства переведены!\n\n"
                         f"Получено: {seller_receives:.2f} грн\n"
                         f"Способ: {transaction.payment_method}\n\n"
                         f"Спасибо за использование нашего сервиса!"
                )
                
                await context.bot.send_message(
                    chat_id=buyer.telegram_id,
                    text=f"✅ Сделка успешно завершена!\n\n"
                         f"Продавец получил оплату.\n"
                         f"Спасибо за использование нашего сервиса!"
                )
            except Exception as e:
                logger.error(f"Failed to notify payment processed: {e}")
    
    @staticmethod
    async def _start_rating_process(context, transaction):
        """Stage 7: Start rating and review process"""
        with db_manager.get_session() as session:
            seller = session.query(User).filter(User.id == transaction.seller_id).first()
            buyer = session.query(User).filter(User.id == transaction.buyer_id).first()
            
            try:
                rating_text = f"⭐ Этап 7: Оценка и отзыв\n\n"
                rating_text += f"Пожалуйста, оцените вашего партнера по сделке.\n"
                rating_text += f"Это поможет другим пользователям!"
                
                # Ask seller to rate buyer
                await context.bot.send_message(
                    chat_id=seller.telegram_id,
                    text=f"{rating_text}\n\nОцените покупателя {buyer.first_name}:",
                    reply_markup=Keyboards.rating_keyboard()
                )
                
                # Ask buyer to rate seller
                await context.bot.send_message(
                    chat_id=buyer.telegram_id,
                    text=f"{rating_text}\n\nОцените продавца {seller.first_name}:",
                    reply_markup=Keyboards.rating_keyboard()
                )
                
            except Exception as e:
                logger.error(f"Failed to start rating process: {e}")
    
    @staticmethod
    async def handle_rating_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle rating selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("rating_"):
            rating = int(query.data.split("_")[1])
            user_id = query.from_user.id
            
            # Store rating temporarily
            context.user_data['selected_rating'] = rating
            
            await query.edit_message_text(
                f"⭐ Вы поставили {rating} звёзд.\n\n"
                f"Теперь оставьте отзыв (или отправьте /skip чтобы пропустить):"
            )
            
            return RATING_REVIEW
    
    @staticmethod
    async def handle_review_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle review text input"""
        if update.message.text == "/skip":
            review_text = ""
        else:
            review_text = update.message.text[:500]  # Limit review length
        
        rating = context.user_data.get('selected_rating')
        user_id = update.effective_user.id
        
        # Save review to database
        with db_manager.get_session() as session:
            # Find the transaction and create review
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            # For now, we'll store the review. In production, you'd link it to specific transaction
            await update.message.reply_text(
                f"✅ Спасибо за отзыв!\n\n"
                f"⭐ Оценка: {rating}/5\n"
                f"💬 Отзыв: {review_text or 'Не указан'}\n\n"
                f"Теперь оцените наш сервис:"
            )
            
            # Ask for bot rating
            await update.message.reply_text(
                "🤖 Как вам наш сервис?",
                reply_markup=Keyboards.rating_keyboard()
            )
        
        return ConversationHandler.END
    
    @staticmethod
    async def _notify_transaction_cancelled(context, transaction, reason):
        """Notify parties about transaction cancellation"""
        with db_manager.get_session() as session:
            seller = session.query(User).filter(User.id == transaction.seller_id).first()
            buyer = session.query(User).filter(User.id == transaction.buyer_id).first()
            
            cancellation_text = f"❌ Сделка отменена\n\n"
            cancellation_text += f"Причина: {reason}\n"
            cancellation_text += f"Средства будут возвращены покупателю."
            
            try:
                await context.bot.send_message(chat_id=seller.telegram_id, text=cancellation_text)
                await context.bot.send_message(chat_id=buyer.telegram_id, text=cancellation_text)
            except Exception as e:
                logger.error(f"Failed to notify cancellation: {e}")
    
    @staticmethod
    async def _notify_help_request(context, transaction_id, user_id):
        """Notify moderators about help request"""
        try:
            with db_manager.get_session() as session:
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                user = session.query(User).filter(User.telegram_id == user_id).first()
                
                help_text = f"🆘 Запрос помощи\n\n"
                help_text += f"👤 От: {user.first_name} (@{user.username or 'нет'})\n"
                help_text += f"💰 Сделка: {transaction.amount} грн\n"
                help_text += f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                help_text += "Пользователь запросил помощь по активной сделке."
                
                await context.bot.send_message(
                    chat_id=Config.MODERATOR_GROUP_ID,
                    text=help_text,
                    reply_markup=Keyboards.admin_transaction_actions(transaction_id)
                )
        except Exception as e:
            logger.error(f"Failed to notify help request: {e}")