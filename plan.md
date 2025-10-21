# Car Posting Web Scraper - Architecture & Class Structure

## Overview
A Python-based web scraper using Playwright to collect car posting data from various websites, with Discord integration for notifications and data sharing.

## Technology Stack
- **Python 3.9+**: Core programming language
- **Playwright**: Web automation and scraping
- **Discord.py**: Discord bot integration
- **SQLite/PostgreSQL**: Data storage
- **python-dotenv**: Environment variable management for secrets
- **Pydantic**: Data validation and models

## Architecture Overview

```
┌─────────────────┐
│  Main Process   │
│   (Scheduler)   │
└────────┬────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         │              │              │              │
         ▼              ▼              ▼              ▼
┌────────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ Scraper Module │ │ Database │ │ Discord  │ │ Config/Auth  │
│                │ │  Layer   │ │   Bot    │ │   Manager    │
└────────────────┘ └──────────┘ └──────────┘ └──────────────┘
```

## Project Structure

```
car_scraper/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configuration management
│   └── .env.example         # Example environment variables
├── models/
│   ├── __init__.py
│   ├── car_posting.py       # CarPosting data model
│   └── scraper_config.py    # Scraper configuration models
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py      # Abstract base scraper class
│   ├── autotrader_scraper.py
│   ├── craigslist_scraper.py
│   └── facebook_scraper.py
├── database/
│   ├── __init__.py
│   ├── db_manager.py        # Database operations
│   └── migrations/          # Database schema migrations
├── discord_bot/
│   ├── __init__.py
│   ├── bot.py              # Discord bot main class
│   ├── commands.py         # Bot commands
│   └── formatters.py       # Message formatters
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Logging configuration
│   └── validators.py       # Data validation utilities
├── tests/
│   ├── __init__.py
│   ├── test_scrapers.py
│   ├── test_database.py
│   └── test_discord_bot.py
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (git-ignored)
```

## Class Structures

### 1. Configuration Management

#### `config/settings.py`
```python
class Settings:
    """
    Central configuration management using environment variables.
    Handles secrets securely through .env file.
    """
    
    # Discord Configuration (Secret)
    DISCORD_BOT_TOKEN: str
    DISCORD_CHANNEL_ID: int
    
    # Database Configuration
    DATABASE_TYPE: str  # 'sqlite' or 'postgresql'
    DATABASE_URL: str
    
    # Scraper Configuration
    SCRAPER_INTERVAL_MINUTES: int
    MAX_CONCURRENT_SCRAPERS: int
    PLAYWRIGHT_HEADLESS: bool
    PLAYWRIGHT_TIMEOUT_MS: int
    
    # Notification Settings
    NOTIFY_ON_NEW_POSTING: bool
    NOTIFY_ON_PRICE_DROP: bool
    PRICE_DROP_THRESHOLD_PERCENT: float
    
    @classmethod
    def load_from_env():
        """Load configuration from .env file"""
        pass
    
    def validate(self):
        """Validate all configuration values"""
        pass
```

### 2. Data Models

#### `models/car_posting.py`
```python
class CarPosting:
    """
    Data model for a car posting/listing.
    Uses Pydantic for validation.
    """
    
    # Unique identifier
    id: str
    source_url: str
    source_platform: str  # 'autotrader', 'craigslist', etc.
    
    # Car details
    title: str
    make: str
    model: str
    year: int
    mileage: int
    price: float
    currency: str
    
    # Posting details
    description: str
    location: str
    seller_name: str
    seller_type: str  # 'dealer', 'private'
    
    # Images
    image_urls: List[str]
    thumbnail_url: str
    
    # Metadata
    posted_date: datetime
    last_updated: datetime
    first_scraped: datetime
    last_scraped: datetime
    
    # Additional features
    features: Dict[str, Any]
    condition: str  # 'new', 'used', 'certified'
    vin: Optional[str]
    
    def to_dict(self):
        """Convert to dictionary for storage"""
        pass
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        pass
    
    def to_discord_embed(self):
        """Convert to Discord embed format"""
        pass
```

