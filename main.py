#!/usr/bin/env python3
"""
Gaming Marketplace Telegram Bot
===============================

A comprehensive Telegram bot for a gaming marketplace with escrow services.
Features:
- Post management (sell/buy/search/auction)
- Secure escrow system with 7-stage verification
- Anti-scam protection
- Admin panel with statistics
- User profiles and ratings
"""

import logging
import asyncio
from datetime import datetime
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)

from config import Config
from database.database import db_manager
from handlers.main_menu import MainMenuHandler
from handlers.announcements import AnnouncementHandler, (
    TYPE_SELECTION, PHOTOS_UPLOAD, DESCRIPTION_INPUT, PRICE_INPUT,
    GAME_SELECTION, PIN_OFFER, SEARCH_WHAT, SEARCH_GAME, SEARCH_BUDGET,
    AUCTION_PHOTOS, AUCTION_DESC, AUCTION_GAME, AUCTION_MIN_PRICE, AUCTION_TIMER
)
from handlers.chat_system import ChatSystemHandler
from handlers.escrow_system import EscrowHandler, (
    PRICE_CONFIRMATION, COMMISSION_SELECTION, PAYMENT_DETAILS,
    PAYMENT_PROCESSING, VERIFICATION_VIDEO, TRANSACTION_PROGRESS, RATING_REVIEW
)
from handlers.admin_panel import AdminPanelHandler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GamingMarketplaceBot:
    """Main bot class"""
    
    def __init__(self):
        self.application = None
        
    async def initialize(self):
        """Initialize the bot"""
        logger.info("Initializing Gaming Marketplace Bot...")
        
        # Create tables
        db_manager.create_tables()
        
        # Initialize application
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Add handlers
        self._add_handlers()
        
        logger.info("Bot initialized successfully!")
    
    def _add_handlers(self):
        """Add all bot handlers"""
        
        # Announcement conversation handler
        announcement_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(
                AnnouncementHandler.start_announcement,
                pattern=r'^(announce_create|announce_search|announce_auction)$'
            )],
            states={
                TYPE_SELECTION: [CallbackQueryHandler(
                    AnnouncementHandler.handle_type_selection,
                    pattern=r'^(type_sell|type_buy)$'
                )],
                PHOTOS_UPLOAD: [
                    MessageHandler(filters.PHOTO, AnnouncementHandler.handle_photo_upload),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, AnnouncementHandler.handle_photo_upload)
                ],
                DESCRIPTION_INPUT: [MessageHandler(
                    filters.TEXT & ~filters.COMMAND, AnnouncementHandler.handle_description
                )],
                PRICE_INPUT: [
                    CallbackQueryHandler(AnnouncementHandler.handle_price_selection),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, AnnouncementHandler.handle_price_input)
                ],
                GAME_SELECTION: [CallbackQueryHandler(AnnouncementHandler.handle_game_selection)],
                PIN_OFFER: [CallbackQueryHandler(AnnouncementHandler.handle_pin_offer)],
                
                # Search states
                SEARCH_WHAT: [MessageHandler(
                    filters.TEXT & ~filters.COMMAND, AnnouncementHandler.handle_search_what
                )],
                SEARCH_GAME: [CallbackQueryHandler(AnnouncementHandler.handle_search_game)],
                SEARCH_BUDGET: [
                    CallbackQueryHandler(AnnouncementHandler.handle_search_budget),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, AnnouncementHandler.handle_search_budget_input)
                ],
                
                # Auction states
                AUCTION_PHOTOS: [
                    MessageHandler(filters.PHOTO, AnnouncementHandler.handle_auction_photos),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, AnnouncementHandler.handle_auction_photos)
                ],
                AUCTION_DESC: [MessageHandler(
                    filters.TEXT & ~filters.COMMAND, AnnouncementHandler.handle_auction_description
                )],
                AUCTION_GAME: [CallbackQueryHandler(AnnouncementHandler.handle_auction_game)],
                AUCTION_MIN_PRICE: [MessageHandler(
                    filters.TEXT & ~filters.COMMAND, AnnouncementHandler.handle_auction_min_price
                )],
                AUCTION_TIMER: [CallbackQueryHandler(AnnouncementHandler.handle_auction_timer)]
            },
            fallbacks=[CommandHandler('cancel', AnnouncementHandler.cancel_announcement)]
        )
        
        # Escrow conversation handler
        escrow_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(
                EscrowHandler.initiate_transaction,
                pattern=r'^start_transaction_\d+$'
            )],
            states={
                PRICE_CONFIRMATION: [
                    CallbackQueryHandler(EscrowHandler.handle_price_confirmation),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, EscrowHandler.handle_price_confirmation)
                ],
                COMMISSION_SELECTION: [CallbackQueryHandler(EscrowHandler.handle_commission_selection)],
                PAYMENT_DETAILS: [
                    CallbackQueryHandler(EscrowHandler.handle_payment_method_selection),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, EscrowHandler.handle_payment_details_input)
                ],
                PAYMENT_PROCESSING: [CallbackQueryHandler(EscrowHandler.handle_payment_details_confirmation)],
                VERIFICATION_VIDEO: [MessageHandler(filters.VIDEO_NOTE, EscrowHandler.handle_verification_video)],
                RATING_REVIEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, EscrowHandler.handle_review_input)]
            },
            fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)]
        )
        
        # Basic command handlers
        self.application.add_handler(CommandHandler('start', MainMenuHandler.start_command))
        self.application.add_handler(CommandHandler('admin', AdminPanelHandler.admin_command))
        self.application.add_handler(CommandHandler('stats', AdminPanelHandler.admin_stats))
        self.application.add_handler(CommandHandler('users', AdminPanelHandler.admin_users_command))
        self.application.add_handler(CommandHandler('broadcast', AdminPanelHandler.admin_broadcast))
        self.application.add_handler(CommandHandler('transactions', AdminPanelHandler.admin_transactions))
        self.application.add_handler(CommandHandler('settings', AdminPanelHandler.admin_settings))
        
        # Conversation handlers
        self.application.add_handler(announcement_conv)
        self.application.add_handler(escrow_conv)
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(
            ChatSystemHandler.handle_contact_seller,
            pattern=r'^contact_\d+$'
        ))
        self.application.add_handler(CallbackQueryHandler(
            ChatSystemHandler.handle_start_transaction,
            pattern=r'^start_transaction_\d+$'
        ))
        self.application.add_handler(CallbackQueryHandler(
            ChatSystemHandler.handle_close_chat,
            pattern=r'^close_chat_\d+$'
        ))
        self.application.add_handler(CallbackQueryHandler(
            EscrowHandler.handle_transaction_completion,
            pattern=r'^(confirm_transaction_|cancel_transaction_|help_transaction_)\d+$'
        ))
        self.application.add_handler(CallbackQueryHandler(
            EscrowHandler.handle_verification_approval,
            pattern=r'^(admin_confirm_|admin_reject_|admin_extend_)\d+$'
        ))
        self.application.add_handler(CallbackQueryHandler(
            EscrowHandler.handle_rating_selection,
            pattern=r'^rating_\d+$'
        ))
        self.application.add_handler(CallbackQueryHandler(
            AdminPanelHandler.handle_admin_user_action,
            pattern=r'^admin_(ban_|unban_|suspicious_|balance_|stats_)\d+$'
        ))
        
        # Message handlers
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, MainMenuHandler.handle_main_menu
        ))
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, ChatSystemHandler.handle_chat_message
        ))
        self.application.add_handler(MessageHandler(
            filters.PHOTO, ChatSystemHandler.handle_photo_message
        ))
        
        # Error handler
        self.application.add_error_handler(self._error_handler)
        
        logger.info("All handlers added successfully!")
    
    async def _error_handler(self, update, context):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        # Try to notify user about the error
        if update and update.effective_user:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text="❌ Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")
    
    async def run(self):
        """Run the bot"""
        logger.info("Starting Gaming Marketplace Bot...")
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        
        # Start polling
        await self.application.updater.start_polling()
        
        logger.info("Bot is running! Press Ctrl+C to stop.")
        
        try:
            # Keep the bot running
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Received stop signal...")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping bot...")
        
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        
        # Close database connections
        db_manager.close_connections()
        
        logger.info("Bot stopped successfully!")

