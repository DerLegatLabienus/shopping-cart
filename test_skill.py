"""
Test Suite for Rami Levy Vegetarian Shopping List Skill
Validates all components: search engine, formatters, skill handler
"""

import sys
from search_engine import SearchEngine
from formatters import OutputFormatter
from skill_handler import ShoppingListSkill


class TestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = 0

    def assert_equal(self, actual, expected, test_name):
        """Assert equality and track result"""
        self.tests_run += 1
        if actual == expected:
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}")
            print(f"     Expected: {expected}")
            print(f"     Got: {actual}")
            return False

    def assert_true(self, condition, test_name):
        """Assert condition is true"""
        self.tests_run += 1
        if condition:
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}")
            return False

    def assert_greater(self, value, threshold, test_name):
        """Assert value is greater than threshold"""
        self.tests_run += 1
        if value > threshold:
            self.passed += 1
            print(f"  ✅ {test_name} (value: {value})")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}")
            print(f"     Expected > {threshold}, got {value}")
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print(f"TEST SUMMARY: {self.passed}/{self.tests_run} passed")
        if self.failed > 0:
            print(f"⚠️  {self.failed} test(s) failed")
        else:
            print("✅ All tests passed!")
        print("=" * 60 + "\n")
        return self.failed == 0

    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "=" * 60)
        print("🧪 RAMI LEVY SHOPPING LIST SKILL - TEST SUITE")
        print("=" * 60 + "\n")

        self.test_search_engine()
        self.test_formatters()
        self.test_skill_handler()
        self.test_cart_management()

        return self.print_summary()


    def test_search_engine(self):
        """Test search engine functionality"""
        print("📖 Testing Search Engine...\n")

        engine = SearchEngine()

        # Test 1: Database loading
        self.assert_greater(len(engine.products), 0, "Database loaded with products")

        # Test 2: Get all categories
        categories = engine.get_categories()
        self.assert_greater(len(categories), 0, "Categories retrieved")

        # Test 3: Fuzzy matching
        score = engine.fuzzy_match("lentil", "Red Lentils")
        self.assert_true(score > 0.7, "Fuzzy match finds similar words (score: {:.2f})".format(score))

        # Test 4: Exact match
        score = engine.fuzzy_match("lentils", "lentils")
        self.assert_equal(score, 1.0, "Exact match scores 1.0")

        # Test 5: Name search
        results = engine.search_by_name("lentils")
        self.assert_greater(len(results), 0, f"Name search finds lentils ({len(results)} results)")

        # Test 6: Category filter
        all_products = engine.products[:]
        legume_products = engine.filter_by_category(all_products, ["legumes"])
        self.assert_greater(len(legume_products), 0, f"Category filter finds legumes ({len(legume_products)} items)")

        # Test 7: Price filter
        cheap_products = engine.filter_by_price_range(all_products, 0, 10)
        self.assert_greater(len(cheap_products), 0, f"Price filter finds items under ₪10 ({len(cheap_products)} items)")

        # Test 8: Attribute filter
        vegan_products = engine.filter_by_attributes(all_products, ["vegan"])
        self.assert_greater(len(vegan_products), 0, f"Attribute filter finds vegan products ({len(vegan_products)} items)")

        # Test 9: Advanced search
        results, metadata = engine.advanced_search(
            name_query="hummus",
            categories=["legumes"],
            max_price=15
        )
        self.assert_greater(len(results), 0, f"Advanced search finds hummus under ₪15 ({len(results)} items)")

        # Test 10: Price stats
        stats = engine.get_price_stats(results)
        self.assert_true(stats['min'] > 0, "Price stats calculated correctly")

        print()

    def test_formatters(self):
        """Test output formatter functionality"""
        print("🎨 Testing Output Formatters...\n")

        formatter = OutputFormatter()

        # Sample data
        sample_products = [
            {
                "id": "prod_001",
                "name": "Red Lentils",
                "category": "legumes",
                "brand": "Rami Levy",
                "sizes": [{"size": "500g", "price": 7.00, "price_per_unit": "1.40 per 100g"}],
                "attributes": ["vegetarian", "vegan"],
                "organic": False
            },
            {
                "id": "prod_063",
                "name": "Organic Tomatoes",
                "category": "organic",
                "brand": "Rami Levy Organic",
                "sizes": [{"size": "per kg", "price": 8.50, "price_per_unit": "8.50 per kg"}],
                "attributes": ["vegetarian", "vegan"],
                "organic": True
            }
        ]

        # Test 1: Calculate total
        total = formatter.calculate_total(sample_products)
        self.assert_equal(total, 15.50, "Total price calculation correct")

        # Test 2: Markdown format
        markdown = formatter.format_markdown(sample_products)
        self.assert_true("Red Lentils" in markdown, "Markdown format includes product names")
        self.assert_true("# " in markdown, "Markdown format includes headers")

        # Test 3: JSON format
        json_output = formatter.format_json(sample_products)
        self.assert_true('"name": "Red Lentils"' in json_output, "JSON format includes product data")
        self.assert_true('"total_items": 2' in json_output, "JSON format includes metadata")

        # Test 4: CSV format
        csv_output = formatter.format_csv(sample_products)
        self.assert_true("Red Lentils" in csv_output, "CSV format includes product names")
        self.assert_true("legumes" in csv_output, "CSV format includes categories")

        # Test 5: HTML format
        html_output = formatter.format_html_table(sample_products)
        self.assert_true("<table>" in html_output, "HTML format includes table")
        self.assert_true("Red Lentils" in html_output, "HTML format includes product names")

        # Test 6: Plain text format
        text_output = formatter.format_plain_text(sample_products)
        self.assert_true("Red Lentils" in text_output, "Text format includes product names")
        self.assert_true("☐" in text_output, "Text format includes checkboxes")

        # Test 7: Format as (universal)
        markdown = formatter.format_as(sample_products, "markdown")
        json_out = formatter.format_as(sample_products, "json")
        self.assert_true(len(markdown) > 0, "Universal formatter works for markdown")
        self.assert_true(len(json_out) > 0, "Universal formatter works for json")

        # Test 8: Empty products
        empty_markdown = formatter.format_markdown([])
        self.assert_true("No products" in empty_markdown, "Formatter handles empty products")

        print()

    def test_skill_handler(self):
        """Test skill handler and conversational logic"""
        print("🤖 Testing Skill Handler...\n")

        skill = ShoppingListSkill()

        # Test 1: Parse budget query
        budget = skill.parse_budget_query("under 50 shekels")
        self.assert_true(budget is not None, "Budget parsing works for 'under X'")
        if budget:
            self.assert_equal(budget, (0, 50), "Budget correctly parsed as (0, 50)")

        # Test 2: Parse range budget
        budget = skill.parse_budget_query("100-200 shekels")
        self.assert_true(budget is not None, "Budget parsing works for range")

        # Test 3: Category extraction
        cats = skill.extract_category_request("vegetables and legumes")
        self.assert_true(cats is not None and len(cats) > 0, f"Category extraction works ({len(cats) if cats else 0} found)")

        # Test 4: Generate clarifying questions
        questions = skill.generate_clarifying_questions("lentils")
        self.assert_greater(len(questions), 0, f"Clarifying questions generated ({len(questions)} questions)")

        # Test 5: Process simple query
        result = skill.process_query("lentils")
        self.assert_true(len(result['products']) > 0, f"Query processing returns products ({len(result['products'])} found)")
        self.assert_true('list_markdown' in result, "Result includes markdown format")

        # Test 6: Process budget query
        result = skill.process_query("chickpeas under 10")
        self.assert_true(len(result['products']) > 0, "Budget query returns results")

        # Test 7: Process diet query
        result = skill.process_query("organic vegetables")
        self.assert_true(len(result['products']) > 0, "Diet query returns results")

        # Test 8: Format response (markdown)
        response = skill.format_response("lentils", "markdown")
        self.assert_true(len(response) > 0, "Markdown response generated")
        self.assert_true("₪" in response or "shekels" in response.lower(), "Response includes prices")

        # Test 9: Format response (json)
        response = skill.format_response("lentils", "json")
        self.assert_true('"name"' in response, "JSON response valid")

        # Test 10: Get categories
        categories = skill.get_categories()
        self.assert_greater(len(categories), 0, f"Skill returns categories ({len(categories)} categories)")

        # Test 11: Get product details
        product = skill.get_product_details("prod_001")
        self.assert_true(product is not None, "Product details retrieval works")
        if product:
            self.assert_equal(product['name'], "Red Lentils", "Correct product retrieved")

        # Test 12: Build custom list
        custom_list = skill.build_custom_list(["prod_001", "prod_002"])
        self.assert_true(len(custom_list['products']) > 0, "Custom list building works")

        # Test 13: Session state
        skill.session_state['preferences'] = {'diet': 'vegan'}
        self.assert_true('preferences' in skill.session_state, "Session state tracking works")

        # Test 14: No results handling
        result = skill.process_query("xyz12345nonexistent")
        self.assert_true('clarifying_questions' in result, "Empty results generate clarifying questions")

        # Test 15: Format consistency
        result1 = skill.format_response("vegetables", "markdown")
        result2 = skill.format_response("vegetables", "csv")
        result3 = skill.format_response("vegetables", "json")
        self.assert_true(len(result1) > 0 and len(result2) > 0 and len(result3) > 0, "All formats work consistently")

        print()

    def test_cart_management(self):
        """Test new cart management features"""
        print("🛒 Testing Cart Management (NEW)...\n")

        skill = ShoppingListSkill()

        # Test 1: Add item to cart
        result = skill.add_item_to_cart("prod_001", quantity=1)
        self.assert_true(result['success'], "Item added to cart successfully")
        self.assert_equal(result['verified'], True, "Item marked as verified")
        self.assert_true(result['cart_total'] > 0, "Cart total updated")

        # Test 2: Verify item in cart
        verification = skill.verify_item_in_cart("prod_001")
        self.assert_true(verification['verified'], "Item verification works")
        self.assert_equal(verification['product_id'], "prod_001", "Correct product verified")

        # Test 3: Get cart summary
        summary = skill.get_cart_summary()
        self.assert_true(len(summary['items']) > 0, "Cart summary includes items")
        self.assert_true('cart_markdown' in summary, "Cart summary includes markdown")
        self.assert_equal(summary['total_items'], 1, "Cart item count correct")

        # Test 4: Add multiple items
        skill.add_item_to_cart("prod_002", quantity=1)
        skill.add_item_to_cart("prod_037", quantity=2)
        summary = skill.get_cart_summary()
        self.assert_equal(summary['total_items'], 3, f"Multiple items tracked")

        # Test 5: Get cart total
        total = skill.get_cart_total()
        self.assert_greater(total, 0, f"Cart total calculated (₪{total:.2f})")

        # Test 6: Verify multiple items
        verification1 = skill.verify_item_in_cart("prod_001")
        verification2 = skill.verify_item_in_cart("prod_002")
        self.assert_true(verification1['verified'] and verification2['verified'], "Multiple items verified")

        # Test 7: Remove item from cart
        result = skill.remove_item_from_cart("prod_001")
        self.assert_true(result['success'], "Item removed successfully")
        self.assert_equal(result['cart_items'], 2, "Cart count updated after removal")

        # Test 8: Verify removed item is gone
        verification = skill.verify_item_in_cart("prod_001")
        self.assert_true(not verification['verified'], "Removed item no longer in cart")

        # Test 9: Remove non-existent item
        result = skill.remove_item_from_cart("prod_999")
        self.assert_true(not result['success'], "Removing non-existent item fails gracefully")

        # Test 10: Add item to empty cart
        skill_new = ShoppingListSkill()
        result = skill_new.add_item_to_cart("prod_005")
        self.assert_true(result['success'], "Can add item to empty cart")
        self.assert_true(skill_new.get_cart_total() > 0, "Empty cart initializes properly")

        # Test 11: Cart state tracking
        self.assert_equal(len(skill.current_list), 2, "Current list tracks added items")

        # Test 12: All items verified flag
        summary = skill.get_cart_summary()
        self.assert_true(summary['all_verified'], "All items in cart are verified")

        print()


def main():
    """Run full test suite"""
    suite = TestSuite()
    success = suite.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
