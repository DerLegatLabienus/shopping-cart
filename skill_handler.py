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
    # Class-level browser instance for persistence across method calls
    # Browser stays OPEN between method calls - you can interact with it manually
    _persistent_browser_manager = None
    _persistent_page = None

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

        ⭐ PERSISTENT BROWSER: The browser STAYS OPEN after this call!
        - First call: Opens new Chrome window (visible, headless=False)
        - Subsequent calls: Reuse same browser, cart items persist
        - Items added to cart stay in the browser until explicitly closed
        - Use stop_shopping() to close browser when completely done
        - Each call to this method adds more items to the same cart

        🤖 ANTI-BOT DETECTION:
        - Browser uses stealth mode to avoid detection
        - If you see "I'm not a robot" CAPTCHA: SOLVE IT MANUALLY
        - Browser will stay open, you can interact with it
        - After solving CAPTCHA, call this method again to continue
        - Or shop manually in the browser - skill tracks your cart

        Args:
            query: User query (e.g., "milk bread" or "lentils")

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
            web_scraper = WebScraper()
            cart_automation = CartAutomation()

            # Step 3: Use persistent browser if available, otherwise create one
            # IMPORTANT: Keep browser open - do NOT close it automatically
            if ShoppingListSkill._persistent_browser_manager and ShoppingListSkill._persistent_page:
                # Reuse existing persistent browser
                browser_manager = ShoppingListSkill._persistent_browser_manager
                page = ShoppingListSkill._persistent_page
                result['message'] = "Using existing browser session..."
            else:
                # Create new persistent browser
                browser_manager = BrowserManager()
                open_result = browser_manager.open_browser()
                if not open_result.get('success'):
                    result['message'] = f"❌ Failed to open browser: {open_result.get('message')}"
                    return result

                # Store for persistence
                ShoppingListSkill._persistent_browser_manager = browser_manager
                ShoppingListSkill._persistent_page = browser_manager.page
                page = browser_manager.page
                result['message'] = "Browser opened and will stay open for shopping"

            result['browser_active'] = True

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
            added_barcodes = set()  # Track added products to avoid duplicates
            for idx, product in enumerate(products_to_add):
                product_name = product.get('name', '')

                # IMPORTANT: Always pass English name to web_scraper
                # web_scraper will translate to Hebrew automatically
                # (Passing Hebrew name directly breaks translation logic)
                search_term = product_name

                try:
                    # Close delivery modal and product panels before each search
                    try:
                        page.evaluate("""() => {
                            // Close delivery modal
                            const modal = document.getElementById('delivery-modal');
                            if (modal) modal.style.display = 'none';
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) backdrop.style.display = 'none';

                            // Close product details panel by clicking escape or close button
                            const closeBtn = document.querySelector('[data-testid="close-icon"]') ||
                                           document.querySelector('[class*="close"]') ||
                                           document.querySelector('button.btn-close');
                            if (closeBtn && closeBtn.offsetParent !== null) {
                                closeBtn.click();
                            }

                            // Close cart drawer if open
                            const cartDrawer = document.querySelector('[class*="cart-drawer"]') ||
                                             document.querySelector('[class*="cart-side"]');
                            if (cartDrawer && cartDrawer.style.display !== 'none') {
                                const drawerClose = cartDrawer.querySelector('[class*="close"]');
                                if (drawerClose) drawerClose.click();
                            }
                        }""")
                    except:
                        pass

                    time.sleep(1)

                    # Navigate back to home to reset page state before each search
                    # This prevents cart panel interference
                    try:
                        page.goto('https://www.rami-levy.co.il/he', wait_until="domcontentloaded", timeout=15000)
                        page.wait_for_timeout(2000)
                    except:
                        pass

                    time.sleep(0.5)

                    # Search for product on website using Hebrew product names (if available)
                    search_result = web_scraper.search_product(page, search_term)

                    if not search_result.get('found'):
                        result['missing_items'].append({
                            'name': product_name,
                            'reason': search_result.get('error', 'Product not found')
                        })
                        continue

                    # Check if this barcode was already added (avoid duplicates)
                    barcode = search_result.get('url', '')
                    if barcode in added_barcodes:
                        result['missing_items'].append({
                            'name': product_name,
                            'reason': 'Duplicate product (already added)'
                        })
                        continue

                    # Product found, add to cart via + button click
                    product_url = search_result.get('url', '')
                    add_result = cart_automation.add_to_cart(page, product_url, quantity=1)

                    if add_result.get('success'):
                        added_barcodes.add(barcode)  # Track this barcode
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

            # Step 6: Verify items are actually in cart drawer
            verification = self.verify_cart_contents(page, result['added_items'])

            # Step 7: Get cart total
            cart_total = verification.get('total_price', 0.0)
            result['cart_total'] = cart_total
            result['verified_items'] = verification.get('verified_items', [])
            result['verified_count'] = verification.get('verified_count', 0)

            # Step 8: Update browser session config
            browser_manager.update_session_config({
                'items_added': len(result['added_items']),
                'items_verified': verification.get('verified_count', 0),
                'cart_total': cart_total
            })

            # Step 9: Generate summary message with verification status
            if result['added_items']:
                result['success'] = True
                verify_msg = f" ({verification.get('verified_count', 0)} verified in cart)"
                result['message'] = f"✅ Added {len(result['added_items'])} items{verify_msg}. Cart total: ₪{cart_total:.2f}"
            else:
                result['message'] = f"⚠️ No items could be added. {len(result['missing_items'])} items were missing."

            return result

        except Exception as e:
            result['message'] = f"❌ Unexpected error: {str(e)}"
            result['browser_active'] = False
            return result

    def verify_cart_contents(self, page, added_items: List[Dict]) -> Dict:
        """
        Verify that items are actually in the Rami Levy cart drawer.

        Args:
            page: Playwright page object
            added_items: List of items that were added

        Returns:
            {
                'verified_count': int,
                'total_price': float,
                'verified_items': [str],
                'message': str
            }
        """
        try:
            # Get page content - cart drawer is on the same page
            html_content = page.content()

            # Extract prices from the HTML to verify items are in cart
            import re

            verified_items = []
            total_found = 0.0

            # Look for price patterns in HTML using Hebrew word "שקל"
            # Format: "13.80 שקל" or "7.00 שקל"
            price_pattern = r'(\d+\.?\d*)\s*שקל'
            prices_found = re.findall(price_pattern, html_content)

            # Convert to floats and track
            prices = [float(p) for p in prices_found if 1 < float(p) < 1000]  # Filter reasonable prices
            prices = sorted(set(prices), reverse=True)  # Remove duplicates, sort descending

            # Match prices with added items
            matched_prices = set()
            for item in added_items:
                item_price = item.get('price', 0)
                if item_price in prices and item_price not in matched_prices:
                    verified_items.append(item.get('name', 'Unknown')[:40])
                    total_found += item_price
                    matched_prices.add(item_price)

            # Also check page text for product names containing "עדשים" (lentils)
            product_indicators = ['עדשים', 'עדשות', 'חלב', 'יוגורט']  # Common Hebrew product indicators
            for indicator in product_indicators:
                if indicator in html_content:
                    # Product type found in cart
                    for item in added_items:
                        item_name = item.get('name', '')
                        if indicator in item_name and item_name not in verified_items:
                            verified_items.append(item_name[:40])
                            break

            # Calculate cart total from all prices found
            # Total is typically the largest price found
            if prices:
                cart_total = max(prices[:3]) if len(prices) > 0 else sum(matched_prices)
                # Actually, sum matched prices for more accuracy
                if matched_prices:
                    cart_total = sum(matched_prices)
            else:
                cart_total = total_found

            return {
                'verified_count': len(set(verified_items)),
                'total_price': cart_total,
                'verified_items': list(set(verified_items)),
                'message': f'✅ Verified {len(set(verified_items))}/{len(added_items)} items in cart (Total: ₪{cart_total:.2f})'
            }

        except Exception as e:
            return {
                'verified_count': 0,
                'total_price': 0.0,
                'verified_items': [],
                'message': f'⚠️ Verification failed: {str(e)}'
            }

    def open_persistent_browser(self) -> Dict:
        """
        Open a persistent browser that stays open for shopping.
        Browser can be reused for multiple add_to_cart calls.

        Returns:
            {
                'success': bool,
                'message': str,
                'browser_active': bool
            }
        """
        try:
            from browser_manager import BrowserManager
        except ImportError:
            return {
                'success': False,
                'message': '❌ Failed to import BrowserManager',
                'browser_active': False
            }

        try:
            # Close existing browser if any
            if ShoppingListSkill._persistent_browser_manager:
                try:
                    ShoppingListSkill._persistent_browser_manager.close_browser()
                except:
                    pass

            # Open new persistent browser
            manager = BrowserManager()
            result = manager.open_browser()

            if result.get('success'):
                ShoppingListSkill._persistent_browser_manager = manager
                ShoppingListSkill._persistent_page = manager.page

                return {
                    'success': True,
                    'message': '✅ Browser opened and ready for shopping! Use "continue shopping" to add items.',
                    'browser_active': True
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ Failed to open browser: {result.get('message')}",
                    'browser_active': False
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Error opening browser: {str(e)}',
                'browser_active': False
            }

    def continue_shopping(self, query: str) -> Dict:
        """
        Add items to cart using the persistent browser session.
        Browser stays open between calls for continuous shopping.

        Args:
            query: Shopping query (e.g., "milk bread" or "lentils")

        Returns:
            {
                'success': bool,
                'added_items': [...],
                'cart_total': float,
                'browser_active': bool,
                'message': str
            }
        """
        # Check if browser is still open
        if not ShoppingListSkill._persistent_browser_manager or not ShoppingListSkill._persistent_page:
            return {
                'success': False,
                'added_items': [],
                'cart_total': 0.0,
                'browser_active': False,
                'message': '❌ Browser not open. Use "open shopping" first.'
            }

        try:
            from web_scraper import WebScraper
            from cart_automation import CartAutomation
            import time

            page = ShoppingListSkill._persistent_page

            # Process query to get products
            query_result = self.process_query(query)
            products = query_result.get('products', [])

            if not products:
                return {
                    'success': False,
                    'added_items': [],
                    'cart_total': 0.0,
                    'browser_active': True,
                    'message': f"❌ No products found for: {query}"
                }

            # Initialize modules
            web_scraper = WebScraper()
            cart_automation = CartAutomation()

            result = {
                'success': False,
                'added_items': [],
                'missing_items': [],
                'cart_total': 0.0,
                'browser_active': True,
                'message': ''
            }

            products_to_add = products[:5]
            added_barcodes = set()

            # Add products
            for idx, product in enumerate(products_to_add):
                product_name = product.get('name', '')
                search_term = product.get('hebrew_name', product_name)

                try:
                    # Close modals
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

                    # Search
                    search_result = web_scraper.search_product(page, search_term)

                    if not search_result.get('found'):
                        result['missing_items'].append({
                            'name': product_name,
                            'reason': search_result.get('error', 'Product not found')
                        })
                        continue

                    # Check for duplicate
                    barcode = search_result.get('url', '')
                    if barcode in added_barcodes:
                        result['missing_items'].append({
                            'name': product_name,
                            'reason': 'Duplicate product (already added)'
                        })
                        continue

                    # Add to cart
                    add_result = cart_automation.add_to_cart(page, barcode, quantity=1)

                    if add_result.get('success'):
                        added_barcodes.add(barcode)
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

            # Verify items in cart
            verification = self.verify_cart_contents(page, result['added_items'])

            result['cart_total'] = verification.get('total_price', 0.0)
            result['verified_items'] = verification.get('verified_items', [])
            result['verified_count'] = verification.get('verified_count', 0)

            # Update session
            manager = ShoppingListSkill._persistent_browser_manager
            manager.update_session_config({
                'items_added': len(result['added_items']),
                'items_verified': verification.get('verified_count', 0),
                'cart_total': result['cart_total']
            })

            # Set success
            result['success'] = len(result['added_items']) > 0
            result['message'] = f"✅ Added {len(result['added_items'])} items. Cart: ₪{result['cart_total']:.2f}"

            return result

        except Exception as e:
            return {
                'success': False,
                'added_items': [],
                'cart_total': 0.0,
                'browser_active': True,
                'message': f'❌ Error: {str(e)}'
            }

    def shop_vegetarian_family(self) -> Dict:
        """
        Automated shopping: Build vegetarian family list and add to cart.

        One-click shopping:
        1. Builds typical vegetarian family shopping list
        2. Auto-launches Chrome if needed
        3. Searches for items on Rami Levy
        4. Batch adds all items to cart
        5. Shows summary of what was added/missing

        Returns:
            {
                'success': bool,
                'items_added': [...],
                'items_missing': [...],
                'added_count': int,
                'missing_count': int,
                'total_price': float,
                'message': str
            }
        """
        # Typical vegetarian family shopping list
        shopping_queries = [
            "milk",
            "yogurt",
            "cheese",
            "bread",
            "eggs",
            "lentils",
            "chickpeas",
            "tomatoes",
            "onions",
            "vegetables"
        ]

        # Search and batch add
        result = self.search_and_batch_add(" ".join(shopping_queries))

        # Build detailed summary
        items_added = result.get('shopping_list', [])
        added_names = [item['name'] for item in items_added]

        # Find what's missing from our original list
        items_missing = []
        for query in shopping_queries:
            if not any(query.lower() in item['name'].lower() or query.lower() in item['query'].lower()
                      for item in items_added):
                items_missing.append(query)

        return {
            'success': result['success'],
            'items_added': items_added,
            'items_missing': items_missing,
            'added_count': result['added_count'],
            'missing_count': len(items_missing),
            'total_price': result['total_price'],
            'message': result['message']
        }

    def search_and_batch_add(self, query: str) -> Dict:
        """
        Smart shopping workflow: Search products via YOUR Chrome → Build list → Batch add to cart.

        NO bot detection because it uses YOUR browser session (trusted by Rami Levy).

        Workflow:
        1. Connect to your Chrome browser (must be running with --remote-debugging-port=9222)
        2. Search for products using your session
        3. Display shopping list
        4. Batch add all items to cart

        Args:
            query: Space-separated product names (e.g., "milk pita yogurt")

        Returns:
            {
                'success': bool,
                'shopping_list': [...],
                'added_count': int,
                'failed_count': int,
                'total_price': float,
                'message': str
            }

        Usage:
            # Start Chrome first:
            # chrome --remote-debugging-port=9222

            # Then use skill:
            result = skill.search_and_batch_add("milk pita yogurt")
        """
        try:
            from smart_shopper import SmartShopper
        except ImportError:
            return {
                'success': False,
                'shopping_list': [],
                'added_count': 0,
                'failed_count': 0,
                'total_price': 0.0,
                'message': '❌ Could not import SmartShopper. Make sure all dependencies are installed.'
            }

        try:
            # Parse queries
            queries = query.strip().split()
            if not queries:
                return {
                    'success': False,
                    'shopping_list': [],
                    'added_count': 0,
                    'failed_count': 0,
                    'total_price': 0.0,
                    'message': '❌ No search terms provided'
                }

            # Initialize shopper
            shopper = SmartShopper()

            # Connect to Chrome
            if not shopper.connect_to_chrome():
                return {
                    'success': False,
                    'shopping_list': [],
                    'added_count': 0,
                    'failed_count': 0,
                    'total_price': 0.0,
                    'message': '❌ Could not connect to Chrome. Make sure it\'s running with: chrome --remote-debugging-port=9222'
                }

            # Search for products
            search_result = shopper.search_for_products(queries)

            if not search_result['success']:
                shopper.close()
                return {
                    'success': False,
                    'shopping_list': [],
                    'added_count': 0,
                    'failed_count': 0,
                    'total_price': 0.0,
                    'message': f"❌ {search_result['message']}"
                }

            # Batch add to cart
            add_result = shopper.batch_add_to_cart(search_result['shopping_list'])

            # Keep browser open for user to continue shopping
            # (Don't close it)

            return {
                'success': add_result['success'],
                'shopping_list': search_result['shopping_list'],
                'added_count': add_result['added_count'],
                'failed_count': add_result['failed_count'],
                'total_price': search_result['total_price'],
                'message': f"✅ {add_result['message']}"
            }

        except Exception as e:
            return {
                'success': False,
                'shopping_list': [],
                'added_count': 0,
                'failed_count': 0,
                'total_price': 0.0,
                'message': f'❌ Error: {str(e)}'
            }

    def stop_shopping(self) -> Dict:
        """
        Close the persistent browser session when done shopping.

        Returns:
            {
                'success': bool,
                'message': str
            }
        """
        if not ShoppingListSkill._persistent_browser_manager:
            return {
                'success': False,
                'message': '❌ No browser session to close'
            }

        try:
            result = ShoppingListSkill._persistent_browser_manager.close_browser()
            ShoppingListSkill._persistent_browser_manager = None
            ShoppingListSkill._persistent_page = None

            return {
                'success': True,
                'message': '✅ Browser closed. Your cart is saved on Rami Levy website.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Error closing browser: {str(e)}'
            }

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