async def setup_initial_data():
    """Set up initial data for the bot"""
    logger.info("Setting up initial data...")
    
    with db_manager.get_session() as session:
        from database.models import Game
        
        # Check if games already exist
        existing_games = session.query(Game).count()
        if existing_games > 0:
            logger.info("Games already exist, skipping initial setup")
            return
        
        # Add popular games
        initial_games = [
            ("Minecraft", "minecraft"),
            ("Fortnite", "fortnite"),
            ("CS:GO", "csgo"),
            ("PUBG", "pubg"),
            ("Dota 2", "dota2"),
            ("League of Legends", "lol"),
            ("World of Warcraft", "wow"),
            ("GTA V", "gtav"),
            ("Rocket League", "rocketleague"),
            ("Valorant", "valorant"),
            ("Apex Legends", "apex"),
            ("Call of Duty", "cod"),
            ("Overwatch", "overwatch"),
            ("FIFA", "fifa"),
            ("Genshin Impact", "genshin"),
            ("Among Us", "amongus"),
            ("Fall Guys", "fallguys"),
            ("Roblox", "roblox"),
            ("Mobile Legends", "mobilelegends"),
            ("MLBB", "mlbb")
        ]
        
        for name, hashtag in initial_games:
            game = Game(name=name, hashtag=hashtag)
            session.add(game)
        
        logger.info(f"Added {len(initial_games)} initial games")

