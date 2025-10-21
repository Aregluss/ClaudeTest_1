#!/usr/bin/env python3
"""
Car Scraper - Main Entry Point

Simple web scraper for Response Motors inventory.
Scrapes listings and stores them in CSV format.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from car_scraper.scrapers import ResponseMotorsScraper
from car_scraper.database import CSVDatabaseManager


def print_separator(char="=", length=80):
    """Print a separator line"""
    print(char * length)


def print_posting(posting, index: int):
    """Pretty print a car posting"""
    print(f"\n{index}. {posting.title}")
    print(f"   URL: {posting.source_url}")

    if posting.year:
        print(f"   Year: {posting.year}")
    if posting.make:
        print(f"   Make: {posting.make}")
    if posting.model:
        print(f"   Model: {posting.model}")
    if posting.price:
        print(f"   Price: ${posting.price:,.2f}")
    if posting.mileage:
        print(f"   Mileage: {posting.mileage:,} miles")
    if posting.description:
        desc = posting.description[:100] + "..." if len(posting.description) > 100 else posting.description
        print(f"   Description: {desc}")


def main():
    """Main application entry point"""

    print_separator()
    print("Car Scraper - Response Motors")
    print_separator()

    # Initialize database
    db = CSVDatabaseManager("car_postings.csv")
    print(f"\nDatabase: car_postings.csv")
    print(f"Existing postings in database: {db.count_postings()}")

    # Initialize scraper
    print("\nInitializing scraper...")
    scraper = ResponseMotorsScraper(headless=True)

    # Scrape listings
    print_separator()
    print("Starting scrape...")
    print_separator()

    try:
        postings = scraper.scrape()

        print_separator()
        print(f"\nScraping Complete!")
        print(f"Found {len(postings)} listings")
        print_separator()

        if not postings:
            print("\nNo listings found. This could mean:")
            print("1. The website structure has changed")
            print("2. The selectors need to be adjusted")
            print("3. The page requires authentication or has anti-bot measures")
            print("\nCheck 'page_source.html' if it was saved for manual inspection.")
            return

        # Save to database
        print("\nSaving to database...")
        new_count = 0
        updated_count = 0

        for posting in postings:
            is_new = db.save_posting(posting)
            if is_new:
                new_count += 1
            else:
                updated_count += 1

        print(f"New postings: {new_count}")
        print(f"Updated postings: {updated_count}")

        # Display all scraped postings
        print_separator()
        print("SCRAPED LISTINGS:")
        print_separator()

        for idx, posting in enumerate(postings, 1):
            print_posting(posting, idx)

        print_separator()
        print(f"\nTotal postings in database: {db.count_postings()}")
        print(f"Data saved to: car_postings.csv")
        print_separator()

        # Show summary statistics
        print("\nSUMMARY STATISTICS:")
        print_separator()

        prices = [p.price for p in postings if p.price]
        if prices:
            print(f"Average Price: ${sum(prices) / len(prices):,.2f}")
            print(f"Min Price: ${min(prices):,.2f}")
            print(f"Max Price: ${max(prices):,.2f}")

        mileages = [p.mileage for p in postings if p.mileage]
        if mileages:
            print(f"Average Mileage: {sum(mileages) // len(mileages):,} miles")

        years = [p.year for p in postings if p.year]
        if years:
            print(f"Year Range: {min(years)} - {max(years)}")

        print_separator()

    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        sys.exit(0)

    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