#### `models/scraper_config.py`
```python
class ScraperConfig:
    """
    Configuration for individual scraper instances.
    """
    
    platform_name: str
    base_url: str
    search_url: str
    search_params: Dict[str, Any]
    
    # Selectors for scraping
    listing_selector: str
    title_selector: str
    price_selector: str
    mileage_selector: str
    # ... more selectors
    
    # Rate limiting
    delay_between_pages_sec: float
    max_pages: int
    
    # Filters
    min_price: Optional[float]
    max_price: Optional[float]
    min_year: Optional[int]
    max_year: Optional[int]
```

### 3. Web Scraping Layer

#### `scrapers/base_scraper.py`
```python
class BaseScraper(ABC):
    """
    Abstract base class for all web scrapers.
    Provides common functionality using Playwright.
    """
    
    def __init__(self, config: ScraperConfig, db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        self.browser = None
        self.page = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize_browser(self):
        """Initialize Playwright browser instance"""
        pass
    
    async def close_browser(self):
        """Clean up browser resources"""
        pass
    
    @abstractmethod
    async def scrape_listing_page(self, url: str) -> List[CarPosting]:
        """Scrape a single listing page - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def scrape_detail_page(self, url: str) -> CarPosting:
        """Scrape detailed information from a posting - must be implemented"""
        pass
    
    async def run_scraper(self) -> List[CarPosting]:
        """
        Main scraping workflow:
        1. Initialize browser
        2. Navigate to search page
        3. Scrape listings
        4. Scrape details for new/updated listings
        5. Store in database
        6. Close browser
        """
        pass
    
    async def handle_pagination(self):
        """Navigate through paginated results"""
        pass
    
    async def extract_text(self, selector: str) -> str:
        """Helper to extract text from element"""
        pass
    
    async def extract_number(self, selector: str) -> float:
        """Helper to extract and parse numeric values"""
        pass
    
    async def take_screenshot(self, filename: str):
        """Take screenshot for debugging"""
        pass
    
    def is_duplicate(self, posting: CarPosting) -> bool:
        """Check if posting already exists in database"""
        pass
    
    def has_price_changed(self, posting: CarPosting) -> Tuple[bool, float]:
        """Check if price has changed for existing posting"""
        pass
```

#### `scrapers/autotrader_scraper.py`
```python
class AutoTraderScraper(BaseScraper):
    """
    Concrete implementation for AutoTrader website.
    """
    
    async def scrape_listing_page(self, url: str) -> List[CarPosting]:
        """AutoTrader-specific listing page scraping"""
        pass
    
    async def scrape_detail_page(self, url: str) -> CarPosting:
        """AutoTrader-specific detail page scraping"""
        pass
    
    def _parse_autotrader_price(self, price_text: str) -> float:
        """Parse AutoTrader price format"""
        pass
```

#### `scrapers/craigslist_scraper.py`
```python
class CraigslistScraper(BaseScraper):
    """
    Concrete implementation for Craigslist.
    """
    
    async def scrape_listing_page(self, url: str) -> List[CarPosting]:
        """Craigslist-specific listing page scraping"""
        pass
    
    async def scrape_detail_page(self, url: str) -> CarPosting:
        """Craigslist-specific detail page scraping"""
        pass
```

### 4. Database Layer

#### `database/db_manager.py`
```python
class DatabaseManager:
    """
    Handles all database operations for car postings.
    Supports SQLite for development and PostgreSQL for production.
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def connect(self):
        """Establish database connection"""
        pass
    
    def disconnect(self):
        """Close database connection"""
        pass
    
    def create_tables(self):
        """Create necessary database tables"""
        pass
    
    def save_posting(self, posting: CarPosting) -> bool:
        """
        Save or update a car posting.
        Returns True if new posting, False if updated.
        """
        pass
    
    def get_posting_by_id(self, posting_id: str) -> Optional[CarPosting]:
        """Retrieve a posting by ID"""
        pass
    
    def get_postings_by_filters(self, filters: Dict) -> List[CarPosting]:
        """Query postings with filters"""
        pass
    
    def get_recent_postings(self, limit: int = 10) -> List[CarPosting]:
        """Get most recent postings"""
        pass
    
    def get_price_history(self, posting_id: str) -> List[Dict]:
        """Get price change history for a posting"""
        pass
    
    def mark_as_sold(self, posting_id: str):
        """Mark posting as no longer available"""
        pass
    
    def cleanup_old_postings(self, days: int = 30):
        """Remove old sold/expired postings"""
        pass
```

