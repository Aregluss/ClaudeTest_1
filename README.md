# Car Inventory Data Gatherer - v1.0

A Python application for gathering and analyzing car inventory data from automotive websites. This tool helps track vehicle listings, pricing, and availability over time.

## Version 1.0 - Features

- Automated data gathering from Response Motors inventory
- CSV-based data storage with structured schemas
- Console-based reporting and statistics
- Duplicate detection and update tracking
- Extensible architecture for multiple data sources

## Running Locally

### Prerequisites

- Python 3.9 or higher
- macOS, Linux, or Windows with WSL
- Internet connection

### Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ClaudeTest_1

# 2. Run the automated setup script
./setup.sh

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Run the application
python main.py
```

### Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install browser automation tools
playwright install chromium

# Run the application
python main.py
```

## How It Works

1. **Data Collection**: Connects to automotive inventory websites
2. **Data Extraction**: Gathers vehicle information (make, model, price, mileage, etc.)
3. **Data Storage**: Saves structured data to CSV format
4. **Analysis**: Displays summary statistics and trends
5. **Tracking**: Monitors changes in listings over time

## Output

The application generates:
- `car_postings.csv` - Structured vehicle data
- Console reports with statistics (pricing trends, inventory counts)
- Debug files when needed (`page_source.html`, screenshots)

## Data Schema

Each vehicle record includes:
- Unique identifier and source URL
- Vehicle details (make, model, year, mileage)
- Pricing information
- Location and description
- Image URLs
- Timestamp of data collection

## Project Structure

```
car_scraper/
├── models/          # Data models and validation
├── database/        # Data persistence layer (CSV)
├── scrapers/        # Data collection modules
└── utils/           # Helper utilities

main.py              # Application entry point
requirements.txt     # Python dependencies
setup.sh            # Automated setup script
```

## Configuration

To adjust data collection parameters, edit the relevant configuration in:
- `car_scraper/scrapers/response_motors_scraper.py`

## Troubleshooting

**No data collected?**
- Ensure internet connection is active
- Check that dependencies are installed: `pip list`
- Verify browser automation is working: `playwright install chromium`

**Permission errors?**
- Make setup script executable: `chmod +x setup.sh`
- Ensure write permissions in the project directory

**Import errors?**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Roadmap

**v1.0** (Current)
- ✅ CSV data storage
- ✅ Response Motors integration
- ✅ Basic statistics and reporting

**v2.0** (Planned)
- SQLite database support
- Discord notifications
- Price change alerts
- Multiple source support

**v3.0** (Future)
- Web dashboard
- Scheduled automation
- Advanced analytics
- API endpoints

## License

MIT License - See LICENSE file for details

---

*Built with Claude Code*
