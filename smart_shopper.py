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

    def connect_to_chrome(self) -> bool:
        """
        Connect to user's Chrome browser.

        Instructions:
        1. Open Chrome (or open if not already open)
        2. In a terminal, start Chrome with debugging:
           chrome --remote-debugging-port=9222

        Returns:
            True if connected successfully
        """
        print("🌐 Connecting to your Chrome browser...")
        print("   Make sure Chrome is running with: chrome --remote-debugging-port=9222\n")

        if not self.connector.check_chrome_running():
            print("✗ Chrome not found on port 9222")
            print("   Starting Chrome...")
            if not self.connector.start_chrome():
                print("   ✗ Could not start Chrome")
                return False

        self.page = self.connector.connect()
        if self.page:
            print(f"✓ Connected to Chrome!")
            print(f"  Current URL: {self.page.url}\n")
            return True
        else:
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

        shopping_list = []
        base_url = "https://www.rami-levy.co.il/he"

        for query in queries:
            print(f"Searching: {query}...")

            try:
                # Navigate to search page
                search_url = f"{base_url}/online/search?q={query}"
                self.page.goto(search_url, wait_until="domcontentloaded", timeout=15000)

                # Wait for products to load (YOUR Chrome loads faster, no detection!)
                self.page.wait_for_timeout(2000)

                # Get products from page
                products = self.page.query_selector_all('[id*="product"]')

                if products:
                    print(f"   ✓ Found {len(products)} results")

                    # Extract first product
                    first_product = products[0]
                    product_id = first_product.get_attribute("id").replace("product-", "")
                    product_text = first_product.inner_text()

                    # Parse price
                    import re
                    price_match = re.search(r'(\d+\.?\d*)\s*שקל', product_text)
                    price = float(price_match.group(1)) if price_match else 0

                    item = {
                        "query": query,
                        "id": product_id,
                        "name": product_text.split("|")[0].strip()[:50],
                        "price": price,
                        "barcode": product_id
                    }

                    shopping_list.append(item)
                    print(f"      └─ {item['name']} - ₪{price}\n")
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
        Add all items from shopping list to cart in batch.

        Args:
            shopping_list: List of products to add

        Returns:
            {
                'success': bool,
                'added_count': int,
                'failed_count': int,
                'message': str
            }
        """
        if not self.page:
            return {
                "success": False,
                "added_count": 0,
                "failed_count": len(shopping_list),
                "message": "✗ Not connected to Chrome"
            }

        print(f"\n🛒 Adding {len(shopping_list)} items to cart...\n")

        added = 0
        failed = 0

        for item in shopping_list:
            try:
                # Navigate to home first
                self.page.goto("https://www.rami-levy.co.il/he", wait_until="domcontentloaded", timeout=15000)
                self.page.wait_for_timeout(1000)

                # Click product by ID
                selector = f'[id="product-{item["id"]}"]'
                product_button = self.page.query_selector(selector)

                if product_button:
                    product_button.click()
                    self.page.wait_for_timeout(1000)

                    # Click + button (SVG)
                    self.page.evaluate("""() => {
                        const svgs = document.querySelectorAll('svg');
                        for (let svg of svgs) {
                            if (svg.querySelector('polygon')) {
                                svg.parentElement.click();
                                return true;
                            }
                        }
                        return false;
                    }""")

                    print(f"✓ Added: {item['name'][:40]}")
                    added += 1
                else:
                    print(f"✗ Not found: {item['name'][:40]}")
                    failed += 1

                self.page.wait_for_timeout(500)

            except Exception as e:
                print(f"✗ Error adding {item['name'][:40]}: {str(e)}")
                failed += 1

        return {
            "success": added > 0,
            "added_count": added,
            "failed_count": failed,
            "message": f"✓ Added {added} items, {failed} failed"
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