### 5. Discord Integration

#### `discord_bot/bot.py`
```python
class CarScraperBot:
    """
    Discord bot for receiving notifications and interacting with scraped data.
    Bot token is loaded from environment variables for security.
    """
    
    def __init__(self, token: str, db_manager: DatabaseManager):
        self.token = token  # Loaded from .env, never hardcoded
        self.bot = discord.Client(intents=discord.Intents.default())
        self.db_manager = db_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Register event handlers"""
        pass
    
    async def start_bot(self):
        """Start the Discord bot"""
        pass
    
    async def stop_bot(self):
        """Gracefully stop the bot"""
        pass
    
    async def send_new_posting_notification(
        self, 
        channel_id: int, 
        posting: CarPosting
    ):
        """Send notification for new car posting"""
        pass
    
    async def send_price_drop_notification(
        self, 
        channel_id: int, 
        posting: CarPosting,
        old_price: float,
        new_price: float
    ):
        """Send notification when price drops"""
        pass
    
    async def send_daily_summary(self, channel_id: int):
        """Send daily summary of new postings"""
        pass
```

#### `discord_bot/commands.py`
```python
class BotCommands:
    """
    Discord bot command handlers.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def cmd_search(self, ctx, **kwargs):
        """
        Search for cars with filters.
        Usage: !search make:Honda model:Civic max_price:15000
        """
        pass
    
    async def cmd_recent(self, ctx, limit: int = 10):
        """
        Show recent postings.
        Usage: !recent 20
        """
        pass
    
    async def cmd_watch(self, ctx, posting_id: str):
        """
        Watch a specific posting for price changes.
        Usage: !watch ABC123
        """
        pass
    
    async def cmd_stats(self, ctx):
        """
        Show scraper statistics.
        Usage: !stats
        """
        pass
```

#### `discord_bot/formatters.py`
```python
class MessageFormatter:
    """
    Formats data into Discord-friendly messages and embeds.
    """
    
    @staticmethod
    def create_posting_embed(posting: CarPosting) -> discord.Embed:
        """
        Create rich embed for car posting with:
        - Title, price, mileage
        - Thumbnail image
        - Key features
        - Link to original posting
        """
        pass
    
    @staticmethod
    def create_price_drop_embed(
        posting: CarPosting,
        old_price: float,
        new_price: float
    ) -> discord.Embed:
        """Create embed highlighting price reduction"""
        pass
    
    @staticmethod
    def format_search_results(postings: List[CarPosting]) -> str:
        """Format multiple postings into readable message"""
        pass
```

### 6. Main Application

#### `main.py`
```python
class CarScraperApplication:
    """
    Main application coordinating all components.
    """
    
    def __init__(self):
        self.settings = Settings.load_from_env()
        self.db_manager = DatabaseManager(self.settings.DATABASE_URL)
        self.discord_bot = CarScraperBot(
            self.settings.DISCORD_BOT_TOKEN,
            self.db_manager
        )
        self.scrapers: List[BaseScraper] = []
        self.scheduler = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def initialize(self):
        """
        Initialize all components:
        1. Load configuration
        2. Connect to database
        3. Initialize scrapers
        4. Start Discord bot
        """
        pass
    
    def register_scraper(self, scraper: BaseScraper):
        """Register a scraper instance"""
        pass
    
    async def run_all_scrapers(self):
        """Run all registered scrapers concurrently"""
        pass
    
    async def process_new_postings(self, postings: List[CarPosting]):
        """
        Process newly scraped postings:
        1. Check for duplicates
        2. Check for price changes
        3. Save to database
        4. Send Discord notifications
        """
        pass
    
    def start_scheduler(self):
        """Start scheduled scraping tasks"""
        pass
    
    def run(self):
        """Main application entry point"""
        pass
    
    def shutdown(self):
        """Graceful shutdown of all components"""
        pass


def main():
    """Application entry point"""
    app = CarScraperApplication()
    try:
        app.initialize()
        app.run()
    except KeyboardInterrupt:
        app.logger.info("Shutting down...")
        app.shutdown()
    except Exception as e:
        app.logger.error(f"Fatal error: {e}")
        app.shutdown()
        raise


if __name__ == "__main__":
    main()
```

