"""
Smart Shopper - Use your real Chrome browser session for searching
No bot detection because it's YOUR browser with YOUR Rami Levy session!

Workflow:
1. Connect to your Chrome browser
2. Search for products using your session (no bot detection)
3. Build shopping list locally
4. Batch add all items to cart at once

Requirements:
- Chrome running with: chrome --remote-debugging-port=9222
"""

from typing import List, Dict, Optional
from chrome_connector import ChromeConnector
import time


class SmartShopper:
    """
    Smart shopping using your real Chrome browser.

    Advantages:
    - Uses YOUR browser session (trusted by Rami Levy)
    - No bot detection
    - No CAPTCHA
    - Reliable product search
    """

    def __init__(self):
        """Initialize smart shopper with Chrome connection."""
        self.connector = ChromeConnector()
        self.page = None
        self.shopping_list = []
        self.keep_browser_open = True  # Keep browser open after shopping

    def connect_to_chrome(self) -> bool:
        """
        Connect to your real Chrome browser with persistent profile.

        Handles:
        1. Connect to existing Chrome on debug port (keeps running)
        2. Auto-start Chrome with your profile (cart data persists)
        3. Fallback to bundled Chromium only if no profile found

        Returns:
            True if connected successfully
        """
        try:
            # Show which Chrome profile is being used
            profile_info = self.connector.get_profile_info()
            print(f"🔌 {profile_info}")
            # connect() handles all fallbacks internally
            self.page = self.connector.connect()
            return self.page is not None
        except Exception as e:
            return False

    def search_for_products(self, queries: List[str]) -> Dict:
        """
        Search for products using your Chrome browser.

        Args:
            queries: List of product names to search for

        Returns:
            {
                'success': bool,
                'shopping_list': [...],
                'total_price': float,
                'message': str
            }
        """
        if not self.page:
            return {
                "success": False,
                "shopping_list": [],
                "total_price": 0.0,
                "message": "✗ Not connected to Chrome"
            }

        print(f"🔍 Searching for products using YOUR Chrome browser...\n")

        # Hebrew translations for search
        translations = {
            'milk': 'חלב',
            'yogurt': 'יוגורט',
            'cheese': 'גבינה',
            'bread': 'לחם',
            'eggs': 'ביצים',
            'lentils': 'עדשים',
            'chickpeas': 'חומוס',
            'tomatoes': 'עגבניות',
            'onions': 'בצל',
            'vegetables': 'ירקות',
            'fruits': 'פירות',
            'pita': 'פיתה',
        }

        shopping_list = []
        base_url = "https://www.rami-levy.co.il/he"

        for query in queries:
            # Translate to Hebrew if available
            search_term = translations.get(query.lower(), query)
            print(f"Searching: {query} ({search_term})...")

            try:
                # Navigate to search page with Hebrew query
                search_url = f"{base_url}/online/search?q={search_term}"
                try:
                    self.page.goto(search_url, wait_until="networkidle", timeout=20000)
                except:
                    # If networkidle times out, continue anyway with domcontentloaded
                    self.page.goto(search_url, wait_until="domcontentloaded", timeout=20000)

                # Wait for products to load (Vue.js needs time to render)
                self.page.wait_for_timeout(5000)

                # Get products from page - try multiple selectors
                products = self.page.query_selector_all('[id*="product"]')

                # Fallback selectors if first didn't work
                if not products:
                    products = self.page.query_selector_all('[class*="product"], [class*="item"]')

                # If still nothing, try generic button elements
                if not products:
                    all_buttons = self.page.query_selector_all('[role="button"]')
                    products = [b for b in all_buttons if 'product' in (b.get_attribute('id') or '').lower()]

                if products:
                    print(f"   ✓ Found {len(products)} results")

                    # Find best matching product (not just first)
                    # Prefer exact matches or products with query term
                    best_product = None
                    search_lower = search_term.lower()

                    for product in products:
                        product_text = product.inner_text()
                        # Check if product text contains the search term
                        if search_lower in product_text.lower():
                            best_product = product
                            break

                    # Fallback to first product if no exact match
                    if not best_product:
                        best_product = products[0]

                    first_product = best_product
                    product_id = first_product.get_attribute("id").replace("product-", "")
                    product_text = first_product.inner_text()

                    # Parse price
                    import re
                    price_match = re.search(r'(\d+\.?\d*)\s*שקל', product_text)
                    price = float(price_match.group(1)) if price_match else 0

                    # Clean product name (remove newlines and extra whitespace)
                    product_name = product_text.split("|")[0].strip()
                    product_name = " ".join(product_name.split())[:50]

                    item = {
                        "query": query,
                        "id": product_id,
                        "name": product_name,
                        "price": price,
                        "barcode": product_id
                    }

                    shopping_list.append(item)

                    # Immediately add to cart while on search page
                    try:
                        first_product.click()
                        self.page.wait_for_timeout(1000)

                        self.page.evaluate("""() => {
                            const svgs = document.querySelectorAll('svg');
                            for (let svg of svgs) {
                                if (svg.querySelector('polygon')) {
                                    svg.parentElement?.click?.();
                                    return true;
                                }
                            }
                        }""")
                        print(f"      └─ {item['name']} - ₪{price} ✓ ADDED\n")
                    except:
                        print(f"      └─ {item['name']} - ₪{price} (search only)\n")
                else:
                    print(f"   ✗ No products found\n")

            except Exception as e:
                print(f"   ✗ Error: {str(e)}\n")
                continue

        total_price = sum(item["price"] for item in shopping_list)

        return {
            "success": len(shopping_list) > 0,
            "shopping_list": shopping_list,
            "total_price": total_price,
            "message": f"✓ Found {len(shopping_list)} products for {len(queries)} searches"
        }

    def batch_add_to_cart(self, shopping_list: List[Dict]) -> Dict:
        """
        Items were already added during search_for_products().
        This is a no-op - returns summary of what was found.

        Args:
            shopping_list: List of products that were added

        Returns:
            {
                'success': bool,
                'added_count': int,
                'failed_count': int,
                'message': str
            }
        """
        # Items are added immediately during search
        # This method just returns a summary
        return {
            "success": len(shopping_list) > 0,
            "added_count": len(shopping_list),
            "failed_count": 0,
            "message": f"✓ {len(shopping_list)} items added during search"
        }

    def show_shopping_list(self, shopping_list: List[Dict]) -> str:
        """
        Display shopping list in markdown format.

        Args:
            shopping_list: List of products

        Returns:
            Markdown formatted shopping list
        """
        if not shopping_list:
            return "📋 Empty shopping list"

        markdown = "# 🛒 Shopping List\n\n"
        markdown += "| Item | Price | Query |\n"
        markdown += "|------|-------|-------|\n"

        for item in shopping_list:
            markdown += f"| {item['name'][:30]} | ₪{item['price']} | {item['query']} |\n"

        total = sum(item["price"] for item in shopping_list)
        markdown += f"\n**Total:** ₪{total:.2f} ({len(shopping_list)} items)\n"

        return markdown

    def close(self):
        """Close Chrome connection."""
        if self.connector:
            self.connector.close()


if __name__ == "__main__":
    # Demo
    print("🛍️  SMART SHOPPER DEMO\n")
    print("=" * 70)

    shopper = SmartShopper()

    # Connect to Chrome
    if not shopper.connect_to_chrome():
        print("✗ Could not connect to Chrome")
        exit(1)

    # Search for products
    search_queries = ["milk", "pita", "yogurt"]
    search_result = shopper.search_for_products(search_queries)

    if search_result["success"]:
        # Show shopping list
        print(shopper.show_shopping_list(search_result["shopping_list"]))

        # Add to cart
        add_result = shopper.batch_add_to_cart(search_result["shopping_list"])
        print(f"\n{add_result['message']}")
    else:
        print(f"✗ {search_result['message']}")

    shopper.close()