async def setup_scheduler():
    """Set up scheduled tasks"""
    logger.info("Setting up scheduler...")
    
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    
    scheduler = AsyncIOScheduler()
    
    # Daily statistics update at midnight
    scheduler.add_job(
        AdminPanelHandler.update_daily_statistics,
        CronTrigger(hour=0, minute=0),
        id='daily_stats'
    )
    
    # Daily report at 9 AM
    scheduler.add_job(
        AdminPanelHandler.generate_daily_report,
        CronTrigger(hour=9, minute=0),
        id='daily_report'
    )
    
    # Post expiry check every hour
    async def check_expired_posts():
        with db_manager.get_session() as session:
            from database.models import Post
            
            expired_posts = session.query(Post).filter(
                Post.is_active == True,
                Post.expires_at <= datetime.now()
            ).all()
            
            for post in expired_posts:
                post.is_active = False
                logger.info(f"Post {post.unique_id} expired")
    
    scheduler.add_job(
        check_expired_posts,
        CronTrigger(minute=0),  # Every hour
        id='check_expired_posts'
    )
    
    # Post expiry warning 2 hours before expiry
    async def send_expiry_warnings():
        with db_manager.get_session() as session:
            from database.models import Post, User
            from datetime import timedelta
            
            warning_time = datetime.now() + timedelta(hours=Config.WARNING_HOURS)
            
            posts_to_warn = session.query(Post).filter(
                Post.is_active == True,
                Post.expires_at <= warning_time,
                Post.expires_at > datetime.now()
            ).all()
            
            for post in posts_to_warn:
                user = session.query(User).filter(User.id == post.user_id).first()
                if user:
                    try:
                        # This would need the bot instance to send messages
                        logger.info(f"Should warn user {user.telegram_id} about post {post.unique_id} expiry")
                    except Exception as e:
                        logger.error(f"Failed to send expiry warning: {e}")
    
    scheduler.add_job(
        send_expiry_warnings,
        CronTrigger(minute=30),  # Every hour at 30 minutes
        id='expiry_warnings'
    )
    
    scheduler.start()
    logger.info("Scheduler started successfully!")
    
    return scheduler

async def main():
    """Main function"""
    print("""
    🎮 Gaming Marketplace Bot
    ========================
    
    Features:
    ✅ Announcement system (Sell/Buy/Search/Auction)
    ✅ 7-stage escrow system with verification
    ✅ Anti-scam protection
    ✅ Admin panel with statistics
    ✅ User profiles and ratings
    ✅ Chat system with message forwarding
    
    Starting bot...
    """)
    
    try:
        # Validate configuration
        if not Config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN not set in environment variables")
        
        # Set up initial data
        await setup_initial_data()
        
        # Set up scheduler
        scheduler = await setup_scheduler()
        
        # Create and run bot
        bot = GamingMarketplaceBot()
        await bot.initialize()
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise
    finally:
        logger.info("Cleanup completed")

if __name__ == '__main__':
    asyncio.run(main())