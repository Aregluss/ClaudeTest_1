"""CSV-based database manager for car postings"""

import csv
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from car_scraper.models import CarPosting


class CSVDatabaseManager:
    """
    Simple CSV-based database for car postings.
    Stores data in CSV format with JSON for complex fields.
    Extensible design allows easy migration to SQLite later.
    """

    def __init__(self, csv_path: str = "car_postings.csv"):
        """
        Initialize CSV database manager.

        Args:
            csv_path: Path to the CSV file
        """
        self.csv_path = Path(csv_path)
        self.fieldnames = [
            'id', 'source_url', 'source_platform', 'title', 'make', 'model',
            'year', 'mileage', 'price', 'currency', 'description', 'location',
            'image_urls', 'thumbnail_url', 'scraped_at', 'features',
            'condition', 'vin'
        ]
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not self.csv_path.exists():
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def save_posting(self, posting: CarPosting) -> bool:
        """
        Save or update a car posting.

        Args:
            posting: CarPosting instance to save

        Returns:
            True if new posting, False if updated existing
        """
        # Check if posting already exists
        existing = self.get_posting_by_id(posting.id)
        is_new = existing is None

        if not is_new:
            # Remove the old entry
            self._remove_posting(posting.id)

        # Append the new/updated posting
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            row = self._posting_to_row(posting)
            writer.writerow(row)

        return is_new

    def get_posting_by_id(self, posting_id: str) -> Optional[CarPosting]:
        """
        Retrieve a posting by ID.

        Args:
            posting_id: Unique identifier

        Returns:
            CarPosting instance or None if not found
        """
        with open(self.csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id'] == posting_id:
                    return self._row_to_posting(row)
        return None

    def get_all_postings(self) -> List[CarPosting]:
        """
        Get all postings from the database.

        Returns:
            List of CarPosting instances
        """
        postings = []
        with open(self.csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    posting = self._row_to_posting(row)
                    postings.append(posting)
                except Exception as e:
                    print(f"Warning: Could not parse row: {e}")
        return postings

    def get_recent_postings(self, limit: int = 10) -> List[CarPosting]:
        """
        Get most recent postings.

        Args:
            limit: Maximum number of postings to return

        Returns:
            List of recent CarPosting instances
        """
        all_postings = self.get_all_postings()
        # Sort by scraped_at descending
        all_postings.sort(key=lambda p: p.scraped_at, reverse=True)
        return all_postings[:limit]

    def count_postings(self) -> int:
        """
        Count total number of postings.

        Returns:
            Number of postings in database
        """
        with open(self.csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return sum(1 for _ in reader)

    def _remove_posting(self, posting_id: str):
        """Remove a posting from the CSV file"""
        temp_path = self.csv_path.with_suffix('.tmp')

        with open(self.csv_path, 'r', newline='', encoding='utf-8') as f_in:
            with open(temp_path, 'w', newline='', encoding='utf-8') as f_out:
                reader = csv.DictReader(f_in)
                writer = csv.DictWriter(f_out, fieldnames=self.fieldnames)
                writer.writeheader()

                for row in reader:
                    if row['id'] != posting_id:
                        writer.writerow(row)

        temp_path.replace(self.csv_path)

    def _posting_to_row(self, posting: CarPosting) -> dict:
        """Convert CarPosting to CSV row"""
        data = posting.to_dict()

        # Convert complex types to JSON strings
        data['image_urls'] = json.dumps(data.get('image_urls', []))
        data['features'] = json.dumps(data.get('features', {}))
        data['scraped_at'] = data['scraped_at'].isoformat() if isinstance(data.get('scraped_at'), datetime) else data.get('scraped_at', '')

        # Ensure all fields are present
        row = {field: data.get(field, '') for field in self.fieldnames}
        return row

    def _row_to_posting(self, row: dict) -> CarPosting:
        """Convert CSV row to CarPosting"""
        # Parse JSON fields
        if row.get('image_urls'):
            row['image_urls'] = json.loads(row['image_urls']) if row['image_urls'] else []
        else:
            row['image_urls'] = []

        if row.get('features'):
            row['features'] = json.loads(row['features']) if row['features'] else {}
        else:
            row['features'] = {}

        # Parse datetime
        if row.get('scraped_at'):
            row['scraped_at'] = datetime.fromisoformat(row['scraped_at'])

        # Convert numeric fields
        for field in ['year', 'mileage']:
            if row.get(field):
                try:
                    row[field] = int(row[field])
                except (ValueError, TypeError):
                    row[field] = None

        if row.get('price'):
            try:
                row['price'] = float(row['price'])
            except (ValueError, TypeError):
                row['price'] = None

        # Remove empty strings, replace with None
        for key, value in row.items():
            if value == '':
                row[key] = None

        return CarPosting(**row)
