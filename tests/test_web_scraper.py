"""
Test Suite for Web Scraper - Product Search & Extraction Module
Tests product search and data extraction from Rami Levy website using Playwright + BeautifulSoup
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import web_scraper
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestWebScraper:
    """Test suite for WebScraper class"""

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
            return False

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
            return False

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
            return False

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
            return False

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
            return False

    def run_all_tests(self):
        """Run all test methods"""
        print("\n" + "=" * 70)
        print("🧪 Web Scraper Test Suite")
        print("=" * 70)

        self.test_web_scraper_import()
        self.test_web_scraper_initialization()
        self.test_search_product_with_none_page()
        self.test_search_product_returns_dict()
        self.test_search_product_dict_has_required_keys()
        self.test_get_product_details_with_none_page()
        self.test_get_product_details_returns_dict()
        self.test_get_product_details_dict_has_required_keys()
        self.test_is_product_available_with_none_page()
        self.test_is_product_available_returns_bool()
        self.test_search_product_not_found_returns_found_false()
        self.test_search_product_found_has_price()

        print("\n" + "=" * 70)
        print(f"Test Results: {self.passed} passed, {self.failed} failed (Total: {self.tests_run})")
        print("=" * 70)

        return self.failed == 0

    def test_web_scraper_import(self):
        """Test that WebScraper class can be imported"""
        print("\n1️⃣ Testing WebScraper import...")
        try:
            from web_scraper import WebScraper
            self.assert_true(True, "WebScraper class imported successfully")
        except ImportError as e:
            self.assert_true(False, f"Failed to import WebScraper: {e}")

    def test_web_scraper_initialization(self):
        """Test that WebScraper can be instantiated"""
        print("\n2️⃣ Testing WebScraper initialization...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()
            self.assert_true(scraper is not None, "WebScraper instance created")
        except Exception as e:
            self.assert_true(False, f"Failed to initialize WebScraper: {e}")

    def test_search_product_with_none_page(self):
        """Test search_product returns mock data when page is None"""
        print("\n3️⃣ Testing search_product with page=None (mock data)...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()
            result = scraper.search_product(None, "tomato")

            self.assert_is_dict(result, "search_product returns a dict when page=None")
            self.assert_equal(result.get("found"), True,
                            "search_product with page=None returns found=True")

        except Exception as e:
            self.assert_true(False, f"Error testing search_product: {e}")

    def test_search_product_returns_dict(self):
        """Test search_product returns dictionary"""
        print("\n4️⃣ Testing search_product returns dict...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            # Create mock page
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.content = MagicMock(return_value="<html><body></body></html>")

            result = scraper.search_product(mock_page, "tomato")
            self.assert_is_dict(result, "search_product returns a dictionary")

        except Exception as e:
            self.assert_true(False, f"Error testing search_product: {e}")

    def test_search_product_dict_has_required_keys(self):
        """Test search_product dict has required keys"""
        print("\n5️⃣ Testing search_product dict structure...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            result = scraper.search_product(None, "test")

            required_keys = ["found", "url", "name", "price", "error"]
            for key in required_keys:
                self.assert_in(key, result,
                              f"search_product result has '{key}' key")

        except Exception as e:
            self.assert_true(False, f"Error testing dict structure: {e}")

    def test_get_product_details_with_none_page(self):
        """Test get_product_details returns mock data when page is None"""
        print("\n6️⃣ Testing get_product_details with page=None (mock data)...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            result = scraper.get_product_details(None, "http://example.com/product")
            self.assert_is_dict(result, "get_product_details returns dict when page=None")

        except Exception as e:
            self.assert_true(False, f"Error testing get_product_details: {e}")

    def test_get_product_details_returns_dict(self):
        """Test get_product_details returns dictionary"""
        print("\n7️⃣ Testing get_product_details returns dict...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            # Create mock page
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.content = MagicMock(return_value="<html><body></body></html>")

            result = scraper.get_product_details(mock_page, "http://example.com/product")
            self.assert_is_dict(result, "get_product_details returns a dictionary")

        except Exception as e:
            self.assert_true(False, f"Error testing get_product_details: {e}")

    def test_get_product_details_dict_has_required_keys(self):
        """Test get_product_details dict has required keys"""
        print("\n8️⃣ Testing get_product_details dict structure...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            result = scraper.get_product_details(None, "http://example.com")

            required_keys = ["price", "availability", "category", "error"]
            for key in required_keys:
                self.assert_in(key, result,
                              f"get_product_details result has '{key}' key")

        except Exception as e:
            self.assert_true(False, f"Error testing details dict structure: {e}")

    def test_is_product_available_with_none_page(self):
        """Test is_product_available with page=None"""
        print("\n9️⃣ Testing is_product_available with page=None...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            result = scraper.is_product_available(None, "http://example.com/product")
            self.assert_is_bool(result, "is_product_available returns boolean when page=None")

        except Exception as e:
            self.assert_true(False, f"Error testing is_product_available: {e}")

    def test_is_product_available_returns_bool(self):
        """Test is_product_available returns boolean"""
        print("\n🔟 Testing is_product_available returns bool...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            # Create mock page
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.content = MagicMock(return_value="<html><body></body></html>")

            result = scraper.is_product_available(mock_page, "http://example.com/product")
            self.assert_is_bool(result, "is_product_available returns a boolean")

        except Exception as e:
            self.assert_true(False, f"Error testing is_product_available return type: {e}")

    def test_search_product_not_found_returns_found_false(self):
        """Test search_product with empty HTML returns found=False"""
        print("\n1️⃣1️⃣ Testing search_product not found case...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            # Create mock page with empty HTML
            mock_page = MagicMock()
            mock_page.goto = MagicMock()
            mock_page.content = MagicMock(return_value="<html><body></body></html>")

            result = scraper.search_product(mock_page, "nonexistent")
            self.assert_false(result.get("found"),
                            "search_product with no results returns found=False")

        except Exception as e:
            self.assert_true(False, f"Error testing not found case: {e}")

    def test_search_product_found_has_price(self):
        """Test search_product when found returns numeric price"""
        print("\n1️⃣2️⃣ Testing search_product found case has price...")
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()

            # Mock data case (page=None) should have a price
            result = scraper.search_product(None, "test")

            if result.get("found"):
                self.assert_is_float(result.get("price"),
                                   "search_product found result has numeric price")
            else:
                # If not found, price should be 0 or missing
                price = result.get("price")
                self.assert_true(price is None or isinstance(price, (int, float)),
                               "search_product not found result has no price or 0")

        except Exception as e:
            self.assert_true(False, f"Error testing found price: {e}")


def run_tests():
    """Main test runner"""
    suite = TestWebScraper()
    success = suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(run_tests())
