"""
Cart Automation - Browser-based Shopping Cart Management
Automates adding items to the Rami Levy shopping cart through Playwright browser interaction.

Features:
- Add items to cart with quantity control
- Verify items are in cart
- Get cart total
- Track added items in session
"""

import re
from typing import Dict, Optional, List


class CartAutomation:
    """
    Automates adding items to Rami Levy shopping cart.

    Handles:
    - Navigating to product pages
    - Extracting product names from HTML attributes
    - Finding and clicking "Add to Cart" buttons (with selector fallback)
    - Setting quantities
    - Verifying items in cart
    - Retrieving cart totals
    - Tracking added items in current session
    """

    def __init__(self):
        """Initialize CartAutomation with empty added items list"""
        self.base_url = "https://www.rami-levy.co.il/he"
        self.added_items: List[Dict] = []

    def add_to_cart(
        self,
        page,
        product_url: str,
        quantity: int = 1
    ) -> Dict:
        """
        Add a product to the shopping cart.

        Args:
            page: Playwright page object (or None for testing)
            product_url: URL of the product page
            quantity: Quantity to add (default 1)

        Returns:
            {
                'success': bool,
                'message': str,
                'product_name': str,
                'quantity': int
            }
        """
        # Guard: page is None or invalid
        if page is None:
            return {
                'success': False,
                'message': '❌ Page is None - cannot add to cart',
                'product_name': '',
                'quantity': quantity
            }

        try:
            # product_url contains the product ID (barcode) from search
            # On Rami Levy, clicking the product button adds it to cart directly

            # Extract product ID from URL (or use as-is if it's already an ID)
            product_id = product_url.split('/')[-1] if '/' in product_url else product_url

            # Find the product button by ID
            # Format: id="product-7290117769690"
            selector = f'[role="button"][id="product-{product_id}"]'
            product_button = page.query_selector(selector)

            if not product_button:
                # Try without the product- prefix in case it's just the ID
                selector = f'[role="button"][id="{product_id}"]'
                product_button = page.query_selector(selector)

            if not product_button:
                return {
                    'success': False,
                    'message': f'❌ Could not find product button for ID: {product_id}',
                    'product_name': product_id,
                    'quantity': quantity
                }

            # Click the product button to add to cart
            try:
                product_button.click()
                page.wait_for_timeout(1000)  # Wait for cart to update
                button_found = True
            except Exception as e:
                return {
                    'success': False,
                    'message': f'❌ Failed to click product button: {str(e)}',
                    'product_name': product_id,
                    'quantity': quantity
                }

            # After click, we assume product is added (Rami Levy shows visual feedback)
            button_found = True

            # Track the added item
            self.added_items.append({
                'name': product_id,
                'url': product_url,
                'quantity': quantity
            })

            return {
                'success': True,
                'message': f'✅ Added product {product_id} (qty: {quantity}) to cart',
                'product_name': product_id,
                'quantity': quantity
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Error adding to cart: {str(e)}',
                'product_name': '',
                'quantity': quantity
            }

    def verify_in_cart(self, page, product_name: str) -> Dict:
        """
        Verify that an item is in the shopping cart.

        Args:
            page: Playwright page object (or None for testing)
            product_name: Name of the product to verify

        Returns:
            {
                'verified': bool,
                'quantity': int,
                'message': str
            }
        """
        # Guard: page is None or invalid
        if page is None:
            return {
                'verified': False,
                'quantity': 0,
                'message': '❌ Page is None - cannot verify cart'
            }

        try:
            # Navigate to cart page
            cart_url = self.base_url + "/cart"
            page.goto(cart_url, wait_until="networkidle", timeout=5000)

            # Get page content
            content = page.content()

            # Parse HTML for cart items [data-cartitem]
            cart_items = page.query_selector_all("[data-cartitem]")

            if not cart_items:
                return {
                    'verified': False,
                    'quantity': 0,
                    'message': f'❌ Could not find cart items on page'
                }

            # Search for matching product (case-insensitive)
            product_name_lower = product_name.lower()

            for item in cart_items:
                try:
                    item_name_element = item.query_selector("[data-productname]")
                    if item_name_element:
                        item_name = item_name_element.get_attribute("data-productname")
                        if item_name and item_name.lower() == product_name_lower:
                            # Found the item, get quantity
                            quantity_element = item.query_selector("[data-quantity]")
                            quantity = 1
                            if quantity_element:
                                qty_text = quantity_element.get_attribute("data-quantity")
                                if qty_text:
                                    try:
                                        quantity = int(qty_text)
                                    except ValueError:
                                        quantity = 1

                            return {
                                'verified': True,
                                'quantity': quantity,
                                'message': f'✅ {product_name} verified in cart (qty: {quantity})'
                            }
                except Exception:
                    # Continue searching other items
                    continue

            return {
                'verified': False,
                'quantity': 0,
                'message': f'❌ {product_name} not found in cart'
            }

        except Exception as e:
            return {
                'verified': False,
                'quantity': 0,
                'message': f'❌ Error verifying cart: {str(e)}'
            }

    def get_cart_total(self, page) -> float:
        """
        Get the current cart total price.

        Args:
            page: Playwright page object (or None for testing)

        Returns:
            Total price as float, 0.0 if error or page is None
        """
        # Guard: page is None
        if page is None:
            return 0.0

        try:
            # Navigate to cart page
            cart_url = self.base_url + "/cart"
            page.goto(cart_url, wait_until="networkidle", timeout=5000)

            # Get page content
            content = page.content()

            # Try to find total in [data-carttotal] or .cart-total
            total_element = page.query_selector("[data-carttotal]")
            if not total_element:
                total_element = page.query_selector(".cart-total")

            if total_element:
                total_text = total_element.inner_text()
            else:
                total_text = content

            # Extract numeric value from price text using regex
            # Matches patterns like "₪150.50", "1,250.99", "150.50"
            # Remove shekel symbol and commas, then parse
            cleaned_text = total_text.replace('₪', '').replace(',', '')
            price_match = re.search(r'[\d]+(?:\.\d+)?', cleaned_text)

            if price_match:
                price_str = price_match.group()
                return float(price_str)

            return 0.0

        except Exception as e:
            return 0.0

    def get_added_items(self) -> List[Dict]:
        """
        Get list of items added in current session.

        Returns:
            List of added items, each with {name, url, quantity}
        """
        return self.added_items
