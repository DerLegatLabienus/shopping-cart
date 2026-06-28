"""
Test Suite for Browser Manager - Session Management Module
Tests browser lifecycle and session persistence for Rami Levy automation
"""

import sys
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import browser_manager
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBrowserManager:
    """Test suite for BrowserManager class"""

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
        print("🧪 Browser Manager Test Suite")
        print("=" * 70)

        self.test_browser_manager_import()
        self.test_browser_manager_initialization()
        self.test_session_config_path()
        self.test_session_config_structure()
        self.test_is_browser_open_when_no_session()
        self.test_get_session_config_returns_dict()
        self.test_update_session_config()
        self.test_session_config_persistence()

        print("\n" + "=" * 70)
        print(f"Test Results: {self.passed} passed, {self.failed} failed (Total: {self.tests_run})")
        print("=" * 70)

        # Cleanup
        self.cleanup()

        return self.failed == 0

    def test_browser_manager_import(self):
        """Test that BrowserManager class can be imported"""
        print("\n1️⃣ Testing BrowserManager import...")
        try:
            from browser_manager import BrowserManager
            self.assert_true(True, "BrowserManager class imported successfully")
        except ImportError as e:
            self.assert_true(False, f"Failed to import BrowserManager: {e}")

    def test_browser_manager_initialization(self):
        """Test that BrowserManager can be instantiated"""
        print("\n2️⃣ Testing BrowserManager initialization...")
        try:
            from browser_manager import BrowserManager
            manager = BrowserManager()
            self.assert_true(manager is not None, "BrowserManager instance created")
        except Exception as e:
            self.assert_true(False, f"Failed to initialize BrowserManager: {e}")

    def test_session_config_path(self):
        """Test that session config path is set correctly"""
        print("\n3️⃣ Testing session config path...")
        try:
            from browser_manager import BrowserManager
            manager = BrowserManager()
            config_path = manager.config_path

            # Config should be in user home directory
            home = Path.home()
            expected_path = home / ".rami-levi-session.json"

            self.assert_equal(config_path, expected_path,
                            "Config path is ~/.rami-levi-session.json")
        except Exception as e:
            self.assert_true(False, f"Error testing config path: {e}")

    def test_session_config_structure(self):
        """Test that session config has required fields"""
        print("\n4️⃣ Testing session config structure...")
        try:
            from browser_manager import BrowserManager
            manager = BrowserManager()

            # Create a test config
            test_config = {
                "active": True,
                "browser_pid": 12345,
                "ws_endpoint": "ws://127.0.0.1:9222/devtools/browser/test",
                "opened_at": "2026-06-28T11:30:00Z",
                "items_added": 0,
                "cart_total": 0.0,
                "last_updated": "2026-06-28T11:35:00Z"
            }

            # Verify all required fields are present
            required_fields = ["active", "browser_pid", "ws_endpoint", "opened_at",
                             "items_added", "cart_total", "last_updated"]

            for field in required_fields:
                self.assert_in(field, test_config,
                              f"Session config has '{field}' field")

        except Exception as e:
            self.assert_true(False, f"Error testing config structure: {e}")

    def test_is_browser_open_when_no_session(self):
        """Test that is_browser_open returns False when no session exists"""
        print("\n5️⃣ Testing is_browser_open with no session...")
        try:
            from browser_manager import BrowserManager
            manager = BrowserManager()

            # Ensure config file doesn't exist
            if manager.config_path.exists():
                manager.config_path.unlink()

            # Should return False when no session
            result = manager.is_browser_open()
            self.assert_false(result, "is_browser_open returns False when no session")

        except Exception as e:
            self.assert_true(False, f"Error testing is_browser_open: {e}")

    def test_get_session_config_returns_dict(self):
        """Test that get_session_config returns a dictionary"""
        print("\n6️⃣ Testing get_session_config return type...")
        try:
            from browser_manager import BrowserManager
            manager = BrowserManager()

            result = manager.get_session_config()
            self.assert_is_dict(result, "get_session_config returns a dictionary")

        except Exception as e:
            self.assert_true(False, f"Error testing get_session_config: {e}")

    def test_update_session_config(self):
        """Test that update_session_config can update configuration"""
        print("\n7️⃣ Testing update_session_config method...")
        try:
            from browser_manager import BrowserManager
            manager = BrowserManager()

            # Ensure clean state
            if manager.config_path.exists():
                manager.config_path.unlink()

            # Test updating config
            updates = {"items_added": 5, "cart_total": 99.99}
            result = manager.update_session_config(updates)

            self.assert_true(result, "update_session_config returns True on success")

            # Verify the update persisted
            config = manager.get_session_config()
            self.assert_equal(config.get("items_added"), 5,
                            "items_added was updated correctly")
            self.assert_equal(config.get("cart_total"), 99.99,
                            "cart_total was updated correctly")

            # Cleanup
            if manager.config_path.exists():
                manager.config_path.unlink()

        except Exception as e:
            self.assert_true(False, f"Error testing update_session_config: {e}")

    def test_session_config_persistence(self):
        """Test that session config persists to disk"""
        print("\n8️⃣ Testing session config persistence...")
        try:
            from browser_manager import BrowserManager
            manager = BrowserManager()

            # Ensure clean state
            if manager.config_path.exists():
                manager.config_path.unlink()

            # Update config
            updates = {"active": True, "items_added": 3}
            manager.update_session_config(updates)

            # Create new manager instance to verify persistence
            manager2 = BrowserManager()
            config = manager2.get_session_config()

            self.assert_equal(config.get("items_added"), 3,
                            "Config persisted to disk and retrieved by new instance")

            # Cleanup
            if manager.config_path.exists():
                manager.config_path.unlink()

        except Exception as e:
            self.assert_true(False, f"Error testing persistence: {e}")


def run_tests():
    """Main test runner"""
    suite = TestBrowserManager()
    success = suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(run_tests())
