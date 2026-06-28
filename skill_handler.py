"""
Rami Levy Vegetarian Shopping List Skill
Main handler for conversational shopping list generation
"""

from search_engine import SearchEngine
from formatters import OutputFormatter
from rami_levy_web import RamiLevyWebIntegration
from typing import Dict, List, Tuple, Optional
import json


class ShoppingListSkill:
    def __init__(self, products_db: str = "rami_levy_products.json"):
        """Initialize the skill with search engine and formatters"""
        self.search_engine = SearchEngine(products_db)
        self.formatter = OutputFormatter()
        self.session_state = {}
        self.current_list = []  # Track items currently in the shopping list
        self.cart = {}  # Track cart contents: {product_id: {item, quantity, verified}}
        self.web = RamiLevyWebIntegration()  # Web integration for Rami Levy website

    def parse_budget_query(self, query: str) -> Optional[Tuple[float, float]]:
        """
        Extract budget constraints from query
        Examples: "under 50", "50-100", "100 shekels"
        Returns: (min_price, max_price)
        """
        query_lower = query.lower()

        # Check for "under X"
        if "under" in query_lower or "below" in query_lower or "less than" in query_lower:
            words = query_lower.split()
            for i, word in enumerate(words):
                if word in ["under", "below", "less"]:
                    if i + 1 < len(words):
                        try:
                            amount = float(''.join(c for c in words[i + 1] if c.isdigit() or c == '.'))
                            if amount > 0:
                                return (0, amount)
                        except:
                            pass

        # Check for "X-Y" range
        if "-" in query_lower:
            parts = query_lower.split("-")
            try:
                min_val = float(''.join(c for c in parts[0] if c.isdigit() or c == '.'))
                max_val = float(''.join(c for c in parts[1] if c.isdigit() or c == '.'))
                if min_val > 0 and max_val > 0:
                    return (min_val, max_val)
            except:
                pass

        return None

    def extract_category_request(self, query: str) -> Optional[List[str]]:
        """
        Extract category requests from query
        Returns list of matching categories or None
        """
        query_lower = query.lower()
        available_categories = self.search_engine.get_categories()

        matched = []
        for cat in available_categories:
            if cat in query_lower or cat.replace("_", " ") in query_lower:
                matched.append(cat)

        # Also check for common terms
        category_aliases = {
            'vegetables': ['veggies', 'produce', 'fresh'],
            'legumes': ['beans', 'lentils', 'chickpeas', 'peas', 'pulses'],
            'grains': ['rice', 'pasta', 'couscous', 'bread'],
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'eggs'],
            'organic': ['organic', 'bio', 'eco'],
            'fruits': ['fruit', 'apple', 'banana', 'orange']
        }

        for category, aliases in category_aliases.items():
            for alias in aliases:
                if alias in query_lower and category not in matched:
                    for cat in available_categories:
                        if cat == category or category in cat:
                            matched.append(cat)
                            break

        return list(set(matched)) if matched else None

    def generate_clarifying_questions(self, query: str) -> List[str]:
        """Generate contextual clarifying questions based on user's query"""
        questions = []

        # Check what's already in query
        has_budget = self.parse_budget_query(query) is not None
        has_category = self.extract_category_request(query) is not None
        has_diet = any(term in query.lower() for term in ['vegan', 'organic', 'kosher'])

        if not has_category:
            questions.append("📂 Which categories interest you? (e.g., vegetables, legumes, dairy, organic, all)")

        if not has_budget:
            questions.append("💰 Do you have a budget in mind? (e.g., under 50 shekels, 100-200)")

        if not has_diet:
            questions.append("🌱 Any dietary preferences? (e.g., vegan, organic, kosher, ready-to-eat)")

        if not questions:
            questions.append("📋 What format would you like? (markdown list, JSON, CSV, table)")

        return questions

    def process_query(self, user_query: str) -> Dict:
        """
        Process user query and return shopping list with metadata
        Returns: {
            'list_markdown': str,
            'products': List[Dict],
            'metadata': Dict,
            'clarifying_questions': List[str],
            'summary': str
        }
        """
        query_lower = user_query.lower()

        # Extract search parameters from query
        name_query = user_query  # Default search term
        budget = self.parse_budget_query(query_lower)
        categories = self.extract_category_request(query_lower)
        dietary_prefs = []

        # Check for dietary preferences
        if any(term in query_lower for term in ['vegan']):
            dietary_prefs.append('vegan')
        if any(term in query_lower for term in ['organic', 'bio']):
            dietary_prefs.append('organic')
        if any(term in query_lower for term in ['kosher', 'gluten']):
            dietary_prefs.append('kosher')
        if any(term in query_lower for term in ['ready']):
            dietary_prefs.append('ready-to-eat')

        # Check for common shopping scenarios to improve search
        if any(term in query_lower for term in ['shopping list', 'groceries', 'ingredients']):
            # This is a general shopping list request - don't restrict by name
            name_query = ""

        # Set price limits
        min_price = budget[0] if budget else 0
        max_price = budget[1] if budget else float('inf')

        # Perform search
        products, metadata = self.search_engine.advanced_search(
            name_query=name_query if name_query.strip() else "",
            categories=categories,
            min_price=min_price,
            max_price=max_price,
            attributes=dietary_prefs if dietary_prefs else None,
            sort_by='price',
            limit=None
        )

        # Generate clarifying questions if results are empty or minimal
        clarifying_questions = []
        if len(products) == 0:
            clarifying_questions = self.generate_clarifying_questions(user_query)

        # Format as markdown (default)
        list_markdown = self.formatter.format_markdown(
            products,
            title=f"Vegetarian Shopping List - Rami Levy"
        )

        # Generate summary
        if len(products) > 0:
            total = self.formatter.calculate_total(products)
            summary = f"✅ Found {len(products)} products totaling ₪{total:.2f}"
        else:
            summary = "❌ No products found matching your criteria"

        return {
            'list_markdown': list_markdown,
            'products': products,
            'metadata': metadata,
            'clarifying_questions': clarifying_questions,
            'summary': summary,
            'user_query': user_query,
            'applied_filters': {
                'categories': categories,
                'budget': budget,
                'dietary_preferences': dietary_prefs
            }
        }

    def format_response(self, user_query: str, output_format: str = "markdown") -> str:
        """
        Process query and format response for user
        output_format: 'markdown', 'json', 'csv', 'html', 'text'
        """
        result = self.process_query(user_query)
        products = result['products']

        if output_format.lower() == 'json':
            return self.formatter.format_json(products)
        elif output_format.lower() == 'csv':
            return self.formatter.format_csv(products)
        elif output_format.lower() == 'html':
            return self.formatter.format_html_table(products)
        elif output_format.lower() == 'text':
            return self.formatter.format_plain_text(products)
        else:  # markdown (default)
            response = result['list_markdown']

            # Add clarifying questions if needed
            if result['clarifying_questions']:
                response += "\n\n---\n\n**Help me refine this list:**\n\n"
                for i, question in enumerate(result['clarifying_questions'], 1):
                    response += f"{i}. {question}\n"

            return response

    def get_categories(self) -> List[str]:
        """Get all available product categories"""
        return self.search_engine.get_categories()

    def get_product_details(self, product_id: str) -> Optional[Dict]:
        """Get detailed information about a specific product"""
        return self.search_engine.get_product_by_id(product_id)

    def build_custom_list(self, product_ids: List[str]) -> Dict:
        """Build a custom shopping list from specific product IDs"""
        products = self.search_engine.get_products_by_ids(product_ids)

        if not products:
            return {
                'list_markdown': "❌ No products found with the given IDs",
                'products': [],
                'total': 0
            }

        total = self.formatter.calculate_total(products)
        list_markdown = self.formatter.format_markdown(
            products,
            title="Custom Shopping List - Rami Levy"
        )

        return {
            'list_markdown': list_markdown,
            'products': products,
            'total': total
        }

    def add_item_to_cart(self, product_id: str, quantity: float = 1.0) -> Dict:
        """
        Add a product to the shopping cart with verification
        Returns: {success: bool, message: str, item: dict, cart_total: float, cart_items: int}
        """
        product = self.search_engine.get_product_by_id(product_id)

        if not product:
            return {
                'success': False,
                'message': f"❌ Product not found: {product_id}",
                'cart_total': self.get_cart_total(),
                'cart_items': len(self.cart)
            }

        # Get minimum price (first size option)
        price = product['sizes'][0]['price'] if product['sizes'] else 0

        # Add to cart
        self.cart[product_id] = {
            'product_id': product_id,
            'name': product['name'],
            'category': product['category'],
            'brand': product['brand'],
            'price_per_unit': price,
            'quantity': quantity,
            'subtotal': price * quantity,
            'verified': True,  # Marked as verified when added
            'added_timestamp': str(self._get_timestamp())
        }

        self.current_list.append(product_id)

        return {
            'success': True,
            'message': f"✅ Added: {product['name']} (₪{price * quantity:.2f})",
            'item': self.cart[product_id],
            'cart_total': self.get_cart_total(),
            'cart_items': len(self.cart),
            'verified': True
        }

    def remove_item_from_cart(self, product_id: str) -> Dict:
        """
        Remove a product from the shopping cart
        Returns: {success: bool, message: str, cart_total: float, cart_items: int}
        """
        if product_id not in self.cart:
            return {
                'success': False,
                'message': f"❌ Product not in cart: {product_id}",
                'cart_total': self.get_cart_total(),
                'cart_items': len(self.cart)
            }

        removed_item = self.cart.pop(product_id)
        if product_id in self.current_list:
            self.current_list.remove(product_id)

        return {
            'success': True,
            'message': f"✅ Removed: {removed_item['name']}",
            'removed_item': removed_item,
            'cart_total': self.get_cart_total(),
            'cart_items': len(self.cart)
        }

    def get_cart_total(self) -> float:
        """Calculate total price of all items in cart"""
        return sum(item['subtotal'] for item in self.cart.values())

    def get_cart_summary(self) -> Dict:
        """Get complete cart summary with all items and verification status"""
        items_list = list(self.cart.values())
        total = self.get_cart_total()

        return {
            'items': items_list,
            'total_items': len(items_list),
            'cart_total': total,
            'all_verified': all(item['verified'] for item in items_list),
            'verified_count': sum(1 for item in items_list if item['verified']),
            'unverified_count': sum(1 for item in items_list if not item['verified']),
            'cart_markdown': self._format_cart_markdown(items_list, total)
        }

    def _format_cart_markdown(self, items: List[Dict], total: float) -> str:
        """Format cart contents as markdown"""
        if not items:
            return "🛒 **Cart is empty**"

        markdown = "# 🛒 Shopping Cart Summary\n\n"
        markdown += f"**Total Items:** {len(items)}\n"
        markdown += f"**Cart Total:** ₪{total:.2f}\n\n"
        markdown += "## Items in Cart\n\n"

        for item in items:
            status = "✅" if item['verified'] else "⚠️"
            markdown += f"{status} **{item['name']}** ({item['brand']})\n"
            markdown += f"   - Category: {item['category']}\n"
            markdown += f"   - Price: ₪{item['price_per_unit']:.2f}\n"
            markdown += f"   - Quantity: {item['quantity']}\n"
            markdown += f"   - Subtotal: ₪{item['subtotal']:.2f}\n\n"

        markdown += f"---\n**Total: ₪{total:.2f}**\n"
        return markdown

    def verify_item_in_cart(self, product_id: str) -> Dict:
        """Verify that a specific item is actually in the cart"""
        if product_id not in self.cart:
            return {
                'verified': False,
                'message': f"❌ Item not found in cart",
                'product_id': product_id
            }

        item = self.cart[product_id]
        return {
            'verified': True,
            'message': f"✅ Item verified in cart",
            'product_id': product_id,
            'item': item,
            'name': item['name'],
            'quantity': item['quantity'],
            'price': item['subtotal']
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def add_items_from_query(self, user_query: str) -> Dict:
        """
        Parse a query and add matching items to cart
        Example: "Add 2kg tomatoes, 1 red lentils 1kg, 2 milk"
        Returns: {added: [], failed: [], cart_total: float}
        """
        results = {
            'added': [],
            'failed': [],
            'cart_total': 0,
            'message': ""
        }

        # This would parse natural language and extract items
        # For now, it demonstrates the structure
        query_lower = user_query.lower()

        # Search for common items mentioned
        for product in self.search_engine.products:
            product_name_lower = product['name'].lower()
            if product_name_lower in query_lower:
                result = self.add_item_to_cart(product['id'])
                if result['success']:
                    results['added'].append({
                        'product_id': product['id'],
                        'name': product['name'],
                        'price': result['item']['subtotal']
                    })
                else:
                    results['failed'].append(product['name'])

        results['cart_total'] = self.get_cart_total()
        results['message'] = f"Added {len(results['added'])} items, {len(results['failed'])} failed"

        return results

    # ============================================================================
    # WEBSITE INTEGRATION - Add items to actual Rami Levy website cart
    # ============================================================================

    def add_to_website_cart(self, product_id: str, quantity: float = 1) -> Dict:
        """
        Add product to Rami Levy website cart with verification

        Args:
            product_id: Product ID from database
            quantity: Quantity to add

        Returns:
            {
                'success': bool,
                'message': str,
                'website_action': str,
                'verification_needed': bool,
                'next_steps': []
            }
        """
        product = self.search_engine.get_product_by_id(product_id)

        if not product:
            return {
                'success': False,
                'message': f"❌ Product not found: {product_id}"
            }

        price = product['sizes'][0]['price'] if product['sizes'] else 0

        # Track in web system
        result = self.web.add_product_to_website_cart(
            product_id=product_id,
            product_name=product['name'],
            quantity=quantity,
            price=price
        )

        return result

    def verify_website_cart_item(self, product_id: str, confirmed_in_cart: bool = None) -> Dict:
        """
        Verify item is actually in Rami Levy website cart

        Args:
            product_id: Product ID
            confirmed_in_cart: User confirmation if item is visible in cart

        Returns:
            {
                'verified': bool,
                'message': str,
                'status': str,
                'actions_needed': []
            }
        """

        if product_id not in self.web.cart_state:
            return {
                'verified': False,
                'message': f"Product {product_id} not in tracking",
                'status': 'not_tracked'
            }

        product = self.web.cart_state[product_id]

        if confirmed_in_cart is not None:
            # User has confirmed whether item is in cart
            result = self.web.mark_item_verified(product_id, confirmed_in_cart)
            return {
                'verified': confirmed_in_cart,
                'message': result['message'],
                'status': product['status']
            }

        # Ask for verification
        return self.web.verify_item_in_website_cart(
            product_id,
            product['product_name'],
            product['subtotal']
        )

    def get_website_cart_status(self) -> Dict:
        """Get status of all items added to Rami Levy website"""
        return self.web.get_cart_status()

    def get_website_verification_checklist(self) -> str:
        """Get markdown checklist of items to verify on Rami Levy website"""
        return self.web.get_verification_checklist()

    def build_shopping_list_for_website(self, criteria: str = None, budget: float = 500) -> Dict:
        """
        Build optimized shopping list and prepare for website shopping

        Args:
            criteria: Shopping criteria (e.g., "vegetables, legumes, dairy")
            budget: Budget limit in shekels

        Returns:
            {
                'products': [],
                'total_estimated': float,
                'workflow': str,
                'next_steps': []
            }
        """

        # Search for products matching criteria
        result = self.process_query(criteria or "vegetables, legumes, dairy short shelf-life")

        products_to_add = []
        total = 0

        for product in result['products']:
            if total >= budget:
                break
            price = product['sizes'][0]['price'] if product['sizes'] else 0
            if total + price <= budget:
                products_to_add.append({
                    'product_id': product['id'],
                    'name': product['name'],
                    'category': product['category'],
                    'price': price,
                    'quantity': 1
                })
                total += price

        # Generate workflow
        workflow = self.web.generate_manual_workflow(products_to_add)

        return {
            'products': products_to_add,
            'total_estimated': total,
            'remaining_budget': budget - total,
            'workflow': workflow,
            'next_steps': [
                "1. Review the shopping list above",
                "2. For each item, go to Rami Levy website and search for it",
                "3. Click 'Add to Cart'",
                "4. After each addition, tell me 'Added [product name]'",
                "5. I'll verify it's in your cart",
                "6. Repeat until all items are added"
            ]
        }

    # ============================================================================
    # BROWSER AUTOMATION INTEGRATION - New Task 5 Methods
    # ============================================================================

    def process_query_with_browser(self, query: str) -> dict:
        """
        Main orchestration method for browser-based shopping automation.

        Processes a user query, builds a shopping list, and automatically adds items
        to the Rami Levy website cart using browser automation.

        Args:
            query: User query (e.g., "build shopping list for 500 shekels")

        Returns:
            {
                'success': bool,                    # Whether operation succeeded
                'message': str,                     # Status message
                'added_items': [                    # Items successfully added
                    {'name': str, 'price': float, 'quantity': int}, ...
                ],
                'missing_items': [                  # Items that could not be added
                    {'name': str, 'reason': str}, ...
                ],
                'cart_total': float,                # Total price in cart
                'browser_active': bool              # Whether browser is still open
            }
        """
        # Import at method level to avoid dependency issues
        try:
            from browser_manager import BrowserManager
            from web_scraper import WebScraper
            from cart_automation import CartAutomation
        except ImportError as e:
            return {
                'success': False,
                'message': f'❌ Failed to import required modules: {str(e)}',
                'added_items': [],
                'missing_items': [],
                'cart_total': 0.0,
                'browser_active': False
            }

        result = {
            'success': False,
            'message': '',
            'added_items': [],
            'missing_items': [],
            'cart_total': 0.0,
            'browser_active': False
        }

        try:
            # Step 1: Process query to build shopping list
            query_result = self.process_query(query)
            products = query_result.get('products', [])

            if not products:
                result['message'] = f"❌ No products found for query: {query}"
                return result

            # Step 2: Initialize modules
            browser_manager = BrowserManager()
            web_scraper = WebScraper()
            cart_automation = CartAutomation()

            # Step 3: Open browser
            open_result = browser_manager.open_browser()
            if not open_result.get('success'):
                result['message'] = f"❌ Failed to open browser: {open_result.get('message')}"
                return result

            result['browser_active'] = True
            page = browser_manager.page

            # Step 3.5: Handle city selection if prompted
            import time
            time.sleep(1)
            city_input = page.query_selector('input[placeholder*="עיר"]') or page.query_selector('input[placeholder*="city"]')
            if city_input:
                city_input.fill("תל אביב")
                time.sleep(0.3)
                confirm_btn = page.query_selector('button:has-text("אישור")') or page.query_selector('button:has-text("OK")')
                if confirm_btn:
                    try:
                        confirm_btn.click()
                        time.sleep(1)
                    except:
                        pass

            # Step 4: Limit to 5 items for performance
            products_to_add = products[:5]

            # Step 5: Process each product
            for idx, product in enumerate(products_to_add):
                product_name = product.get('name', '')

                try:
                    # Close delivery modal if open
                    try:
                        page.evaluate("""() => {
                            const modal = document.getElementById('delivery-modal');
                            if (modal) modal.style.display = 'none';
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) backdrop.style.display = 'none';
                        }""")
                    except:
                        pass

                    time.sleep(0.5)

                    # Search for product on website using Hebrew product names
                    search_result = web_scraper.search_product(page, product_name)

                    if not search_result.get('found'):
                        result['missing_items'].append({
                            'name': product_name,
                            'reason': search_result.get('error', 'Product not found')
                        })
                        continue

                    # Product found, add to cart via + button click
                    product_url = search_result.get('url', '')
                    add_result = cart_automation.add_to_cart(page, product_url, quantity=1)

                    if add_result.get('success'):
                        result['added_items'].append({
                            'name': product_name,
                            'price': search_result.get('price', 0),
                            'quantity': 1
                        })
                    else:
                        result['missing_items'].append({
                            'name': product_name,
                            'reason': add_result.get('message', 'Failed to add to cart')
                        })

                except Exception as e:
                    result['missing_items'].append({
                        'name': product_name,
                        'reason': str(e)
                    })
                    continue

            # Step 6: Get cart total
            cart_total = cart_automation.get_cart_total(page)
            result['cart_total'] = cart_total

            # Set success message
            result['success'] = len(result['added_items']) > 0
            result['message'] = f"✅ Added {len(result['added_items'])} items to cart" if result['success'] else "⚠️ Could not add items"

            # Step 7: Update browser session config
            browser_manager.update_session_config({
                'items_added': len(result['added_items']),
                'cart_total': cart_total
            })

            # Step 8: Generate summary message
            if result['added_items']:
                result['success'] = True
                result['message'] = f"✅ Added {len(result['added_items'])} items to cart. Cart total: ₪{cart_total:.2f}"
            else:
                result['message'] = f"⚠️ No items could be added. {len(result['missing_items'])} items were missing."

            return result

        except Exception as e:
            result['message'] = f"❌ Unexpected error: {str(e)}"
            result['browser_active'] = False
            return result

    def cleanup_browser_session(self) -> dict:
        """
        Clean up and close the browser session.

        Closes the browser window and removes session configuration.

        Returns:
            {
                'success': bool,            # Whether cleanup succeeded
                'message': str,             # Status message
                'browser_closed': bool      # Whether browser was successfully closed
            }
        """
        try:
            from browser_manager import BrowserManager
        except ImportError as e:
            return {
                'success': False,
                'message': f'❌ Failed to import BrowserManager: {str(e)}',
                'browser_closed': False
            }

        try:
            browser_manager = BrowserManager()
            close_result = browser_manager.close_browser()

            return {
                'success': close_result.get('success', False),
                'message': close_result.get('message', ''),
                'browser_closed': close_result.get('success', False)
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Error cleaning up browser: {str(e)}',
                'browser_closed': False
            }

    def _generate_cart_summary(self) -> dict:
        """
        Generate human-readable summary of cart contents.

        Provides a summary of items currently in the shopping cart.

        Returns:
            {
                'summary_markdown': str,    # Markdown-formatted summary
                'items_count': int,         # Number of items in cart
                'estimated_total': float    # Current cart total
            }
        """
        try:
            # Get current cart state
            cart_summary = self.get_cart_summary()

            return {
                'summary_markdown': cart_summary.get('cart_markdown', '🛒 Cart is empty'),
                'items_count': cart_summary.get('total_items', 0),
                'estimated_total': cart_summary.get('cart_total', 0.0)
            }

        except Exception as e:
            return {
                'summary_markdown': f'❌ Error generating summary: {str(e)}',
                'items_count': 0,
                'estimated_total': 0.0
            }


def run_interactive_demo():
    """Run interactive demo of the skill"""
    skill = ShoppingListSkill()

    print("=" * 60)
    print("🛒 Rami Levy Vegetarian Shopping List Skill - Demo")
    print("=" * 60)
    print("\nTry these sample queries:")
    print("  1. 'Find lentils'")
    print("  2. 'Chickpeas under 10 shekels'")
    print("  3. 'Organic vegetables'")
    print("  4. 'Build a vegetarian shopping list for 100 shekels'")
    print("  5. 'Vegan products'")
    print("\nType 'quit' to exit\n")

    while True:
        query = input("📝 Your query: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break

        if not query:
            print("Please enter a query\n")
            continue

        # Ask for output format
        print("\n📊 Output format? (markdown/json/csv/html/text) [default: markdown]")
        format_choice = input("Format: ").strip().lower() or "markdown"

        response = skill.format_response(query, format_choice)

        print("\n" + "=" * 60)
        print(response)
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Run interactive demo
    run_interactive_demo()
