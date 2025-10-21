# Car Posting Data Gatherer - Architecture & Class Structure

## Overview
A Python-based web gatherer using Playwright to collect car posting data from various websites, with Discord integration for notifications and data sharing.

## Technology Stack
- **Python 3.12+**: Core programming language
- **Playwright**: Web automation and gathering
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
│ Gatherer Module │ │ Database │ │ Discord  │ │ Config/Auth  │
│                │ │  Layer   │ │   Bot    │ │   Manager    │
└────────────────┘ └──────────┘ └──────────┘ └──────────────┘
```

## Project Structure

```
inventory_gatherer/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configuration management
│   └── .env.example         # Example environment variables
├── models/
│   ├── __init__.py
│   ├── car_posting.py       # CarPosting data model
│   └── gatherer_config.py    # Gatherer configuration models
├── gatherers/
│   ├── __init__.py
│   ├── base_gatherer.py      # Abstract base gatherer class
│   ├── autotrader_gatherer.py
│   ├── craigslist_gatherer.py
│   └── facebook_gatherer.py
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
│   ├── test_gatherers.py
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
    
    # Gatherer Configuration
    GATHERER_INTERVAL_MINUTES: int
    MAX_CONCURRENT_GATHERERS: int
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
    first_gathered: datetime
    last_gathered: datetime
    
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

#### `models/gatherer_config.py`
```python
class GathererConfig:
    """
    Configuration for individual gatherer instances.
    """
    
    platform_name: str
    base_url: str
    search_url: str
    search_params: Dict[str, Any]
    
    # Selectors for gathering
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

### 3. Web Gathering Layer

#### `gatherers/base_gatherer.py`
```python
class BaseGatherer(ABC):
    """
    Abstract base class for all web gatherers.
    Provides common functionality using Playwright.
    """
    
    def __init__(self, config: GathererConfig, db_manager: DatabaseManager):
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
    async def gather_listing_page(self, url: str) -> List[CarPosting]:
        """Gather a single listing page - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def gather_detail_page(self, url: str) -> CarPosting:
        """Gather detailed information from a posting - must be implemented"""
        pass
    
    async def run_gatherer(self) -> List[CarPosting]:
        """
        Main gathering workflow:
        1. Initialize browser
        2. Navigate to search page
        3. Gather listings
        4. Gather details for new/updated listings
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

#### `gatherers/autotrader_gatherer.py`
```python
class AutoTraderGatherer(BaseGatherer):
    """
    Concrete implementation for AutoTrader website.
    """
    
    async def gather_listing_page(self, url: str) -> List[CarPosting]:
        """AutoTrader-specific listing page gathering"""
        pass
    
    async def gather_detail_page(self, url: str) -> CarPosting:
        """AutoTrader-specific detail page gathering"""
        pass
    
    def _parse_autotrader_price(self, price_text: str) -> float:
        """Parse AutoTrader price format"""
        pass
```

