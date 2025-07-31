from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

class UserStatus(enum.Enum):
    ACTIVE = "active"
    SUSPICIOUS = "suspicious"
    BANNED = "banned"

class PostType(enum.Enum):
    SELL = "sell"
    BUY = "buy"
    SEARCH = "search"
    AUCTION = "auction"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    PAYMENT_PENDING = "payment_pending"
    VERIFICATION_PENDING = "verification_pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class PriceType(enum.Enum):
    FIXED = "fixed"
    NEGOTIABLE = "negotiable"
    NO_PRICE = "no_price"

class ChatStatus(enum.Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    TRANSACTION = "transaction"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    nickname = Column(String(255))
    phone = Column(String(20))
    
    # Status and ratings
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    total_transactions = Column(Integer, default=0)
    total_amount = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)
    is_verified_seller = Column(Boolean, default=False)
    
    # Counters for anti-scam
    daily_cancellations = Column(Integer, default=0)
    last_cancellation_date = Column(DateTime)
    warnings_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime, default=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="user")
    chats_as_user1 = relationship("Chat", foreign_keys="[Chat.user1_id]", back_populates="user1")
    chats_as_user2 = relationship("Chat", foreign_keys="[Chat.user2_id]", back_populates="user2")
    transactions_as_buyer = relationship("Transaction", foreign_keys="[Transaction.buyer_id]", back_populates="buyer")
    transactions_as_seller = relationship("Transaction", foreign_keys="[Transaction.seller_id]", back_populates="seller")
    reviews_given = relationship("Review", foreign_keys="[Review.reviewer_id]", back_populates="reviewer")
    reviews_received = relationship("Review", foreign_keys="[Review.reviewee_id]", back_populates="reviewee")

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    hashtag = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="game")

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    unique_id = Column(String(10), unique=True, nullable=False)  # #10484079
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'))
    
    # Post content
    post_type = Column(Enum(PostType), nullable=False)
    title = Column(String(500))
    description = Column(Text)
    price = Column(Float)
    price_type = Column(Enum(PriceType), default=PriceType.FIXED)
    photos = Column(Text)  # JSON array of photo file_ids
    
    # Auction specific
    min_price = Column(Float)
    auction_timer = Column(Integer)  # minutes
    auction_end_time = Column(DateTime)
    
    # Post status
    is_active = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    channel_message_id = Column(Integer)
    views_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    game = relationship("Game", back_populates="posts")
    chats = relationship("Chat", back_populates="post")
    auction_bids = relationship("AuctionBid", back_populates="post")

class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user1_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Post author
    user2_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Interested user
    
    status = Column(Enum(ChatStatus), default=ChatStatus.WAITING)
    last_message_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="chats")
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="chats_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="chats_as_user2")
    messages = relationship("Message", back_populates="chat")
    transactions = relationship("Transaction", back_populates="chat")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    message_text = Column(Text)
    message_type = Column(String(50), default='text')  # text, photo, video, etc.
    file_id = Column(String(255))
    
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(255))
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    seller_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    buyer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    commission_payer = Column(String(20))  # 'seller', 'buyer', 'split'
    
    # Payment details
    payment_method = Column(String(50))  # 'ua_card', 'crypto_ton', 'crypto_usdt'
    seller_payment_info = Column(Text)  # JSON with payment details
    
    # Status and verification
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    verification_phrase = Column(String(255))
    verification_video_file_id = Column(String(255))
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    payment_deadline = Column(DateTime)
    completion_deadline = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    chat = relationship("Chat", back_populates="transactions")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="transactions_as_seller")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="transactions_as_buyer")

class AuctionBid(Base):
    __tablename__ = 'auction_bids'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    amount = Column(Float, nullable=False)
    is_accepted = Column(Boolean, default=False)
    is_winner = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="auction_bids")
    user = relationship("User")

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reviewee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    transaction = relationship("Transaction")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="reviews_received")

class AntiSpamLog(Base):
    __tablename__ = 'antispam_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message_text = Column(Text)
    triggered_keywords = Column(String(500))
    action_taken = Column(String(100))
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User")

class AdminAction(Base):
    __tablename__ = 'admin_actions'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, nullable=False)
    target_user_id = Column(Integer, ForeignKey('users.id'))
    action_type = Column(String(100), nullable=False)
    reason = Column(Text)
    details = Column(Text)  # JSON
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    target_user = relationship("User")

class BotStatistics(Base):
    __tablename__ = 'bot_statistics'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    
    # Daily stats
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_posts = Column(Integer, default=0)
    completed_transactions = Column(Integer, default=0)
    cancelled_transactions = Column(Integer, default=0)
    total_transaction_volume = Column(Float, default=0.0)
    commission_earned = Column(Float, default=0.0)
    post_revenue = Column(Float, default=0.0)
    
    # Referral stats
    referral_users = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())

class SystemSettings(Base):
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(String(500))
    
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())