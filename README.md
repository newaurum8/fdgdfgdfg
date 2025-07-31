# 🎮 Gaming Marketplace Telegram Bot

A comprehensive Telegram bot for a gaming marketplace with secure escrow services, designed specifically for the Ukrainian gaming community.

## 🌟 Features

### 📢 Announcement System
- **Sell/Buy Posts**: Create listings with photos, descriptions, and pricing
- **Search Requests**: Post what you're looking for with budget information
- **Auction System**: Time-limited auctions with bidding functionality
- **Game Categorization**: Hashtag-based game filtering
- **Post Management**: Pin, extend, and delete functionality

### 🤝 7-Stage Escrow System
1. **Initiation**: Price negotiation and agreement
2. **Commission**: Payment responsibility selection
3. **Payment Details**: Seller payment method setup
4. **Payment Processing**: Secure payment collection
5. **Seller Verification**: Video verification with phrase confirmation
6. **Transaction Progress**: 3-hour completion window
7. **Rating & Review**: Mutual feedback system

### 💬 Chat System
- **Message Forwarding**: Secure communication through bot
- **Unique Chat IDs**: Each conversation has a unique identifier
- **Anti-Spam Protection**: Automatic detection of scam attempts
- **Status Tracking**: Real-time chat and transaction status

### 🛡️ Anti-Scam Protection
- **Keyword Detection**: Monitors for bypass attempts
- **Automatic Warnings**: Progressive warning system
- **Temporary Bans**: Protection against repeat offenders
- **Moderator Alerts**: Real-time notifications to admin team

### 👤 User Profiles
- **Rating System**: 5-star rating with transaction history
- **Verified Seller Status**: Special badge for trusted sellers
- **Transaction Statistics**: Complete activity overview
- **Review Management**: Public feedback system

### 🔧 Admin Panel
- **User Management**: Ban, unban, and status modification
- **Transaction Oversight**: Monitor and manage all transactions
- **Statistics Dashboard**: Comprehensive analytics
- **Broadcast System**: Mass messaging capabilities
- **Daily Reports**: Automated performance summaries

## 🚀 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL database
- Redis server
- Telegram Bot Token

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/gaming-marketplace-bot.git
cd gaming-marketplace-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up the database**
```bash
# Create PostgreSQL database
createdb gaming_bot

# The bot will automatically create tables on first run
```

5. **Run the bot**
```bash
python main.py
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot Token from @BotFather | ✅ |
| `CHANNEL_ID` | Channel where posts are published | ✅ |
| `MODERATOR_GROUP_ID` | Admin group for notifications | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `ADMIN_IDS` | Comma-separated admin user IDs | ✅ |
| `ESCROW_COMMISSION` | Commission rate (0.05 = 5%) | ❌ |
| `MIN_TRANSACTION_AMOUNT` | Minimum transaction amount | ❌ |
| `POST_PRICE` | Cost to create a post (UAH) | ❌ |
| `PIN_PRICE` | Cost to pin a post (UAH) | ❌ |
| `EXTEND_PRICE` | Cost to extend a post (UAH) | ❌ |

### Default Pricing (UAH)
- Post creation: 30₴
- Post pinning: 99₴
- Post extension: 25₴
- Escrow commission: 5%

## 🗂️ Project Structure

```
gaming-marketplace-bot/
├── main.py                 # Main bot entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── .env.example          # Environment template
│
├── database/
│   ├── __init__.py
│   ├── models.py         # SQLAlchemy models
│   └── database.py       # Database connection
│
├── handlers/
│   ├── __init__.py
│   ├── main_menu.py      # Main menu handlers
│   ├── announcements.py  # Post creation system
│   ├── chat_system.py    # Chat management
│   ├── escrow_system.py  # Transaction processing
│   └── admin_panel.py    # Admin functionality
│
└── utils/
    ├── __init__.py
    └── keyboards.py       # Telegram keyboards
```

## 📱 User Guide

### Creating a Post

1. Start with `/start` command
2. Press "📢 Сделать объявление"
3. Choose post type:
   - **▶️ Сделать объявление**: Regular sell/buy post
   - **🔍 Найти**: Search request
   - **📣 Аукцион**: Auction listing

4. Follow the step-by-step form:
   - Upload photos (up to 10)
   - Add description
   - Set price or select "negotiable"
   - Choose game category
   - Decide on pinning (optional)

### Starting a Transaction

1. Find a post in the channel
2. Click "📩 Открыть в боте"
3. Press "💬 Связаться с продавцом"
4. Negotiate in chat
5. Click "🤝 Начать сделку"
6. Follow the 7-stage escrow process

### Using the Auction System

1. Create auction with minimum price and timer
2. Users make bids through the bot
3. Seller can accept/reject individual bids
4. Automatic winner selection at timer end
5. Losing bidders get second chances if winner declines

## 🔧 Admin Commands

- `/admin` - Main admin panel
- `/stats` - Detailed statistics
- `/users [ID/@username]` - User management
- `/transactions [pending]` - Transaction oversight
- `/broadcast [message]` - Send message to all users
- `/settings` - View bot configuration

### User Management Filters
- `/users banned` - Show banned users
- `/users suspicious` - Show flagged users
- `/users active` - Show recently active users
- `/users top` - Show top sellers

## 🛡️ Security Features

### Anti-Scam Protection
- Monitors messages for bypass attempts
- Detects contact information sharing
- Progressive warning system (3 strikes)
- Automatic temporary bans
- Moderator notifications

### Transaction Security
- Funds held in escrow until completion
- Video verification of sellers
- 3-hour transaction completion window
- Admin oversight for disputes
- Automatic refund system

## 📊 Statistics & Analytics

### Daily Metrics
- New user registrations
- Active users
- Posts created
- Transactions completed/cancelled
- Revenue generated

### Performance Tracking
- Transaction success rates
- User engagement metrics
- Top sellers identification
- Fraud detection statistics

## 🎯 Roadmap

### Planned Features
- [ ] Mobile app integration
- [ ] Multi-language support
- [ ] Enhanced payment methods
- [ ] Advanced search filters
- [ ] Seller verification badges
- [ ] Dispute resolution system
- [ ] Automatic translation

### Technical Improvements
- [ ] Webhook support
- [ ] Database optimization
- [ ] Caching improvements
- [ ] Load balancing
- [ ] Monitoring dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to functions
- Keep functions small and focused

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Join our Telegram support group

## 🙏 Acknowledgments

- Thanks to the python-telegram-bot library developers
- Ukrainian gaming community for feedback and testing
- All contributors and supporters

---

**⚠️ Important Notice**: This bot handles financial transactions. Always ensure proper security measures and comply with local regulations when deploying in production.

Made with ❤️ for the Ukrainian gaming community 🇺🇦