## Security & Secrets Management

### Environment Variables (.env)
```
# Discord Configuration - KEEP SECRET
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=1234567890

# Database Configuration
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///car_scraper.db

# Scraper Settings
SCRAPER_INTERVAL_MINUTES=60
MAX_CONCURRENT_SCRAPERS=3
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT_MS=30000

# Notification Settings
NOTIFY_ON_NEW_POSTING=true
NOTIFY_ON_PRICE_DROP=true
PRICE_DROP_THRESHOLD_PERCENT=5.0
```

### Security Best Practices
1. **Never commit .env file**: Add to .gitignore
2. **Use environment variables**: Load secrets using python-dotenv
3. **Provide .env.example**: Template without actual secrets
4. **Validate secrets on startup**: Ensure all required secrets are present
5. **Use HTTPS**: All external API calls should use secure connections
6. **Rate limiting**: Respect website rate limits to avoid bans
7. **User agent rotation**: Use realistic user agents
8. **Error handling**: Don't expose sensitive data in logs

## Data Flow

1. **Scheduled Scraping**:
   - Scheduler triggers scraper at configured interval
   - Scraper initializes Playwright browser
   - Navigates to car listing websites
   - Extracts car posting data
   - Validates and structures data

2. **Data Processing**:
   - Check for duplicate postings in database
   - Detect price changes for existing postings
   - Save new/updated postings to database
   - Track price history

3. **Discord Notifications**:
   - New posting: Send embed with car details
   - Price drop: Send alert with old/new prices
   - Daily summary: Aggregate report of activity

4. **User Interaction**:
   - Discord commands to search/filter postings
   - Watch specific postings for changes
   - View statistics and trends

## Dependencies (requirements.txt)

```
# Web Scraping
playwright==1.40.0
beautifulsoup4==4.12.2
lxml==4.9.3

# Discord Integration
discord.py==2.3.2

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9  # For PostgreSQL

# Data Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Configuration
python-dotenv==1.0.0

# Utilities
python-dateutil==2.8.2
aiohttp==3.9.1
asyncio==3.4.3

# Logging
loguru==0.7.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-playwright==0.4.3
pytest-mock==3.12.0

# Development
black==23.11.0
flake8==6.1.0
mypy==1.7.1
```

## Testing Strategy

1. **Unit Tests**:
   - Test individual scraper methods
   - Test data model validation
   - Test database operations
   - Test Discord message formatting

2. **Integration Tests**:
   - Test complete scraping workflow
   - Test database persistence
   - Test Discord notification delivery

3. **Mock Data**:
   - Use recorded HTTP responses for scraper tests
   - Mock Playwright browser for faster tests
   - Mock Discord API calls

## Deployment Considerations

1. **Development**: Run locally with SQLite
2. **Production**: 
   - Use PostgreSQL for better concurrency
   - Deploy as Docker container
   - Use process manager (systemd/supervisor)
   - Set up monitoring and alerting
3. **Scaling**:
   - Run multiple scraper instances
   - Use message queue for notifications
   - Implement caching layer

## Future Enhancements

1. Machine learning for price prediction
2. Multi-language support
3. Web dashboard for visualization
4. Email notifications
5. Mobile app integration
6. Advanced filtering and saved searches
7. Price trend analysis and charts
8. Integration with more car listing platforms
