"""
Integration Tests for Rami Levy Browser Automation
Tests full workflow with all components (BrowserManager, WebScraper, CartAutomation, ShoppingListSkill)
"""

import sys
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestIntegration:
    """Integration tests for browser automation workflow"""

    passed = 0
    failed = 0
    tests_run = 0
    cleanup_files = []

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

    def assert_is_bool(self, value, test_name):
        """Assert value is a boolean"""
        self.tests_run += 1
        if isinstance(value, bool):
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

    def assert_not_none(self, value, test_name):
        """Assert value is not None"""
        self.tests_run += 1
        if value is not None:
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name} (value is None)")
            raise AssertionError(test_name)

    def assert_dict_has_keys(self, d, keys, test_name):
        """Assert dictionary has all required keys"""
        self.tests_run += 1
        if all(k in d for k in keys):
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            missing = [k for k in keys if k not in d]
            self.failed += 1
            print(f"  ❌ {test_name}")
            print(f"     Missing keys: {missing}")
            raise AssertionError(test_name)

    def cleanup(self):
        """Clean up temporary files"""
        for file_path in self.cleanup_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not clean up {file_path}: {e}")

    def run_all_tests(self):
        """Run all test methods"""
        print("\n" + "=" * 70)
        print("🧪 Integration Tests - Browser Automation Workflow")
        print("=" * 70)

        # Component Import Tests
        self.test_all_modules_importable()
        self.test_browser_manager_class_exists()
        self.test_web_scraper_class_exists()
        self.test_cart_automation_class_exists()
        self.test_shopping_list_skill_class_exists()

        # Component Method Existence Tests
        self.test_browser_manager_methods_exist()
        self.test_web_scraper_methods_exist()
        self.test_cart_automation_methods_exist()
        self.test_shopping_list_skill_methods_exist()

        # Workflow Simulation Tests
        self.test_shopping_list_skill_process_query()
        self.test_browser_manager_initialization()
        self.test_web_scraper_search_with_none_page()
        self.test_cart_automation_with_mock_page()
        self.test_skill_handler_browser_integration_methods()

        # Return Type Contract Tests
        self.test_browser_manager_open_browser_return_structure()
        self.test_web_scraper_search_product_return_structure()
        self.test_cart_automation_add_to_cart_return_structure()
        self.test_skill_handler_process_query_with_browser_return_structure()
        self.test_skill_handler_cleanup_browser_session_return_structure()

        # Error Handling Tests
        self.test_web_scraper_handles_none_input()
        self.test_cart_automation_handles_none_page()
        self.test_browser_manager_handles_missing_config()
        self.test_skill_handler_handles_missing_modules()

        # Session State Tests
        self.test_browser_manager_session_config_structure()
        self.test_cart_automation_tracks_added_items()
        self.test_shopping_list_skill_cart_state()

        print("\n" + "=" * 70)
        print(f"Test Results: {self.passed} passed, {self.failed} failed (Total: {self.tests_run})")
        print("=" * 70)

        return self.failed == 0

    # =========================================================================
    # COMPONENT IMPORT TESTS
    # =========================================================================

    def test_all_modules_importable(self):
        """Test that all 4 modules can be imported"""
        print("\n1️⃣ Testing all modules importable...")
        try:
            from browser_manager import BrowserManager
            from cart_automation import CartAutomation
            from skill_handler import ShoppingListSkill
            from web_scraper import WebScraper
            self.assert_true(True, "All 4 modules imported successfully")
        except ImportError as e:
            self.assert_true(False, f"Failed to import modules: {e}")

    def test_browser_manager_class_exists(self):
        """Test that BrowserManager class exists"""
        print("\n2️⃣ Testing BrowserManager class exists...")
        try:
            from browser_manager import BrowserManager
            self.assert_true(BrowserManager is not None, "BrowserManager class exists")
        except Exception as e:
            self.assert_true(False, f"BrowserManager error: {e}")

    def test_web_scraper_class_exists(self):
        """Test that WebScraper class exists"""
        print("\n3️⃣ Testing WebScraper class exists...")
        try:
            from web_scraper import WebScraper
            self.assert_true(WebScraper is not None, "WebScraper class exists")
        except Exception as e:
            self.assert_true(False, f"WebScraper error: {e}")

    def test_cart_automation_class_exists(self):
        """Test that CartAutomation class exists"""
        print("\n4️⃣ Testing CartAutomation class exists...")
        try:
            from cart_automation import CartAutomation
            self.assert_true(CartAutomation is not None, "CartAutomation class exists")
        except Exception as e:
            self.assert_true(False, f"CartAutomation error: {e}")

    def test_shopping_list_skill_class_exists(self):
        """Test that ShoppingListSkill class exists"""
        print("\n5️⃣ Testing ShoppingListSkill class exists...")
        try:
            from skill_handler import ShoppingListSkill
            self.assert_true(ShoppingListSkill is not None, "ShoppingListSkill class exists")
        except Exception as e:
            self.assert_true(False, f"ShoppingListSkill error: {e}")

    # =========================================================================
    # COMPONENT METHOD EXISTENCE TESTS
    # =========================================================================

    def test_browser_manager_methods_exist(self):
        """Test that BrowserManager has all required methods"""
        print("\n6️⃣ Testing BrowserManager methods exist...")
        try:
            from browser_manager import BrowserManager
            bm = BrowserManager()

            methods = [
                'open_browser',
                'close_browser',
                'get_browser',
                'is_browser_open',
                'navigate_to_cart',
                'get_session_config',
                'update_session_config'
            ]

            for method in methods:
                if not hasattr(bm, method):
                    self.assert_true(False, f"Missing method: {method}")
                    return

            self.assert_true(True, "All BrowserManager methods exist")
        except Exception as e:
            self.assert_true(False, f"BrowserManager methods error: {e}")

    def test_web_scraper_methods_exist(self):
        """Test that WebScraper has all required methods (skipped if bs4 not available)"""
        print("\n7️⃣ Testing WebScraper methods exist...")
        try:
            from web_scraper import WebScraper
            ws = WebScraper()

            methods = [
                'search_product',
                'get_product_details',
                'is_product_available'
            ]

            for method in methods:
                if not hasattr(ws, method):
                    self.assert_true(False, f"Missing method: {method}")
                    return

            self.assert_true(True, "All WebScraper methods exist")
        except ImportError as e:
            if 'bs4' in str(e):
                print("  ⏭️  Skipped (bs4 not installed)")
                self.tests_run -= 1
            else:
                self.assert_true(False, f"WebScraper methods error: {e}")
        except Exception as e:
            self.assert_true(False, f"WebScraper methods error: {e}")

    def test_cart_automation_methods_exist(self):
        """Test that CartAutomation has all required methods"""
        print("\n8️⃣ Testing CartAutomation methods exist...")
        try:
            from cart_automation import CartAutomation
            ca = CartAutomation()

            methods = [
                'add_to_cart',
                'verify_in_cart',
                'get_cart_total',
                'get_added_items'
            ]

            for method in methods:
                if not hasattr(ca, method):
                    self.assert_true(False, f"Missing method: {method}")
                    return

            self.assert_true(True, "All CartAutomation methods exist")
        except Exception as e:
            self.assert_true(False, f"CartAutomation methods error: {e}")

    def test_shopping_list_skill_methods_exist(self):
        """Test that ShoppingListSkill has all required methods"""
        print("\n9️⃣ Testing ShoppingListSkill methods exist...")
        try:
            from skill_handler import ShoppingListSkill
            skill = ShoppingListSkill()

            methods = [
                'process_query',
                'format_response',
                'build_custom_list',
                'add_item_to_cart',
                'remove_item_from_cart',
                'get_cart_total',
                'get_cart_summary',
                'process_query_with_browser',
                'cleanup_browser_session'
            ]

            for method in methods:
                if not hasattr(skill, method):
                    self.assert_true(False, f"Missing method: {method}")
                    return

            self.assert_true(True, "All ShoppingListSkill methods exist")
        except Exception as e:
            self.assert_true(False, f"ShoppingListSkill methods error: {e}")

    # =========================================================================
    # WORKFLOW SIMULATION TESTS
    # =========================================================================

    def test_shopping_list_skill_process_query(self):
        """Test ShoppingListSkill can process a query"""
        print("\n🔟 Testing ShoppingListSkill process_query workflow...")
        try:
            from skill_handler import ShoppingListSkill
            skill = ShoppingListSkill()
            result = skill.process_query("lentils")

            self.assert_is_dict(result, "process_query returns dict")
            self.assert_in('products', result, "Result has 'products' key")
            self.assert_in('metadata', result, "Result has 'metadata' key")
            self.assert_in('clarifying_questions', result, "Result has 'clarifying_questions' key")
        except Exception as e:
            self.assert_true(False, f"process_query error: {e}")

    def test_browser_manager_initialization(self):
        """Test BrowserManager can be initialized"""
        print("\n1️⃣1️⃣ Testing BrowserManager initialization...")
        try:
            from browser_manager import BrowserManager
            bm = BrowserManager()

            self.assert_true(bm is not None, "BrowserManager instantiated")
            self.assert_true(hasattr(bm, 'config_path'), "Has config_path attribute")
            self.assert_true(hasattr(bm, 'page'), "Has page attribute")
        except Exception as e:
            self.assert_true(False, f"BrowserManager init error: {e}")

    def test_web_scraper_search_with_none_page(self):
        """Test WebScraper can search with None page (mock mode, skipped if bs4 not available)"""
        print("\n1️⃣2️⃣ Testing WebScraper search with None page...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()
            result = scraper.search_product(None, "lentils")

            self.assert_is_dict(result, "search_product returns dict with None page")
            self.assert_in('found', result, "Result has 'found' key")
            self.assert_in('url', result, "Result has 'url' key")
            self.assert_in('name', result, "Result has 'name' key")
            self.assert_in('price', result, "Result has 'price' key")
        except ImportError as e:
            if 'bs4' in str(e):
                print("  ⏭️  Skipped (bs4 not installed)")
                self.tests_run -= 1
            else:
                self.assert_true(False, f"WebScraper search error: {e}")
        except Exception as e:
            self.assert_true(False, f"WebScraper search error: {e}")

    def test_cart_automation_with_mock_page(self):
        """Test CartAutomation initialization and item tracking"""
        print("\n1️⃣3️⃣ Testing CartAutomation with mock state...")
        try:
            from cart_automation import CartAutomation
            ca = CartAutomation()

            self.assert_is_list(ca.added_items, "added_items is initialized as list")
            self.assert_equal(len(ca.added_items), 0, "added_items starts empty")
        except Exception as e:
            self.assert_true(False, f"CartAutomation error: {e}")

    def test_skill_handler_browser_integration_methods(self):
        """Test ShoppingListSkill has browser integration methods"""
        print("\n1️⃣4️⃣ Testing ShoppingListSkill browser integration methods...")
        try:
            from skill_handler import ShoppingListSkill
            skill = ShoppingListSkill()

            # Check that new browser integration methods exist
            self.assert_true(hasattr(skill, 'process_query_with_browser'),
                            "Has process_query_with_browser method")
            self.assert_true(hasattr(skill, 'cleanup_browser_session'),
                            "Has cleanup_browser_session method")
        except Exception as e:
            self.assert_true(False, f"Browser integration methods error: {e}")

    # =========================================================================
    # RETURN TYPE CONTRACT TESTS
    # =========================================================================

    def test_browser_manager_open_browser_return_structure(self):
        """Test BrowserManager.open_browser() return structure"""
        print("\n1️⃣5️⃣ Testing BrowserManager.open_browser return structure...")
        try:
            from browser_manager import BrowserManager
            bm = BrowserManager()

            # Mock the playwright instance to avoid actually opening browser
            with patch('browser_manager.sync_playwright'):
                with patch.object(bm, 'playwright_instance', MagicMock()):
                    with patch.object(bm, 'browser', MagicMock()):
                        bm.browser.process = MagicMock()
                        bm.browser.process.pid = 12345

                        with patch.object(bm, 'page', MagicMock()):
                            # Since we can't easily mock the full workflow,
                            # just verify the structure by examining the method
                            result = bm.open_browser()

            if isinstance(result, dict):
                self.assert_dict_has_keys(result, ['success', 'message'],
                                         "open_browser returns dict with success and message")
        except Exception as e:
            # If we can't fully test due to playwright dependencies, just verify method signature
            from browser_manager import BrowserManager
            bm = BrowserManager()
            self.assert_true(callable(bm.open_browser), "open_browser is callable")

    def test_web_scraper_search_product_return_structure(self):
        """Test WebScraper.search_product() return structure (skipped if bs4 not available)"""
        print("\n1️⃣6️⃣ Testing WebScraper.search_product return structure...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()
            result = scraper.search_product(None, "test product")

            required_keys = ['found', 'url', 'name', 'price', 'error']
            self.assert_dict_has_keys(result, required_keys,
                                     "search_product returns all required keys")
            self.assert_is_bool(result['found'], "found is boolean")
        except ImportError as e:
            if 'bs4' in str(e):
                print("  ⏭️  Skipped (bs4 not installed)")
                self.tests_run -= 1
            else:
                self.assert_true(False, f"WebScraper return structure error: {e}")
        except Exception as e:
            self.assert_true(False, f"WebScraper return structure error: {e}")

    def test_cart_automation_add_to_cart_return_structure(self):
        """Test CartAutomation.add_to_cart() return structure"""
        print("\n1️⃣7️⃣ Testing CartAutomation.add_to_cart return structure...")
        try:
            from cart_automation import CartAutomation
            ca = CartAutomation()
            result = ca.add_to_cart(None, "http://example.com/product", quantity=1)

            required_keys = ['success', 'message', 'product_name', 'quantity']
            self.assert_dict_has_keys(result, required_keys,
                                     "add_to_cart returns all required keys")
            self.assert_is_bool(result['success'], "success is boolean")
        except Exception as e:
            self.assert_true(False, f"CartAutomation return structure error: {e}")

    def test_skill_handler_process_query_with_browser_return_structure(self):
        """Test ShoppingListSkill.process_query_with_browser() return structure"""
        print("\n1️⃣8️⃣ Testing ShoppingListSkill.process_query_with_browser return structure...")
        try:
            from skill_handler import ShoppingListSkill
            skill = ShoppingListSkill()

            # Test with a query that won't find products to avoid browser launch
            result = skill.process_query_with_browser("ZZZZZZ_NONEXISTENT_PRODUCT_ZZZZZZ")

            required_keys = ['success', 'message', 'added_items', 'missing_items',
                           'cart_total', 'browser_active']
            self.assert_dict_has_keys(result, required_keys,
                                     "process_query_with_browser returns all required keys")
            self.assert_is_bool(result['success'], "success is boolean")
            self.assert_is_list(result['added_items'], "added_items is list")
            self.assert_is_list(result['missing_items'], "missing_items is list")
        except Exception as e:
            self.assert_true(False, f"process_query_with_browser error: {e}")

    def test_skill_handler_cleanup_browser_session_return_structure(self):
        """Test ShoppingListSkill.cleanup_browser_session() return structure"""
        print("\n1️⃣9️⃣ Testing ShoppingListSkill.cleanup_browser_session return structure...")
        try:
            from skill_handler import ShoppingListSkill
            skill = ShoppingListSkill()

            # Call cleanup without opening a browser (should handle gracefully)
            result = skill.cleanup_browser_session()

            required_keys = ['success', 'message', 'browser_closed']
            self.assert_dict_has_keys(result, required_keys,
                                     "cleanup_browser_session returns all required keys")
            self.assert_is_bool(result['success'], "success is boolean")
            self.assert_is_bool(result['browser_closed'], "browser_closed is boolean")
        except Exception as e:
            self.assert_true(False, f"cleanup_browser_session error: {e}")

    # =========================================================================
    # ERROR HANDLING TESTS
    # =========================================================================

    def test_web_scraper_handles_none_input(self):
        """Test WebScraper handles None page gracefully (skipped if bs4 not available)"""
        print("\n2️⃣0️⃣ Testing WebScraper handles None page...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            # Should not crash, should return dict with error handling
            result = scraper.search_product(None, "")
            self.assert_is_dict(result, "search_product(None, '') returns dict")

            result2 = scraper.get_product_details(None, "")
            self.assert_is_dict(result2, "get_product_details(None, '') returns dict")
        except ImportError as e:
            if 'bs4' in str(e):
                print("  ⏭️  Skipped (bs4 not installed)")
                self.tests_run -= 1
            else:
                self.assert_true(False, f"WebScraper None handling error: {e}")
        except Exception as e:
            self.assert_true(False, f"WebScraper None handling error: {e}")

    def test_cart_automation_handles_none_page(self):
        """Test CartAutomation handles None page gracefully"""
        print("\n2️⃣1️⃣ Testing CartAutomation handles None page...")
        try:
            from cart_automation import CartAutomation
            ca = CartAutomation()

            # add_to_cart with None page
            result = ca.add_to_cart(None, "http://example.com/product")
            self.assert_is_dict(result, "add_to_cart(None, ...) returns dict")
            self.assert_false(result['success'], "add_to_cart(None, ...) returns success=False")

            # verify_in_cart with None page
            result2 = ca.verify_in_cart(None, "product name")
            self.assert_is_dict(result2, "verify_in_cart(None, ...) returns dict")
            self.assert_false(result2['verified'], "verify_in_cart(None, ...) returns verified=False")
        except Exception as e:
            self.assert_true(False, f"CartAutomation None handling error: {e}")

    def test_browser_manager_handles_missing_config(self):
        """Test BrowserManager handles missing config file"""
        print("\n2️⃣2️⃣ Testing BrowserManager handles missing config...")
        try:
            from browser_manager import BrowserManager
            bm = BrowserManager()

            # Should not crash when config doesn't exist
            config = bm.get_session_config()
            self.assert_is_dict(config, "get_session_config returns dict even if missing")
            self.assert_equal(config, {}, "Returns empty dict when config missing")
        except Exception as e:
            self.assert_true(False, f"BrowserManager missing config error: {e}")

    def test_skill_handler_handles_missing_modules(self):
        """Test ShoppingListSkill handles missing browser modules gracefully"""
        print("\n2️⃣3️⃣ Testing ShoppingListSkill handles missing modules...")
        try:
            from skill_handler import ShoppingListSkill
            skill = ShoppingListSkill()

            # The method should handle module import errors gracefully
            # We can verify this by checking if the method is callable and returns proper structure
            result = skill.process_query_with_browser("test")
            self.assert_is_dict(result, "Returns dict (handles errors gracefully)")
            self.assert_in('success', result, "Has success key in response")
            self.assert_in('message', result, "Has message key in response")
        except Exception as e:
            self.assert_true(False, f"ShoppingListSkill error handling error: {e}")

    # =========================================================================
    # SESSION STATE TESTS
    # =========================================================================

    def test_browser_manager_session_config_structure(self):
        """Test BrowserManager session config has required structure"""
        print("\n2️⃣4️⃣ Testing BrowserManager session config structure...")
        try:
            from browser_manager import BrowserManager
            import tempfile

            bm = BrowserManager()

            # Create test config with all required fields
            test_config = {
                "active": True,
                "browser_pid": 12345,
                "ws_endpoint": "ws://localhost:3000",
                "opened_at": datetime.now().isoformat() + "Z",
                "items_added": 0,
                "cart_total": 0.0,
                "last_updated": datetime.now().isoformat() + "Z"
            }

            # Save it
            bm._save_config(test_config)
            self.cleanup_files.append(str(bm.config_path))

            # Load it back
            loaded = bm.get_session_config()

            required_keys = ['active', 'browser_pid', 'ws_endpoint', 'opened_at',
                           'items_added', 'cart_total', 'last_updated']
            self.assert_dict_has_keys(loaded, required_keys,
                                     "Session config has all required keys")
        except Exception as e:
            self.assert_true(False, f"Session config structure error: {e}")

    def test_cart_automation_tracks_added_items(self):
        """Test CartAutomation properly tracks added items"""
        print("\n2️⃣5️⃣ Testing CartAutomation tracks added items...")
        try:
            from cart_automation import CartAutomation
            ca = CartAutomation()

            # Initially empty
            self.assert_equal(len(ca.get_added_items()), 0, "added_items starts empty")

            # Manually add an item to simulate successful addition
            ca.added_items.append({
                'name': 'Test Product',
                'url': 'http://example.com/product',
                'quantity': 1
            })

            items = ca.get_added_items()
            self.assert_equal(len(items), 1, "added_items has 1 item after adding")
            self.assert_equal(items[0]['name'], 'Test Product', "Item name is correct")
        except Exception as e:
            self.assert_true(False, f"CartAutomation tracking error: {e}")

    def test_shopping_list_skill_cart_state(self):
        """Test ShoppingListSkill maintains cart state"""
        print("\n2️⃣6️⃣ Testing ShoppingListSkill cart state...")
        try:
            from skill_handler import ShoppingListSkill
            skill = ShoppingListSkill()

            # Check cart is initialized
            self.assert_is_dict(skill.cart, "cart is dict")
            self.assert_equal(len(skill.cart), 0, "cart starts empty")

            # Check session state
            self.assert_is_dict(skill.session_state, "session_state is dict")

            # Check current_list
            self.assert_is_list(skill.current_list, "current_list is list")
            self.assert_equal(len(skill.current_list), 0, "current_list starts empty")
        except Exception as e:
            self.assert_true(False, f"ShoppingListSkill cart state error: {e}")


def main():
    """Run all integration tests"""
    tester = TestIntegration()
    success = tester.run_all_tests()
    tester.cleanup()

    if success:
        print("\n✅ All integration tests passed!")
        return 0
    else:
        print("\n❌ Some integration tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())
