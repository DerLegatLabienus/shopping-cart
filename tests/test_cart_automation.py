"""
Test Suite for Cart Automation - Adding Items to Rami Levy Shopping Cart
Tests CartAutomation class for adding items, verification, and cart totals
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add parent directory to path to import cart_automation
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCartAutomation:
    """Test suite for CartAutomation class"""

    passed = 0
    failed = 0
    tests_run = 0

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
            raise AssertionError(test_name)

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
            raise AssertionError(test_name)

    def assert_false(self, condition, test_name):
        """Assert condition is false"""
        self.tests_run += 1
        if not condition:
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}")
            raise AssertionError(test_name)

    def assert_is_dict(self, value, test_name):
        """Assert value is a dictionary"""
        self.tests_run += 1
        if isinstance(value, dict):
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name} (got {type(value).__name__})")
            raise AssertionError(test_name)

    def assert_is_float(self, value, test_name):
        """Assert value is a float or int"""
        self.tests_run += 1
        if isinstance(value, (float, int)):
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name} (got {type(value).__name__})")
            raise AssertionError(test_name)

    def assert_is_list(self, value, test_name):
        """Assert value is a list"""
        self.tests_run += 1
        if isinstance(value, list):
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name} (got {type(value).__name__})")
            raise AssertionError(test_name)

    def assert_in(self, item, container, test_name):
        """Assert item is in container"""
        self.tests_run += 1
        if item in container:
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}")
            print(f"     '{item}' not found in {container}")
            raise AssertionError(test_name)

    def run_all_tests(self):
        """Run all test methods"""
        print("\n" + "=" * 70)
        print("🧪 Cart Automation Test Suite")
        print("=" * 70)

        self.test_cart_automation_import()
        self.test_cart_automation_initialization()
        self.test_add_to_cart_returns_dict()
        self.test_add_to_cart_with_none_page()
        self.test_add_to_cart_dict_has_required_keys()
        self.test_add_to_cart_success_path()
        self.test_add_to_cart_with_quantity()
        self.test_verify_in_cart_returns_dict()
        self.test_verify_in_cart_with_none_page()
        self.test_verify_in_cart_dict_has_required_keys()
        self.test_get_cart_total_returns_float()
        self.test_get_cart_total_with_none_page()
        self.test_get_cart_total_with_price_symbols()
        self.test_get_added_items_returns_list()
        self.test_get_added_items_initialization()
        self.test_add_to_cart_tracks_items()
        self.test_add_to_cart_invalid_url()
        self.test_add_to_cart_missing_add_button()

        print("\n" + "=" * 70)
        print(f"Test Results: {self.passed} passed, {self.failed} failed (Total: {self.tests_run})")
        print("=" * 70)

        return self.failed == 0

    def test_cart_automation_import(self):
        """Test that CartAutomation class can be imported"""
        print("\n1️⃣ Testing CartAutomation import...")
        try:
            from cart_automation import CartAutomation
            self.assert_true(True, "CartAutomation class imported successfully")
        except ImportError as e:
            self.assert_true(False, f"Failed to import CartAutomation: {e}")

    def test_cart_automation_initialization(self):
        """Test that CartAutomation can be instantiated"""
        print("\n2️⃣ Testing CartAutomation initialization...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()
            self.assert_true(automation is not None, "CartAutomation instance created")
        except Exception as e:
            self.assert_true(False, f"Failed to initialize CartAutomation: {e}")

    def test_add_to_cart_returns_dict(self):
        """Test that add_to_cart returns a dictionary"""
        print("\n3️⃣ Testing add_to_cart returns dict...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.query_selector = MagicMock(return_value=None)
            mock_page.wait_for_load_state = MagicMock()

            result = automation.add_to_cart(mock_page, "http://example.com/product")
            self.assert_is_dict(result, "add_to_cart returns a dictionary")
        except Exception as e:
            self.assert_true(False, f"Error testing add_to_cart: {e}")

    def test_add_to_cart_with_none_page(self):
        """Test add_to_cart with page=None returns complete dict"""
        print("\n4️⃣ Testing add_to_cart with page=None...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            result = automation.add_to_cart(None, "http://example.com/product")

            self.assert_is_dict(result, "add_to_cart with page=None returns a dict")
            self.assert_equal(result.get("success"), False, "success key is False")
            self.assert_in("message", result, "result has 'message' key")
            self.assert_in("product_name", result, "result has 'product_name' key")
            self.assert_in("quantity", result, "result has 'quantity' key")
        except Exception as e:
            self.assert_true(False, f"Error testing add_to_cart with None: {e}")

    def test_add_to_cart_dict_has_required_keys(self):
        """Test add_to_cart dict has required keys"""
        print("\n5️⃣ Testing add_to_cart dict structure...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.query_selector = MagicMock(return_value=None)
            mock_page.wait_for_load_state = MagicMock()

            result = automation.add_to_cart(mock_page, "http://example.com/product")

            required_keys = ["success", "message", "product_name", "quantity"]
            for key in required_keys:
                self.assert_in(key, result, f"add_to_cart result has '{key}' key")
        except Exception as e:
            self.assert_true(False, f"Error testing dict structure: {e}")

    def test_add_to_cart_success_path(self):
        """Test add_to_cart success path with mocked element"""
        print("\n6️⃣ Testing add_to_cart success path...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page with successful element
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.wait_for_load_state = MagicMock()

            # Mock the data-productname attribute
            mock_element = MagicMock()
            mock_element.get_attribute = MagicMock(return_value="Test Product")

            # Mock query_selector to return the element for product name, then None for button
            mock_page.query_selector = MagicMock(return_value=mock_element)

            # Mock the add to cart button
            mock_button = MagicMock()
            mock_button.click = MagicMock()
            mock_page.query_selector = MagicMock(side_effect=[
                mock_element,  # First call for product name
                mock_button,   # Second call for add to cart button
            ])

            result = automation.add_to_cart(mock_page, "http://example.com/product", quantity=1)

            self.assert_equal(result.get("success"), True, "success key is True")
            self.assert_equal(result.get("product_name"), "Test Product", "product_name is extracted")
            self.assert_equal(result.get("quantity"), 1, "quantity is set correctly")
        except Exception as e:
            self.assert_true(False, f"Error testing add_to_cart success: {e}")

    def test_add_to_cart_with_quantity(self):
        """Test add_to_cart with specific quantity"""
        print("\n7️⃣ Testing add_to_cart with quantity > 1...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.wait_for_load_state = MagicMock()

            mock_element = MagicMock()
            mock_element.get_attribute = MagicMock(return_value="Test Product")

            mock_button = MagicMock()
            mock_button.click = MagicMock()

            # Setup for multiple query_selector calls
            mock_page.query_selector = MagicMock(side_effect=[
                mock_element,  # product name
                None,          # quantity input (not found, so skip)
                mock_button,   # add to cart button
            ])

            result = automation.add_to_cart(mock_page, "http://example.com/product", quantity=3)

            self.assert_equal(result.get("quantity"), 3, "quantity parameter is respected")
        except Exception as e:
            self.assert_true(False, f"Error testing add_to_cart with quantity: {e}")

    def test_verify_in_cart_returns_dict(self):
        """Test that verify_in_cart returns a dictionary"""
        print("\n8️⃣ Testing verify_in_cart returns dict...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.content = MagicMock(return_value="<html></html>")

            result = automation.verify_in_cart(mock_page, "Test Product")
            self.assert_is_dict(result, "verify_in_cart returns a dictionary")
        except Exception as e:
            self.assert_true(False, f"Error testing verify_in_cart: {e}")

    def test_verify_in_cart_with_none_page(self):
        """Test verify_in_cart with page=None returns complete dict"""
        print("\n9️⃣ Testing verify_in_cart with page=None...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            result = automation.verify_in_cart(None, "Test Product")

            self.assert_is_dict(result, "verify_in_cart with page=None returns a dict")
            self.assert_equal(result.get("verified"), False, "verified key is False")
            self.assert_in("quantity", result, "result has 'quantity' key")
            self.assert_in("message", result, "result has 'message' key")
        except Exception as e:
            self.assert_true(False, f"Error testing verify_in_cart with None: {e}")

    def test_verify_in_cart_dict_has_required_keys(self):
        """Test verify_in_cart dict has required keys"""
        print("\n🔟 Testing verify_in_cart dict structure...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            result = automation.verify_in_cart(None, "Test Product")

            required_keys = ["verified", "quantity", "message"]
            for key in required_keys:
                self.assert_in(key, result, f"verify_in_cart result has '{key}' key")
        except Exception as e:
            self.assert_true(False, f"Error testing verify_in_cart dict structure: {e}")

    def test_get_cart_total_returns_float(self):
        """Test that get_cart_total returns a float"""
        print("\n1️⃣1️⃣ Testing get_cart_total returns float...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.content = MagicMock(return_value="<div>₪150.50</div>")
            mock_page.query_selector = MagicMock(return_value=None)

            result = automation.get_cart_total(mock_page)
            self.assert_is_float(result, "get_cart_total returns a float")
        except Exception as e:
            self.assert_true(False, f"Error testing get_cart_total: {e}")

    def test_get_cart_total_with_none_page(self):
        """Test get_cart_total with page=None returns 0.0"""
        print("\n1️⃣2️⃣ Testing get_cart_total with page=None...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            result = automation.get_cart_total(None)
            self.assert_equal(result, 0.0, "get_cart_total with page=None returns 0.0")
        except Exception as e:
            self.assert_true(False, f"Error testing get_cart_total with None: {e}")

    def test_get_cart_total_with_price_symbols(self):
        """Test get_cart_total parses prices with currency symbols correctly"""
        print("\n1️⃣3️⃣ Testing get_cart_total price parsing...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page with price containing shekel symbol
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.content = MagicMock(return_value="<div data-carttotal>₪1,250.99</div>")
            mock_page.query_selector = MagicMock(return_value=None)

            result = automation.get_cart_total(mock_page)
            # Should parse "₪1,250.99" correctly (removes symbol and comma, parses as 1250.99)
            self.assert_true(result >= 1250.0, "get_cart_total parses price with shekel symbol")
        except Exception as e:
            self.assert_true(False, f"Error testing price parsing: {e}")

    def test_get_added_items_returns_list(self):
        """Test that get_added_items returns a list"""
        print("\n1️⃣4️⃣ Testing get_added_items returns list...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            result = automation.get_added_items()
            self.assert_is_list(result, "get_added_items returns a list")
        except Exception as e:
            self.assert_true(False, f"Error testing get_added_items: {e}")

    def test_get_added_items_initialization(self):
        """Test that added_items starts empty"""
        print("\n1️⃣5️⃣ Testing get_added_items initialization...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            result = automation.get_added_items()
            self.assert_equal(result, [], "get_added_items returns empty list initially")
        except Exception as e:
            self.assert_true(False, f"Error testing added_items initialization: {e}")

    def test_add_to_cart_tracks_items(self):
        """Test that add_to_cart adds item to added_items list"""
        print("\n1️⃣6️⃣ Testing add_to_cart tracking...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page with successful add
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.wait_for_load_state = MagicMock()

            mock_element = MagicMock()
            mock_element.get_attribute = MagicMock(return_value="Test Product")

            mock_button = MagicMock()
            mock_button.click = MagicMock()

            # Return element for product name, None for quantity input, then button for add
            mock_page.query_selector = MagicMock(side_effect=[
                mock_element,  # product name [data-productname]
                None,          # quantity input [data-quantity] - not found
                mock_button,   # add to cart button (first selector match)
            ])
            mock_page.wait_for_timeout = MagicMock()

            automation.add_to_cart(mock_page, "http://example.com/product", quantity=2)

            added_items = automation.get_added_items()
            self.assert_equal(len(added_items), 1, "one item added to tracking")
            if len(added_items) > 0:
                self.assert_equal(added_items[0]["name"], "Test Product", "item name is tracked")
                self.assert_equal(added_items[0]["quantity"], 2, "item quantity is tracked")
        except Exception as e:
            self.assert_true(False, f"Error testing add_to_cart tracking: {e}")

    def test_add_to_cart_invalid_url(self):
        """Test add_to_cart with invalid URL"""
        print("\n1️⃣7️⃣ Testing add_to_cart with invalid URL...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page that raises on goto
            mock_page = MagicMock()
            mock_page.goto = MagicMock(side_effect=Exception("Invalid URL"))

            result = automation.add_to_cart(mock_page, "not-a-url")

            self.assert_equal(result.get("success"), False, "returns success=False on invalid URL")
            self.assert_in("message", result, "returns message on error")
        except Exception as e:
            self.assert_true(False, f"Error testing invalid URL: {e}")

    def test_add_to_cart_missing_add_button(self):
        """Test add_to_cart when add button is not found"""
        print("\n1️⃣8️⃣ Testing add_to_cart with missing add button...")
        try:
            from cart_automation import CartAutomation
            automation = CartAutomation()

            # Create mock page where button is never found
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.wait_for_load_state = MagicMock()

            mock_element = MagicMock()
            mock_element.get_attribute = MagicMock(return_value="Test Product")

            # Always return None for query_selector
            mock_page.query_selector = MagicMock(return_value=None)

            result = automation.add_to_cart(mock_page, "http://example.com/product")

            self.assert_equal(result.get("success"), False, "returns success=False when button not found")
            self.assert_in("message", result, "returns message explaining button not found")
        except Exception as e:
            self.assert_true(False, f"Error testing missing button: {e}")


def run_tests():
    """Main test runner"""
    suite = TestCartAutomation()
    success = suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(run_tests())
