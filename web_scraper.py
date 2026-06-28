"""
Web Scraper - Product Search & Extraction Module
Handles product search and data extraction from Rami Levy website using Playwright + BeautifulSoup4.
Parses HTML with CSS selectors for product information: [data-productid], [data-price], [data-outofstock], [data-category]
"""

from typing import Dict, Optional


class WebScraper:
    """
    Scrapes product information from Rami Levy website.

    Key features:
    - Search for products by name
    - Extract product details (price, availability, category)
    - Quick availability check
    - Mock data support when page=None (for testing)
    - Graceful error handling with error messages in response dicts
    """

    BASE_URL = "https://www.rami-levy.co.il/he/online"
    SEARCH_URL = BASE_URL + "/search?s="
    CART_URL = BASE_URL + "/cart"
    TIMEOUT_MS = 5000

    def __init__(self):
        """Initialize WebScraper"""
        pass

    def search_product(self, page, product_name: str) -> Dict:
        """
        Search for a product on Rami Levy by name.

        Args:
            page: Playwright page object (or None for mock data in testing)
            product_name: Name of product to search for

        Returns:
            {
                'found': bool,           # Whether product was found
                'url': str,              # Product URL (empty if not found)
                'name': str,             # Product name (empty if not found)
                'price': float,          # Product price (0 if not found)
                'error': str             # Error message (empty if success)
            }
        """
        try:
            # Handle testing case: page=None returns mock data
            if page is None:
                return self._mock_search_product(product_name)

            # Method-level import to avoid module-level dependency issues
            from bs4 import BeautifulSoup

            # Navigate to search URL with product name query
            search_url = self.SEARCH_URL + product_name
            page.goto(search_url, wait_until="networkidle", timeout=self.TIMEOUT_MS)

            # Get page content and parse with BeautifulSoup
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')

            # Look for product results - try to find first product with data-productid
            product_element = soup.find(attrs={"data-productid": True})

            if not product_element:
                # No product found
                return {
                    'found': False,
                    'url': '',
                    'name': '',
                    'price': 0,
                    'error': f'Product "{product_name}" not found'
                }

            # Extract product URL
            product_link = product_element.find('a', href=True)
            product_url = product_link['href'] if product_link else ''

            # Make URL absolute if relative
            if product_url and not product_url.startswith('http'):
                product_url = self.BASE_URL + product_url

            # Extract product name
            name_element = product_element.find(attrs={"data-productname": True})
            product_name_found = name_element.get('data-productname', '') if name_element else ''

            # If name not found via data attribute, try text content
            if not product_name_found:
                name_element = product_element.find(['h2', 'h3', 'span'])
                product_name_found = name_element.get_text(strip=True) if name_element else ''

            # Extract price
            price = 0
            price_element = product_element.find(attrs={"data-price": True})
            if price_element:
                try:
                    price = float(price_element.get('data-price', 0))
                except (ValueError, TypeError):
                    price = 0
            else:
                # Try alternate price selectors
                price_elem = product_element.find(class_=lambda x: x and 'price' in x.lower())
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    try:
                        # Remove currency symbols and parse
                        price = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
                    except (ValueError, AttributeError):
                        price = 0

            return {
                'found': True,
                'url': product_url,
                'name': product_name_found,
                'price': price,
                'error': ''
            }

        except Exception as e:
            # Graceful error handling
            return {
                'found': False,
                'url': '',
                'name': '',
                'price': 0,
                'error': f'Error searching for product: {str(e)}'
            }

    def get_product_details(self, page, product_url: str) -> Dict:
        """
        Extract detailed information from a product page.

        Args:
            page: Playwright page object (or None for mock data in testing)
            product_url: Full URL of product page

        Returns:
            {
                'price': float,          # Product price
                'availability': bool,    # Whether product is in stock
                'category': str,         # Product category
                'error': str             # Error message (empty if success)
            }
        """
        try:
            # Handle testing case: page=None returns mock data
            if page is None:
                return self._mock_get_product_details(product_url)

            # Method-level import to avoid module-level dependency issues
            from bs4 import BeautifulSoup

            # Navigate to product URL
            page.goto(product_url, wait_until="networkidle", timeout=self.TIMEOUT_MS)

            # Get page content and parse with BeautifulSoup
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract price from [data-price] attribute
            price = 0
            price_element = soup.find(attrs={"data-price": True})
            if price_element:
                try:
                    price = float(price_element.get('data-price', 0))
                except (ValueError, TypeError):
                    price = 0
            else:
                # Try alternate price selector
                price_elem = soup.find(class_=lambda x: x and 'price' in x.lower())
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    try:
                        price = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
                    except (ValueError, AttributeError):
                        price = 0

            # Check availability - look for [data-outofstock] attribute
            out_of_stock_element = soup.find(attrs={"data-outofstock": True})
            availability = out_of_stock_element is None  # Available if NOT out of stock

            # Alternative: check for "out of stock" text
            if not out_of_stock_element:
                body_text = soup.get_text().lower()
                availability = 'out of stock' not in body_text and 'אין במלאי' not in body_text

            # Extract category from breadcrumb or [data-category]
            category = ''
            category_element = soup.find(attrs={"data-category": True})
            if category_element:
                category = category_element.get('data-category', '')
            else:
                # Try breadcrumb navigation
                breadcrumb = soup.find(class_=lambda x: x and 'breadcrumb' in x.lower())
                if breadcrumb:
                    breadcrumb_items = breadcrumb.find_all(['a', 'span'])
                    if len(breadcrumb_items) > 1:
                        # Take the second-to-last as category (last is usually product name)
                        category = breadcrumb_items[-2].get_text(strip=True)

            return {
                'price': price,
                'availability': availability,
                'category': category,
                'error': ''
            }

        except Exception as e:
            # Graceful error handling
            return {
                'price': 0,
                'availability': False,
                'category': '',
                'error': f'Error getting product details: {str(e)}'
            }

    def is_product_available(self, page, product_url: str) -> bool:
        """
        Quick availability check for a product.

        Uses get_product_details internally and returns availability boolean.

        Args:
            page: Playwright page object (or None for mock data in testing)
            product_url: Full URL of product page

        Returns:
            True if product is in stock, False otherwise
        """
        details = self.get_product_details(page, product_url)
        return details.get('availability', False)

    # ============================================================================
    # Private Mock Data Methods (for testing)
    # ============================================================================

    def _mock_search_product(self, product_name: str) -> Dict:
        """
        Generate mock search result data for testing.

        Args:
            product_name: Product name to search for

        Returns:
            Mock product search result
        """
        return {
            'found': True,
            'url': f'{self.BASE_URL}/product/mock-{product_name.lower().replace(" ", "-")}',
            'name': f'{product_name} - Mock Product',
            'price': 29.99,
            'error': ''
        }

    def _mock_get_product_details(self, product_url: str) -> Dict:
        """
        Generate mock product details for testing.

        Args:
            product_url: Product URL (not used in mock)

        Returns:
            Mock product details
        """
        return {
            'price': 29.99,
            'availability': True,
            'category': 'Mock Category',
            'error': ''
        }
