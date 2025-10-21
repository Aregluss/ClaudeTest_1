"""Data gatherer for RM inventory"""

import re
import hashlib
from typing import List, Optional
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser

from car_scraper.models import CarPosting


class RMGatherer:
    """
    Data gatherer for RM (responsemotors.com) inventory page.
    Uses Playwright for dynamic page rendering.
    """

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize data gatherer.

        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        self.base_url = "https://responsemotors.com/inventory/"
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def gather_data(self) -> List[CarPosting]:
        """
        Gather all car listings from RM inventory.

        Returns:
            List of CarPosting instances
        """
        postings = []

        with sync_playwright() as playwright:
            # Launch browser
            self.browser = playwright.chromium.launch(headless=self.headless)
            self.page = self.browser.new_page()
            self.page.set_default_timeout(self.timeout)

            try:
                print(f"Navigating to {self.base_url}...")
                self.page.goto(self.base_url)

                # Wait for page to load - adjust selector based on actual page
                print("Waiting for inventory to load...")
                self.page.wait_for_load_state('networkidle')

                # Extract listings
                postings = self._extract_listings()

                print(f"Successfully gathered {len(postings)} listings")

            except Exception as e:
                print(f"Error during data gathering: {e}")
                # Take screenshot for debugging
                self._take_screenshot("error_screenshot.png")

            finally:
                # Clean up
                if self.page:
                    self.page.close()
                if self.browser:
                    self.browser.close()

        return postings

    def _extract_listings(self) -> List[CarPosting]:
        """Extract all car listings from the current page"""
        postings = []

        # Try multiple common selectors for car listing containers
        # We'll need to adjust these based on the actual HTML structure
        possible_selectors = [
            '.vehicle-card',
            '.inventory-item',
            '.car-listing',
            'article.vehicle',
            '[data-vehicle]',
            '.listing-item',
        ]

        listing_elements = None
        used_selector = None

        for selector in possible_selectors:
            elements = self.page.query_selector_all(selector)
            if elements and len(elements) > 0:
                listing_elements = elements
                used_selector = selector
                print(f"Found {len(elements)} listings using selector: {selector}")
                break

        if not listing_elements:
            # Fallback: try to find any reasonable container
            print("Warning: Could not find listings with common selectors.")
            print("Page title:", self.page.title())

            # Get page content for debugging
            content = self.page.content()
            print(f"Page content length: {len(content)} characters")

            # Try to save HTML for manual inspection
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Saved page source to 'page_source.html' for inspection")

            return postings

        # Extract data from each listing
        for idx, element in enumerate(listing_elements):
            try:
                posting = self._extract_posting_from_element(element, idx, used_selector)
                if posting:
                    postings.append(posting)
            except Exception as e:
                print(f"Error extracting listing {idx}: {e}")

        return postings

    def _extract_posting_from_element(self, element, idx: int, parent_selector: str) -> Optional[CarPosting]:
        """Extract car posting data from a single element"""

        # Try to extract URL first
        url_element = element.query_selector('a[href]')
        if url_element:
            url = url_element.get_attribute('href')
            if url and not url.startswith('http'):
                url = f"https://responsemotors.com{url}"
        else:
            url = f"{self.base_url}#listing-{idx}"

        # Generate unique ID from URL
        posting_id = hashlib.md5(url.encode()).hexdigest()[:16]

        # Extract title - try multiple selectors
        title = self._safe_extract_text(element, [
            'h2', 'h3', 'h4',
            '.title', '.vehicle-title', '.car-title',
            '[data-title]'
        ]) or f"Vehicle {idx + 1}"

        # Extract price
        price_text = self._safe_extract_text(element, [
            '.price', '.vehicle-price', '[data-price]',
            'span.price', 'div.price'
        ])
        price = self._parse_price(price_text) if price_text else None

        # Extract mileage
        mileage_text = self._safe_extract_text(element, [
            '.mileage', '.miles', '[data-mileage]',
            'span.mileage', 'div.mileage'
        ])
        mileage = self._parse_mileage(mileage_text) if mileage_text else None

        # Extract year
        year = self._extract_year(title)

        # Extract make and model (from title)
        make, model = self._extract_make_model(title)

        # Extract image
        img_element = element.query_selector('img')
        thumbnail_url = None
        if img_element:
            thumbnail_url = img_element.get_attribute('src')
            if thumbnail_url and not thumbnail_url.startswith('http'):
                thumbnail_url = f"https://responsemotors.com{thumbnail_url}"

        # Extract description/details
        description = self._safe_extract_text(element, [
            '.description', '.details', '[data-description]'
        ])

        # Create CarPosting instance
        posting = CarPosting(
            id=posting_id,
            source_url=url,
            source_platform="rm",
            title=title.strip() if title else "Unknown Vehicle",
            make=make,
            model=model,
            year=year,
            mileage=mileage,
            price=price,
            currency="USD",
            description=description,
            thumbnail_url=thumbnail_url,
            image_urls=[thumbnail_url] if thumbnail_url else [],
            gathered_at=datetime.now()
        )

        return posting

    def _safe_extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """Try multiple selectors to extract text"""
        for selector in selectors:
            try:
                el = element.query_selector(selector)
                if el:
                    text = el.inner_text().strip()
                    if text:
                        return text
            except Exception:
                continue
        return None

    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text like '$25,999' or '25999'"""
        if not price_text:
            return None

        # Remove currency symbols and commas
        cleaned = re.sub(r'[,$]', '', price_text)

        # Extract first number
        match = re.search(r'\d+(?:\.\d+)?', cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass

        return None

    def _parse_mileage(self, mileage_text: str) -> Optional[int]:
        """Parse mileage from text like '45,000 miles' or '45000'"""
        if not mileage_text:
            return None

        # Remove commas and non-digits
        cleaned = re.sub(r'[,]', '', mileage_text)

        # Extract first number
        match = re.search(r'\d+', cleaned)
        if match:
            try:
                return int(match.group())
            except ValueError:
                pass

        return None

    def _extract_year(self, title: str) -> Optional[int]:
        """Extract year from title like '2020 Honda Civic'"""
        if not title:
            return None

        # Look for 4-digit year (1900-2099)
        match = re.search(r'\b(19\d{2}|20\d{2})\b', title)
        if match:
            return int(match.group())

        return None

    def _extract_make_model(self, title: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract make and model from title.
        This is a simple implementation - may need refinement.
        """
        if not title:
            return None, None

        # Remove year from title
        title_no_year = re.sub(r'\b(19\d{2}|20\d{2})\b', '', title).strip()

        # Split into words
        words = title_no_year.split()

        if len(words) >= 2:
            make = words[0]
            model = ' '.join(words[1:3])  # Take next 1-2 words as model
            return make, model
        elif len(words) == 1:
            return words[0], None

        return None, None

    def _take_screenshot(self, filename: str = "screenshot.png"):
        """Take a screenshot for debugging"""
        if self.page:
            try:
                self.page.screenshot(path=filename)
                print(f"Screenshot saved to {filename}")
            except Exception as e:
                print(f"Could not take screenshot: {e}")
