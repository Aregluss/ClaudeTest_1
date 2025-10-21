# Quick Start Guide

## Inventory Data Gatherer - v1.0

This is a minimal viable product that gathers data from https://responsemotors.com/inventory/ and saves results to CSV.

## Installation (One-time setup)

```bash
# Option 1: Use the setup script (easiest)
./setup.sh

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Running the Data Gatherer

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python main.py
```

## What It Does

1. Opens the RM inventory page with Playwright
2. Gathers car listings data (title, price, mileage, year, make, model)
3. Saves to `car_postings.csv`
4. Displays results in your terminal
5. Shows summary statistics (avg price, mileage range, etc.)

## Output Files

- **car_postings.csv** - Your gathered data
- **page_source.html** - HTML source (created if selectors need debugging)
- **error_screenshot.png** - Screenshot if errors occur

## Customizing the Data Gatherer

If the gatherer doesn't find listings, you may need to adjust the selectors:

1. Run with visible browser to see what's happening:
   ```python
   # Edit main.py, change line 58 to:
   gatherer = RMGatherer(headless=False)
   ```

2. Inspect `page_source.html` to find the right selectors

3. Edit `inventory_gatherer/gatherers/rm_gatherer.py`:
   - **Line 62**: Update `possible_selectors` list
   - **Lines 139-147**: Adjust field extraction selectors

## Example Output

```
================================================================================
Car Data Gatherer - RM
================================================================================

Database: car_postings.csv
Existing postings in database: 0

Initializing data gatherer...
================================================================================
Starting data gathering...
================================================================================
Navigating to https://responsemotors.com/inventory/...
Waiting for inventory to load...
Found 24 listings using selector: .vehicle-card
Successfully gathered 24 listings
================================================================================

Data Gathering Complete!
Found 24 listings
================================================================================

Saving to database...
New postings: 24
Updated postings: 0
================================================================================
GATHERED LISTINGS:
================================================================================

1. 2020 Honda Civic LX
   URL: https://responsemotors.com/vehicle/123
   Year: 2020
   Make: Honda
   Model: Civic LX
   Price: $18,995.00
   Mileage: 35,400 miles

[... more listings ...]

================================================================================
Total postings in database: 24
Data saved to: car_postings.csv
================================================================================

SUMMARY STATISTICS:
================================================================================
Average Price: $23,456.78
Min Price: $12,500.00
Max Price: $45,900.00
Average Mileage: 42,350 miles
Year Range: 2015 - 2023
================================================================================
```

## CSV Format

The CSV includes these fields:

| Field | Description |
|-------|-------------|
| id | Unique identifier (MD5 hash) |
| source_url | Link to the listing |
| title | Full title/description |
| make | Car manufacturer |
| model | Car model |
| year | Manufacturing year |
| mileage | Odometer reading |
| price | Listed price |
| description | Additional details |
| thumbnail_url | Main image URL |
| scraped_at | Timestamp |

## Troubleshooting

### "No listings found"
- The website may have changed its HTML structure
- Try running with `headless=False` to see the browser
- Check `page_source.html` to inspect the actual HTML
- Update selectors in the scraper

### "Module not found" errors
- Make sure you activated the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Playwright browser not found
- Run: `playwright install chromium`

## Next Steps

Once the basic scraper works:

1. **Add more fields**: Edit CarPosting model and scraper
2. **SQLite database**: Replace CSVDatabaseManager with SQLite version
3. **Price tracking**: Detect price changes on re-runs
4. **Discord notifications**: Add Discord bot integration
5. **Scheduling**: Add cron job or systemd service for automated scraping

## Architecture

```
main.py
  ├─> ResponseMotorsScraper (Playwright-based)
  │     ├─> Navigates to website
  │     ├─> Extracts listings
  │     └─> Returns List[CarPosting]
  │
  └─> CSVDatabaseManager
        ├─> Saves postings
        ├─> Detects duplicates
        └─> Writes to car_postings.csv
```

Clean, simple, and ready to extend!
