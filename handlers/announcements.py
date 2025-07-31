from telegram import Update, Message
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from utils.keyboards import Keyboards
from database.database import db_manager
from database.models import Post, Game, PostType, PriceType, User
from config import Config
import json
import random
import string
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Conversation states
(TYPE_SELECTION, PHOTOS_UPLOAD, DESCRIPTION_INPUT, PRICE_INPUT, 
 GAME_SELECTION, PIN_OFFER, SEARCH_WHAT, SEARCH_GAME, SEARCH_BUDGET,
 AUCTION_PHOTOS, AUCTION_DESC, AUCTION_GAME, AUCTION_MIN_PRICE, 
 AUCTION_TIMER) = range(14)

class AnnouncementHandler:
    
    @staticmethod
    async def start_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle announcement type selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "announce_create":
            await query.edit_message_text(
                "💰 Хотите продать или купить?",
                reply_markup=Keyboards.sell_or_buy()
            )
            return TYPE_SELECTION
            
        elif query.data == "announce_search":
            await query.edit_message_text(
                "🔍 Что вы ищете? Опишите товар или услугу:"
            )
            context.user_data['announcement_type'] = 'search'
            return SEARCH_WHAT
            
        elif query.data == "announce_auction":
            await AnnouncementHandler._show_auction_info(query, context)
            return AUCTION_PHOTOS
    
    @staticmethod
    async def handle_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle sell/buy type selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "type_sell":
            context.user_data['post_type'] = PostType.SELL
            await query.edit_message_text(
                "📸 Загрузите фото товара (до 10 фотографий).\n\n"
                "Когда загрузите все фото, отправьте команду /done"
            )
            context.user_data['photos'] = []
            return PHOTOS_UPLOAD
            
        elif query.data == "type_buy":
            context.user_data['post_type'] = PostType.BUY
            await query.edit_message_text(
                "📸 Загрузите фото примера того, что хотите купить (необязательно).\n\n"
                "Можете сразу перейти к описанию, отправив команду /skip"
            )
            context.user_data['photos'] = []
            return PHOTOS_UPLOAD
    
    @staticmethod
    async def handle_photo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo uploads"""
        if update.message.text == "/done":
            if not context.user_data.get('photos') and context.user_data['post_type'] == PostType.SELL:
                await update.message.reply_text(
                    "❌ Для продажи необходимо загрузить хотя бы одно фото."
                )
                return PHOTOS_UPLOAD
                
            await update.message.reply_text(
                "📝 Теперь опишите ваш товар:"
            )
            return DESCRIPTION_INPUT
            
        elif update.message.text == "/skip":
            await update.message.reply_text(
                "📝 Опишите ваш товар:"
            )
            return DESCRIPTION_INPUT
            
        elif update.message.photo:
            photos = context.user_data.get('photos', [])
            if len(photos) >= Config.MAX_PHOTOS:
                await update.message.reply_text(
                    f"❌ Максимум {Config.MAX_PHOTOS} фотографий."
                )
                return PHOTOS_UPLOAD
                
            photo_file_id = update.message.photo[-1].file_id
            photos.append(photo_file_id)
            context.user_data['photos'] = photos
            
            await update.message.reply_text(
                f"✅ Фото {len(photos)}/{Config.MAX_PHOTOS} загружено.\n"
                "Отправьте /done когда закончите."
            )
            return PHOTOS_UPLOAD
        else:
            await update.message.reply_text(
                "❌ Пожалуйста, загрузите фото или отправьте /done"
            )
            return PHOTOS_UPLOAD
    
    @staticmethod
    async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle description input"""
        description = update.message.text
        if len(description) > 1000:
            await update.message.reply_text(
                "❌ Описание слишком длинное. Максимум 1000 символов."
            )
            return DESCRIPTION_INPUT
            
        context.user_data['description'] = description
        
        await update.message.reply_text(
            "💰 Выберите тип цены:",
            reply_markup=Keyboards.price_type()
        )
        return PRICE_INPUT
    
    @staticmethod
    async def handle_price_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle price type selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "price_fixed":
            context.user_data['price_type'] = PriceType.FIXED
            await query.edit_message_text(
                "💵 Введите цену в гривнах (только число):"
            )
            return PRICE_INPUT
            
        elif query.data == "price_negotiable":
            context.user_data['price_type'] = PriceType.NEGOTIABLE
            context.user_data['price'] = None
            await AnnouncementHandler._show_games_selection(query, context)
            return GAME_SELECTION
            
        elif query.data == "price_none":
            context.user_data['price_type'] = PriceType.NO_PRICE
            context.user_data['price'] = None
            await AnnouncementHandler._show_games_selection(query, context)
            return GAME_SELECTION
    
    @staticmethod
    async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle price numeric input"""
        try:
            price = float(update.message.text)
            if price <= 0:
                raise ValueError("Price must be positive")
                
            context.user_data['price'] = price
            await AnnouncementHandler._show_games_selection_message(update, context)
            return GAME_SELECTION
            
        except ValueError:
            await update.message.reply_text(
                "❌ Пожалуйста, введите корректную цену (только число):"
            )
            return PRICE_INPUT
    
    @staticmethod
    async def _show_games_selection(query, context):
        """Show games selection keyboard"""
        with db_manager.get_session() as session:
            games = session.query(Game).filter(Game.is_active == True).all()
            
            await query.edit_message_text(
                "🎮 Выберите игру из списка:",
                reply_markup=Keyboards.games_pagination(games)
            )
    
    @staticmethod
    async def _show_games_selection_message(update, context):
        """Show games selection for message updates"""
        with db_manager.get_session() as session:
            games = session.query(Game).filter(Game.is_active == True).all()
            
            await update.message.reply_text(
                "🎮 Выберите игру из списка:",
                reply_markup=Keyboards.games_pagination(games)
            )
    
    @staticmethod
    async def handle_game_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle game selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "game_none":
            context.user_data['game_id'] = None
        elif query.data.startswith("game_"):
            game_id = int(query.data.split("_")[1])
            context.user_data['game_id'] = game_id
        elif query.data.startswith("games_page_"):
            # Handle pagination
            page = int(query.data.split("_")[2])
            with db_manager.get_session() as session:
                games = session.query(Game).filter(Game.is_active == True).all()
                await query.edit_message_reply_markup(
                    reply_markup=Keyboards.games_pagination(games, page)
                )
            return GAME_SELECTION
        else:
            return GAME_SELECTION
        
        # Show pin offer
        await query.edit_message_text(
            f"📌 Хотите закрепить объявление за {Config.PIN_PRICE} грн?\n\n"
            "Закреплённые объявления показываются в топе канала.",
            reply_markup=Keyboards.yes_no("pin_yes", "pin_no")
        )
        return PIN_OFFER
    
    @staticmethod
    async def handle_pin_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pin offer response"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['pin_post'] = query.data == "pin_yes"
        
        # Create and publish post
        await AnnouncementHandler._create_post(query, context)
        return ConversationHandler.END
    
    @staticmethod
    async def _create_post(query, context):
        """Create and publish post"""
        user_id = query.from_user.id
        
        with db_manager.get_session() as session:
            # Get user
            user = session.query(User).filter(User.telegram_id == user_id).first()
            
            # Generate unique ID
            unique_id = AnnouncementHandler._generate_unique_id()
            
            # Create post
            post = Post(
                unique_id=unique_id,
                user_id=user.id,
                game_id=context.user_data.get('game_id'),
                post_type=context.user_data['post_type'],
                title=context.user_data['description'][:100],  # First 100 chars as title
                description=context.user_data['description'],
                price=context.user_data.get('price'),
                price_type=context.user_data['price_type'],
                photos=json.dumps(context.user_data.get('photos', [])),
                is_pinned=context.user_data.get('pin_post', False),
                expires_at=datetime.now() + timedelta(hours=Config.POST_DURATION_HOURS)
            )
            
            session.add(post)
            session.flush()
            
            # Publish to channel
            message_id = await AnnouncementHandler._publish_to_channel(query, post, context)
            post.channel_message_id = message_id
            
            # Calculate total cost
            total_cost = Config.POST_PRICE
            if context.user_data.get('pin_post'):
                total_cost += Config.PIN_PRICE
            
            await query.edit_message_text(
                f"✅ Объявление #{unique_id} создано!\n\n"
                f"💰 К оплате: {total_cost} грн\n"
                f"⏰ Объявление будет активно {Config.POST_DURATION_HOURS} часов\n\n"
                "Объявление опубликовано в канале!"
            )
    
    @staticmethod
    async def _publish_to_channel(query, post, context):
        """Publish post to channel"""
        # Format post message
        game_text = ""
        if post.game_id:
            with db_manager.get_session() as session:
                game = session.query(Game).filter(Game.id == post.game_id).first()
                if game:
                    game_text = f"#{game.hashtag}"
        
        price_text = ""
        if post.price_type == PriceType.FIXED and post.price:
            price_text = f"💰 {post.price} грн"
        elif post.price_type == PriceType.NEGOTIABLE:
            price_text = "💬 Договорная"
        elif post.price_type == PriceType.NO_PRICE:
            price_text = "🆓 Цена не указана"
        
        type_emoji = "💰" if post.post_type == PostType.SELL else "🛒"
        type_text = "Продам" if post.post_type == PostType.SELL else "Куплю"
        
        message_text = f"{type_emoji} {type_text}\n\n"
        message_text += f"📝 {post.description}\n\n"
        if price_text:
            message_text += f"{price_text}\n"
        if game_text:
            message_text += f"🎮 {game_text}\n"
        message_text += f"\n#{post.unique_id}"
        
        # Send to channel
        photos = json.loads(post.photos) if post.photos else []
        
        try:
            if photos:
                # Send with photo
                message = await context.bot.send_photo(
                    chat_id=Config.CHANNEL_ID,
                    photo=photos[0],
                    caption=message_text,
                    reply_markup=Keyboards.open_in_bot(post.unique_id)
                )
            else:
                # Send text only
                message = await context.bot.send_message(
                    chat_id=Config.CHANNEL_ID,
                    text=message_text,
                    reply_markup=Keyboards.open_in_bot(post.unique_id)
                )
            
            # Pin if requested
            if post.is_pinned:
                await context.bot.pin_chat_message(
                    chat_id=Config.CHANNEL_ID,
                    message_id=message.message_id
                )
            
            return message.message_id
            
        except Exception as e:
            logger.error(f"Failed to publish to channel: {e}")
            return None
    
    @staticmethod
    def _generate_unique_id():
        """Generate unique post ID"""
        return ''.join(random.choices(string.digits, k=8))
    
    # Search functionality
    @staticmethod
    async def handle_search_what(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle search 'what' input"""
        context.user_data['search_what'] = update.message.text
        
        with db_manager.get_session() as session:
            games = session.query(Game).filter(Game.is_active == True).all()
            
            await update.message.reply_text(
                "🎮 Для какой игры?",
                reply_markup=Keyboards.games_pagination(games)
            )
        return SEARCH_GAME
    
    @staticmethod
    async def handle_search_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle search game selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "game_none":
            context.user_data['search_game_id'] = None
        elif query.data.startswith("game_"):
            game_id = int(query.data.split("_")[1])
            context.user_data['search_game_id'] = game_id
        elif query.data.startswith("games_page_"):
            # Handle pagination
            page = int(query.data.split("_")[2])
            with db_manager.get_session() as session:
                games = session.query(Game).filter(Game.is_active == True).all()
                await query.edit_message_reply_markup(
                    reply_markup=Keyboards.games_pagination(games, page)
                )
            return SEARCH_GAME
        else:
            return SEARCH_GAME
        
        await query.edit_message_text(
            "💰 Укажите примерный бюджет:",
            reply_markup=Keyboards.price_type()
        )
        return SEARCH_BUDGET
    
    @staticmethod
    async def handle_search_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle search budget selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "price_fixed":
            await query.edit_message_text(
                "💵 Введите сумму бюджета в гривнах:"
            )
            return SEARCH_BUDGET
        elif query.data in ["price_negotiable", "price_none"]:
            context.user_data['search_budget'] = None
            context.user_data['search_budget_type'] = query.data
            await AnnouncementHandler._create_search_post(query, context)
            return ConversationHandler.END
    
    @staticmethod
    async def handle_search_budget_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle search budget numeric input"""
        try:
            budget = float(update.message.text)
            if budget <= 0:
                raise ValueError("Budget must be positive")
                
            context.user_data['search_budget'] = budget
            context.user_data['search_budget_type'] = 'fixed'
            await AnnouncementHandler._create_search_post_message(update, context)
            return ConversationHandler.END
            
        except ValueError:
            await update.message.reply_text(
                "❌ Пожалуйста, введите корректную сумму:"
            )
            return SEARCH_BUDGET
    
    @staticmethod
    async def _create_search_post(query, context):
        """Create search post"""
        await AnnouncementHandler._create_search_post_common(query.from_user.id, context, query.bot, query.edit_message_text)
    
    @staticmethod
    async def _create_search_post_message(update, context):
        """Create search post from message"""
        await AnnouncementHandler._create_search_post_common(update.effective_user.id, context, update.bot, update.message.reply_text)
    
    @staticmethod
    async def _create_search_post_common(user_id, context, bot, reply_func):
        """Common search post creation logic"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            unique_id = AnnouncementHandler._generate_unique_id()
            
            # Create search post
            post = Post(
                unique_id=unique_id,
                user_id=user.id,
                game_id=context.user_data.get('search_game_id'),
                post_type=PostType.SEARCH,
                title=f"Ищу: {context.user_data['search_what'][:50]}",
                description=context.user_data['search_what'],
                price=context.user_data.get('search_budget'),
                price_type=PriceType.FIXED if context.user_data.get('search_budget') else PriceType.NEGOTIABLE,
                expires_at=datetime.now() + timedelta(hours=Config.POST_DURATION_HOURS)
            )
            
            session.add(post)
            session.flush()
            
            # Publish to channel
            await AnnouncementHandler._publish_search_to_channel(post, context, bot)
            
            await reply_func(
                f"✅ Поисковое объявление #{unique_id} создано!\n\n"
                f"💰 К оплате: {Config.POST_PRICE} грн\n"
                f"⏰ Объявление будет активно {Config.POST_DURATION_HOURS} часов"
            )
    
    @staticmethod
    async def _publish_search_to_channel(post, context, bot):
        """Publish search post to channel"""
        game_text = ""
        if post.game_id:
            with db_manager.get_session() as session:
                game = session.query(Game).filter(Game.id == post.game_id).first()
                if game:
                    game_text = f"#{game.hashtag}"
        
        budget_text = ""
        if post.price:
            budget_text = f"💰 Бюджет: {post.price} грн"
        else:
            budget_text = "💬 Бюджет договорной"
        
        message_text = f"🔍 Ищу\n\n"
        message_text += f"📝 {post.description}\n\n"
        message_text += f"{budget_text}\n"
        if game_text:
            message_text += f"🎮 {game_text}\n"
        message_text += f"\n#{post.unique_id}"
        
        try:
            message = await bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=message_text,
                reply_markup=Keyboards.open_in_bot(post.unique_id)
            )
            
            # Update post with message ID
            with db_manager.get_session() as session:
                post = session.query(Post).filter(Post.id == post.id).first()
                post.channel_message_id = message.message_id
                
        except Exception as e:
            logger.error(f"Failed to publish search to channel: {e}")
    
    # Auction functionality
    @staticmethod
    async def _show_auction_info(query, context):
        """Show auction information"""
        auction_info = """
📣 Как работает аукцион:

1️⃣ Вы создаёте лот с минимальной ценой
2️⃣ Устанавливаете таймер (30 мин - 2 часа)
3️⃣ Участники делают ставки
4️⃣ Побеждает лучшая ставка
5️⃣ У вас есть возможность выбрать победителя

📸 Загрузите фото товара для аукциона:
        """
        
        await query.edit_message_text(auction_info)
        context.user_data['announcement_type'] = 'auction'
        context.user_data['photos'] = []
    
    @staticmethod
    async def handle_auction_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle auction photo upload"""
        return await AnnouncementHandler.handle_photo_upload(update, context)
    
    @staticmethod
    async def handle_auction_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle auction description"""
        context.user_data['description'] = update.message.text
        
        with db_manager.get_session() as session:
            games = session.query(Game).filter(Game.is_active == True).all()
            
            await update.message.reply_text(
                "🎮 Выберите игру:",
                reply_markup=Keyboards.games_pagination(games)
            )
        return AUCTION_GAME
    
    @staticmethod
    async def handle_auction_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle auction game selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "game_none":
            context.user_data['game_id'] = None
        elif query.data.startswith("game_"):
            game_id = int(query.data.split("_")[1])
            context.user_data['game_id'] = game_id
        elif query.data.startswith("games_page_"):
            page = int(query.data.split("_")[2])
            with db_manager.get_session() as session:
                games = session.query(Game).filter(Game.is_active == True).all()
                await query.edit_message_reply_markup(
                    reply_markup=Keyboards.games_pagination(games, page)
                )
            return AUCTION_GAME
        else:
            return AUCTION_GAME
        
        await query.edit_message_text(
            "💰 Введите минимальную цену для аукциона:"
        )
        return AUCTION_MIN_PRICE
    
    @staticmethod
    async def handle_auction_min_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle auction minimum price"""
        try:
            min_price = float(update.message.text)
            if min_price <= 0:
                raise ValueError("Price must be positive")
                
            context.user_data['min_price'] = min_price
            
            await update.message.reply_text(
                "⏰ Выберите длительность аукциона:",
                reply_markup=Keyboards.auction_timer()
            )
            return AUCTION_TIMER
            
        except ValueError:
            await update.message.reply_text(
                "❌ Пожалуйста, введите корректную цену:"
            )
            return AUCTION_MIN_PRICE
    
    @staticmethod
    async def handle_auction_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle auction timer selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("timer_"):
            timer_minutes = int(query.data.split("_")[1])
            context.user_data['auction_timer'] = timer_minutes
            
            await AnnouncementHandler._create_auction_post(query, context)
            return ConversationHandler.END
        
        return AUCTION_TIMER
    
    @staticmethod
    async def _create_auction_post(query, context):
        """Create auction post"""
        user_id = query.from_user.id
        
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            unique_id = AnnouncementHandler._generate_unique_id()
            
            auction_end_time = datetime.now() + timedelta(minutes=context.user_data['auction_timer'])
            
            post = Post(
                unique_id=unique_id,
                user_id=user.id,
                game_id=context.user_data.get('game_id'),
                post_type=PostType.AUCTION,
                title=context.user_data['description'][:100],
                description=context.user_data['description'],
                min_price=context.user_data['min_price'],
                auction_timer=context.user_data['auction_timer'],
                auction_end_time=auction_end_time,
                photos=json.dumps(context.user_data.get('photos', [])),
                expires_at=auction_end_time
            )
            
            session.add(post)
            session.flush()
            
            # Publish to channel
            await AnnouncementHandler._publish_auction_to_channel(query, post, context)
            
            timer_text = f"{context.user_data['auction_timer']} минут" if context.user_data['auction_timer'] < 60 else f"{context.user_data['auction_timer'] // 60} час(а)"
            
            await query.edit_message_text(
                f"🏆 Аукцион #{unique_id} создан!\n\n"
                f"💰 Минимальная цена: {context.user_data['min_price']} грн\n"
                f"⏰ Длительность: {timer_text}\n"
                f"🏁 Завершится: {auction_end_time.strftime('%d.%m %H:%M')}\n\n"
                "Аукцион опубликован в канале!"
            )
    
    @staticmethod
    async def _publish_auction_to_channel(query, post, context):
        """Publish auction to channel"""
        game_text = ""
        if post.game_id:
            with db_manager.get_session() as session:
                game = session.query(Game).filter(Game.id == post.game_id).first()
                if game:
                    game_text = f"#{game.hashtag}"
        
        timer_text = f"{post.auction_timer} минут" if post.auction_timer < 60 else f"{post.auction_timer // 60} час(а)"
        
        message_text = f"🏆 АУКЦИОН\n\n"
        message_text += f"📝 {post.description}\n\n"
        message_text += f"💰 Минимальная ставка: {post.min_price} грн\n"
        message_text += f"⏰ Длительность: {timer_text}\n"
        message_text += f"🏁 Завершится: {post.auction_end_time.strftime('%d.%m %H:%M')}\n"
        if game_text:
            message_text += f"🎮 {game_text}\n"
        message_text += f"\n#{post.unique_id}"
        
        photos = json.loads(post.photos) if post.photos else []
        
        try:
            if photos:
                message = await context.bot.send_photo(
                    chat_id=Config.CHANNEL_ID,
                    photo=photos[0],
                    caption=message_text,
                    reply_markup=Keyboards.open_in_bot(post.unique_id)
                )
            else:
                message = await context.bot.send_message(
                    chat_id=Config.CHANNEL_ID,
                    text=message_text,
                    reply_markup=Keyboards.open_in_bot(post.unique_id)
                )
            
            # Update post with message ID
            with db_manager.get_session() as session:
                post_update = session.query(Post).filter(Post.id == post.id).first()
                post_update.channel_message_id = message.message_id
                
        except Exception as e:
            logger.error(f"Failed to publish auction to channel: {e}")
    
    @staticmethod
    async def cancel_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel announcement creation"""
        await update.message.reply_text(
            "❌ Создание объявления отменено.",
            reply_markup=Keyboards.main_menu()
        )
        return ConversationHandler.END