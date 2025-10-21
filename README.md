# Car Scraper - MVP

A simple web scraper for Response Motors inventory listings.

## Features

- Scrapes car listings from responsemotors.com
- Stores data in CSV format
- Displays results in terminal
- Tracks new vs updated listings
- Shows summary statistics

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install requirements
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Run the Scraper

```bash
python main.py
```

## Output

The scraper will:
1. Navigate to the Response Motors inventory page
2. Extract car listings
3. Save to `car_postings.csv`
4. Display results in terminal with statistics

## Project Structure

```
car_scraper/
├── models/
│   └── car_posting.py       # CarPosting data model
├── database/
│   └── csv_manager.py       # CSV database implementation
└── scrapers/
    └── response_motors_scraper.py  # Website scraper

main.py                       # Entry point
requirements.txt              # Dependencies
car_postings.csv             # Generated data file
```

## CSV Database

Data is stored in `car_postings.csv` with the following fields:
- id, source_url, source_platform
- title, make, model, year, mileage, price
- description, location
- image_urls, thumbnail_url
- scraped_at, features, condition, vin

## Troubleshooting

### No listings found?

1. Check `page_source.html` (auto-saved on first run)
2. Run with visible browser to see what happens:
   ```python
   # Edit main.py line 63:
   scraper = ResponseMotorsScraper(headless=False)
   ```
3. The website structure may have changed - selectors may need adjustment

### Adjusting Selectors

Edit `car_scraper/scrapers/response_motors_scraper.py`:
- Line 62: Add website-specific selectors to `possible_selectors`
- Lines 139-147: Adjust field extraction selectors

## Future Enhancements

- SQLite database support
- Discord notifications
- Multiple website support
- Scheduled scraping
- Price change tracking

---

**Original Project**: ClaudeTest_1 - Testing Claude Code Integration with GH