#### `gatherers/craigslist_gatherer.py`
```python
class CraigslistGatherer(BaseGatherer):
    """
    Concrete implementation for Craigslist.
    """
    
    async def gather_listing_page(self, url: str) -> List[CarPosting]:
        """Craigslist-specific listing page gathering"""
        pass
    
    async def gather_detail_page(self, url: str) -> CarPosting:
        """Craigslist-specific detail page gathering"""
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
class CarGathererBot:
    """
    Discord bot for receiving notifications and interacting with gathered data.
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
        Show gatherer statistics.
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
class CarGathererApplication:
    """
    Main application coordinating all components.
    """
    
    def __init__(self):
        self.settings = Settings.load_from_env()
        self.db_manager = DatabaseManager(self.settings.DATABASE_URL)
        self.discord_bot = CarGathererBot(
            self.settings.DISCORD_BOT_TOKEN,
            self.db_manager
        )
        self.gatherers: List[BaseGatherer] = []
        self.scheduler = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def initialize(self):
        """
        Initialize all components:
        1. Load configuration
        2. Connect to database
        3. Initialize gatherers
        4. Start Discord bot
        """
        pass
    
    def register_gatherer(self, gatherer: BaseGatherer):
        """Register a gatherer instance"""
        pass
    
    async def run_all_gatherers(self):
        """Run all registered gatherers concurrently"""
        pass
    
    async def process_new_postings(self, postings: List[CarPosting]):
        """
        Process newly gathered postings:
        1. Check for duplicates
        2. Check for price changes
        3. Save to database
        4. Send Discord notifications
        """
        pass
    
    def start_scheduler(self):
        """Start scheduled gathering tasks"""
        pass
    
    def run(self):
        """Main application entry point"""
        pass
    
    def shutdown(self):
        """Graceful shutdown of all components"""
        pass


def main():
    """Application entry point"""
    app = CarGathererApplication()
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
DATABASE_URL=sqlite:///inventory_gatherer.db

# Gatherer Settings
GATHERER_INTERVAL_MINUTES=60
MAX_CONCURRENT_GATHERERS=3
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

1. **Scheduled Gathering**:
   - Scheduler triggers gatherer at configured interval
   - Gatherer initializes Playwright browser
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
# Web Gathering
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
   - Test individual gatherer methods
   - Test data model validation
   - Test database operations
   - Test Discord message formatting

2. **Integration Tests**:
   - Test complete gathering workflow
   - Test database persistence
   - Test Discord notification delivery

3. **Mock Data**:
   - Use recorded HTTP responses for gatherer tests
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
   - Run multiple gatherer instances
   - Use message queue for notifications
   - Implement caching layer

## Agile Implementation Plan

### Sprint Overview
The project is broken down into 8 two-week sprints, each with clear deliverables and integrated testing.

---

### Sprint 0: Project Setup & Infrastructure (Week 1-2)

**Goal**: Establish development environment and CI/CD foundation

**Tasks**:
- [ ] Initialize Git repository and branch strategy
- [ ] Set up project structure (directories, `__init__.py` files)
- [ ] Create `requirements.txt` with initial dependencies
- [ ] Set up virtual environment
- [ ] Configure `.env.example` and `.gitignore`
- [ ] Set up pytest configuration
- [ ] Configure logging framework (loguru)
- [ ] Set up code formatting (Black) and linting (Flake8, mypy)
- [ ] Create basic CI/CD pipeline (GitHub Actions)
- [ ] Install Playwright and run `playwright install`

**Deliverables**:
- Working development environment
- Executable test suite (even if empty)
- CI pipeline running on commits

**Testing**:
- Verify all dependencies install correctly
- Run `pytest` successfully (with placeholder tests)
- Verify linting and formatting checks pass

**Definition of Done**:
- Any developer can clone repo and run tests
- CI pipeline shows green status
- Documentation on local setup exists

---

### Sprint 1: Core Data Models & Configuration (Week 3-4)

**Goal**: Build validated data models and configuration management

**Tasks**:
- [ ] Implement `models/car_posting.py` with Pydantic validation
- [ ] Implement `models/gatherer_config.py`
- [ ] Create `config/settings.py` with environment variable loading
- [ ] Implement settings validation
- [ ] Create comprehensive `.env.example`
- [ ] Build `to_dict()` and `from_dict()` methods
- [ ] Add `to_discord_embed()` skeleton method

**Deliverables**:
- Fully validated CarPosting model
- Configuration system loading from .env
- 100% test coverage for models

**Testing**:
```python
# tests/test_models.py
- test_car_posting_validation_success()
- test_car_posting_validation_failures()
- test_car_posting_to_dict_round_trip()
- test_settings_load_from_env()
- test_settings_validation_errors()
- test_gatherer_config_with_defaults()
```

**Acceptance Criteria**:
- Invalid data raises validation errors
- All required fields enforced
- Settings load from .env correctly
- Type hints work with mypy

---

### Sprint 2: Database Layer (Week 5-6)

**Goal**: Implement database operations with full CRUD support

**Tasks**:
- [ ] Design database schema (SQLAlchemy models)
- [ ] Implement `database/db_manager.py`
- [ ] Create database migration system (Alembic)
- [ ] Implement connection pooling
- [ ] Build CRUD operations for CarPosting
- [ ] Implement price history tracking
- [ ] Add database indexes for performance
- [ ] Create cleanup utility for old postings

**Deliverables**:
- Working DatabaseManager with SQLite
- Migration system initialized
- Tested CRUD operations

**Testing**:
```python
# tests/test_database.py
- test_database_connection()
- test_create_tables()
- test_save_new_posting()
- test_save_duplicate_posting_updates()
- test_get_posting_by_id()
- test_get_postings_with_filters()
- test_price_history_tracking()
- test_cleanup_old_postings()
# Use in-memory SQLite for fast tests
```

**Integration Tests**:
- Test with both SQLite and PostgreSQL (Docker)
- Test concurrent access
- Test transaction rollback

**Acceptance Criteria**:
- Can save and retrieve postings
- Price history tracks changes
- No SQL injection vulnerabilities
- Tests run in < 5 seconds

---

### Sprint 3: Base Gatherer Framework (Week 7-8)

**Goal**: Create reusable gatherer foundation with Playwright

**Tasks**:
- [ ] Implement `gatherers/base_gatherer.py` abstract class
- [ ] Build browser initialization/cleanup
- [ ] Implement helper methods (extract_text, extract_number)
- [ ] Add screenshot capability for debugging
- [ ] Implement duplicate detection logic
- [ ] Add price change detection
- [ ] Create retry mechanism for network failures
- [ ] Implement rate limiting
- [ ] Add user agent rotation

**Deliverables**:
- Complete BaseGatherer abstract class
- Helper utilities tested
- Mock gatherer for testing

**Testing**:
```python
# tests/test_base_gatherer.py
- test_browser_initialization()
- test_browser_cleanup()
- test_extract_text_from_selector()
- test_extract_number_parsing()
- test_screenshot_capture()
- test_duplicate_detection()
- test_price_change_detection()
- test_retry_on_network_failure()
# Use pytest-playwright fixtures
```

**Mock Implementation**:
- Create `MockGatherer` for testing
- Use recorded HTML for consistent tests

**Acceptance Criteria**:
- Browser launches and closes cleanly
- Helper methods handle missing elements gracefully
- Retry logic works on failures
- Memory leaks avoided (browser cleanup)

---

### Sprint 4: First Gatherer Implementation (Week 9-10)

**Goal**: Implement one complete gatherer (Craigslist - simpler structure)

**Tasks**:
- [ ] Research Craigslist HTML structure
- [ ] Implement `gatherers/craigslist_gatherer.py`
- [ ] Create Craigslist GathererConfig
- [ ] Implement `gather_listing_page()`
- [ ] Implement `gather_detail_page()`
- [ ] Handle pagination
- [ ] Parse Craigslist-specific price format
- [ ] Extract images and metadata
- [ ] Add error handling for missing fields

**Deliverables**:
- Working CraigslistGatherer
- Can gather at least 10 listings
- Data persists to database

**Testing**:
```python
# tests/test_craigslist_gatherer.py
- test_gather_listing_page() # Use saved HTML
- test_gather_detail_page()
- test_parse_price_formats()
- test_pagination_handling()
- test_handle_missing_images()
- test_handle_missing_fields()
# Integration test with real site (optional, tagged @slow)
```

**Manual Testing**:
- Run gatherer against live Craigslist
- Verify data accuracy manually
- Check for edge cases (deleted posts, etc.)

**Acceptance Criteria**:
- Successfully gathers 100+ listings
- All required fields populated
- Handles errors without crashing
- Respects rate limits (no 429 errors)

---

### Sprint 5: Discord Bot Foundation (Week 11-12)

**Goal**: Create Discord bot with basic notification capability

**Tasks**:
- [ ] Implement `discord_bot/bot.py`
- [ ] Set up Discord bot token in .env
- [ ] Implement bot startup/shutdown
- [ ] Create `discord_bot/formatters.py`
- [ ] Implement `create_posting_embed()`
- [ ] Implement `send_new_posting_notification()`
- [ ] Add basic error handling
- [ ] Test embed formatting

**Deliverables**:
- Discord bot connects successfully
- Can send formatted car posting embeds
- Graceful shutdown implemented

**Testing**:
```python
# tests/test_discord_bot.py
- test_bot_initialization()
- test_create_posting_embed()
- test_send_notification() # Mock Discord API
- test_bot_graceful_shutdown()
- test_handle_discord_rate_limits()
```

**Manual Testing**:
- Create test Discord server
- Send test notifications
- Verify embed formatting looks good
- Test with various posting data

**Acceptance Criteria**:
- Bot shows online in Discord
- Embeds display correctly with images
- No crashes on Discord API errors
- Rate limiting respected

---

### Sprint 6: Integration & Notifications (Week 13-14)

**Goal**: Connect all components and implement notification flow

**Tasks**:
- [ ] Implement `main.py` CarGathererApplication
- [ ] Connect gatherer → database → Discord flow
- [ ] Implement `process_new_postings()`
- [ ] Add price drop notifications
- [ ] Create scheduler for periodic gathering
- [ ] Implement daily summary feature
- [ ] Add application health checks
- [ ] Create startup/shutdown orchestration

**Deliverables**:
- End-to-end working system
- Automated gathering on schedule
- Notifications firing correctly

**Testing**:
```python
# tests/test_integration.py
- test_gatherer_to_database_flow()
- test_new_posting_triggers_notification()
- test_price_drop_triggers_alert()
- test_scheduler_runs_gatherers()
- test_graceful_shutdown_all_components()
# End-to-end test with all components
```

**Integration Testing**:
- Run full system for 1 hour
- Verify notifications sent
- Check database has new entries
- Monitor memory usage

**Acceptance Criteria**:
- System runs autonomously
- New postings appear in Discord
- Price drops detected and alerted
- No memory leaks over 24 hours

---

### Sprint 7: Additional Gatherers & Commands (Week 15-16)

**Goal**: Add more gatherers and Discord command functionality

**Tasks**:
- [ ] Implement `gatherers/autotrader_gatherer.py`
- [ ] Implement `gatherers/facebook_gatherer.py` (if feasible)
- [ ] Create `discord_bot/commands.py`
- [ ] Implement `!search` command
- [ ] Implement `!recent` command
- [ ] Implement `!watch` command
- [ ] Implement `!stats` command
- [ ] Add help command documentation

**Deliverables**:
- 2-3 working gatherers
- Interactive Discord commands
- Multi-platform gathering

**Testing**:
```python
# tests/test_autotrader_gatherer.py
# tests/test_facebook_gatherer.py
# tests/test_bot_commands.py
- test_search_command_with_filters()
- test_recent_command()
- test_watch_command()
- test_stats_command()
- test_invalid_command_handling()
```

**User Acceptance Testing**:
- Have users test Discord commands
- Gather feedback on UX
- Test with various search parameters

**Acceptance Criteria**:
- All gatherers running concurrently
- Commands respond within 3 seconds
- Search filters work correctly
- Command help is clear

---

### Sprint 8: Polish, Optimization & Documentation (Week 17-18)

**Goal**: Production readiness and documentation

**Tasks**:
- [ ] Performance optimization (database queries, async operations)
- [ ] Add comprehensive error handling
- [ ] Implement monitoring/logging
- [ ] Create Docker containerization
- [ ] Write deployment documentation
- [ ] Create user guide for Discord commands
- [ ] Add administrator documentation
- [ ] Security audit (secrets, rate limiting, input validation)
- [ ] Load testing
- [ ] Create backup/restore procedures

**Deliverables**:
- Production-ready application
- Complete documentation
- Docker deployment option
- Performance benchmarks

**Testing**:
```python
# tests/test_performance.py
- test_gather_1000_listings_performance()
- test_database_query_performance()
- test_concurrent_gatherer_performance()
- test_memory_usage_stability()
```

**Production Readiness Checklist**:
- [ ] All tests passing (>90% coverage)
- [ ] No security vulnerabilities
- [ ] Error handling comprehensive
- [ ] Logging structured and useful
- [ ] Monitoring dashboards created
- [ ] Documentation complete
- [ ] Backup procedures tested
- [ ] Rollback plan documented

**Acceptance Criteria**:
- Can handle 10,000+ postings in database
- Gathers 500+ listings without errors
- Responds to commands in <2 seconds
- Docker container runs successfully
- Documentation allows new developer to onboard

---

## Testing Strategy by Type

### Unit Tests (Run on every commit)
- Fast (<5 seconds total)
- Mock all external dependencies
- 90%+ code coverage target
- Use pytest fixtures for common setup

### Integration Tests (Run on PR)
- Test component interactions
- Use Docker for external services (PostgreSQL, Discord mock)
- Test real Playwright browser
- ~1-2 minutes runtime

### End-to-End Tests (Run nightly)
- Full system test
- May use real websites (with caution)
- Verify complete workflows
- ~5-10 minutes runtime

### Manual Testing Checklist (Before each sprint demo)
- [ ] Run gatherer against live sites
- [ ] Test Discord notifications in test server
- [ ] Verify database persistence
- [ ] Check logs for errors
- [ ] Test all Discord commands
- [ ] Verify price drop detection

---

## Sprint Ceremonies

### Daily Standups (5-10 minutes)
- What did I complete yesterday?
- What will I work on today?
- Any blockers?

### Sprint Planning (2 hours at sprint start)
- Review sprint goal
- Break down tasks
- Estimate effort
- Commit to deliverables

### Sprint Review/Demo (1 hour at sprint end)
- Demonstrate working features
- Gather stakeholder feedback
- Update product backlog

### Sprint Retrospective (1 hour)
- What went well?
- What could improve?
- Action items for next sprint

---

## Definition of Ready (Before starting a task)
- [ ] Task clearly defined
- [ ] Acceptance criteria written
- [ ] Dependencies identified
- [ ] Test scenarios outlined
- [ ] Estimated and sized

## Definition of Done (Before marking task complete)
- [ ] Code written and reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests passing (if applicable)
- [ ] Documentation updated
- [ ] No new linting errors
- [ ] Manually tested
- [ ] Committed to version control
- [ ] Deployed to dev environment

---

## Risk Management

### High Priority Risks

**Risk**: Website structure changes breaking gatherers
- **Mitigation**: Design flexible selectors, implement gatherer health checks
- **Monitoring**: Alert on consecutive gatherer failures

**Risk**: Discord rate limiting
- **Mitigation**: Implement notification queuing, respect rate limits
- **Monitoring**: Track notification send rates

**Risk**: Database performance degradation
- **Mitigation**: Proper indexing, cleanup old data, connection pooling
- **Monitoring**: Query performance metrics

**Risk**: Playwright browser memory leaks
- **Mitigation**: Proper cleanup, restart browser periodically
- **Monitoring**: Memory usage tracking

**Risk**: Secrets exposure
- **Mitigation**: Never commit .env, use environment variables
- **Monitoring**: Git hooks to prevent secret commits

---

## Success Metrics

### Sprint-level Metrics
- Velocity (story points completed)
- Test coverage percentage
- Bug count
- Code review turnaround time

### Product Metrics
- Number of postings gathered per day
- Notification accuracy (% of new postings caught)
- Price drop detection accuracy
- Discord command usage
- System uptime

### Quality Metrics
- Test coverage >90%
- Zero critical security vulnerabilities
- <5% error rate in gatherers
- <2 second command response time

---

## Future Enhancements (Post-MVP Backlog)

1. Machine learning for price prediction
2. Multi-language support
3. Web dashboard for visualization
4. Email notifications
5. Mobile app integration
6. Advanced filtering and saved searches
7. Price trend analysis and charts
8. Integration with more car listing platforms
9. Geo-location based searches
10. Image similarity detection (find similar cars)
