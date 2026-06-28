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

    BASE_URL = "https://www.rami-levy.co.il/he"
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
            product_name: Name of product to search for (English or Hebrew)

        Returns:
            {
                'found': bool,           # Whether product was found
                'url': str,              # Product ID (empty if not found)
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

            # Translate common English product names to Hebrew for search
            translations = {
                'milk': 'חלב',
                'yogurt': 'יוגורט',
                'cheese': 'גבינה',
                'eggs': 'ביצים',
                'vegetables': 'ירקות',
                'frozen': 'קפוא',
                'protein': 'חלבון',
                'fruits': 'פירות',
            }

            # Check if product_name needs translation
            search_term = product_name
            if product_name.lower() in translations:
                search_term = translations[product_name.lower()]

            # Navigate to search URL with product name query
            search_url = self.SEARCH_URL + search_term
            page.goto(search_url, wait_until="domcontentloaded", timeout=self.TIMEOUT_MS)

            # Get page content and parse with BeautifulSoup
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')

            # Look for product results using actual Rami Levy selectors
            # Products are divs with role="button" and id="product-BARCODE"
            product_elements = soup.find_all(attrs={'role': 'button', 'id': lambda x: x and 'product-' in x})

            if not product_elements:
                # No products found
                return {
                    'found': False,
                    'url': '',
                    'name': '',
                    'price': 0,
                    'error': f'Product "{product_name}" not found'
                }

            # Search for product matching the name
            product_element = None
            search_term_lower = product_name.lower()

            for elem in product_elements:
                # Get text content of product
                text = elem.get_text().lower()
                # Check if search term is in the product text
                if search_term_lower in text or any(word in text for word in search_term_lower.split()):
                    product_element = elem
                    break

            # If no match found, use first product as fallback
            if not product_element and product_elements:
                product_element = product_elements[0]

            if not product_element:
                # No product found
                return {
                    'found': False,
                    'url': '',
                    'name': '',
                    'price': 0,
                    'error': f'Product "{product_name}" not found'
                }

            # Extract product ID from element id attribute
            # Format: id="product-7290117769690"
            product_id = product_element.get('id', '').replace('product-', '')
            if not product_id:
                product_id = product_name  # Fallback to search term

            # Extract product name and price from full text content
            # Format: "חלב 3% מהדריןתנובה|1 ליטרמחיר המוצר7.20₪7.20שקלים חדשים..."
            full_text = product_element.get_text(strip=True)

            # Extract price: look for ₪ followed by numbers
            import re
            price = 0
            price_match = re.search(r'₪\s*([\d.]+)', full_text)
            if price_match:
                try:
                    price = float(price_match.group(1))
                except (ValueError, AttributeError):
                    price = 0

            # Extract product name: take text before first | or before "מחיר"
            product_name_found = product_name  # Default
            if '|' in full_text:
                product_name_found = full_text.split('|')[0].strip()
            elif 'מחיר' in full_text:
                product_name_found = full_text.split('מחיר')[0].strip()
            else:
                # Use first 50 chars as name
                product_name_found = full_text[:50]

            return {
                'found': True,
                'url': product_id,  # Return product ID to be used in add_to_cart
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
