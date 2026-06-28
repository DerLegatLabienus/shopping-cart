#!/usr/bin/env python3
"""
Test script for Task 5: Browser Integration Methods
Verifies that the new methods are properly added to skill_handler.py
"""

import sys
from skill_handler import ShoppingListSkill

def test_method_existence():
    """Test that all three new methods exist"""
    print("=" * 60)
    print("TEST 1: Verify Methods Exist")
    print("=" * 60)

    skill = ShoppingListSkill()

    # Check if methods exist
    has_process_query_with_browser = hasattr(skill, 'process_query_with_browser')
    has_cleanup_browser = hasattr(skill, 'cleanup_browser_session')
    has_generate_summary = hasattr(skill, '_generate_cart_summary')

    print(f"✓ process_query_with_browser exists: {has_process_query_with_browser}")
    print(f"✓ cleanup_browser_session exists: {has_cleanup_browser}")
    print(f"✓ _generate_cart_summary exists: {has_generate_summary}")

    if all([has_process_query_with_browser, has_cleanup_browser, has_generate_summary]):
        print("\n✅ All methods exist!\n")
        return True
    else:
        print("\n❌ Some methods are missing!\n")
        return False


def test_return_dict_structure():
    """Test that methods return proper dict structures"""
    print("=" * 60)
    print("TEST 2: Verify Return Dict Structures")
    print("=" * 60)

    skill = ShoppingListSkill()

    # Test cleanup_browser_session return structure
    print("\nTesting cleanup_browser_session return structure...")
    cleanup_result = skill.cleanup_browser_session()
    print(f"  Returned type: {type(cleanup_result)}")
    print(f"  Keys: {list(cleanup_result.keys())}")

    expected_cleanup_keys = {'success', 'message', 'browser_closed'}
    cleanup_keys = set(cleanup_result.keys())
    cleanup_structure_ok = expected_cleanup_keys == cleanup_keys
    print(f"  Structure OK: {cleanup_structure_ok}")

    # Test _generate_cart_summary return structure
    print("\nTesting _generate_cart_summary return structure...")
    summary_result = skill._generate_cart_summary()
    print(f"  Returned type: {type(summary_result)}")
    print(f"  Keys: {list(summary_result.keys())}")

    expected_summary_keys = {'summary_markdown', 'items_count', 'estimated_total'}
    summary_keys = set(summary_result.keys())
    summary_structure_ok = expected_summary_keys == summary_keys
    print(f"  Structure OK: {summary_structure_ok}")

    if cleanup_structure_ok and summary_structure_ok:
        print("\n✅ All return structures are correct!\n")
        return True
    else:
        print("\n❌ Some return structures are incorrect!\n")
        return False


def test_imports_work():
    """Test that imports work without errors"""
    print("=" * 60)
    print("TEST 3: Verify Imports Work")
    print("=" * 60)

    try:
        from browser_manager import BrowserManager
        print("✓ BrowserManager imported successfully")
    except Exception as e:
        print(f"❌ BrowserManager import failed: {e}")
        return False

    try:
        from web_scraper import WebScraper
        print("✓ WebScraper imported successfully")
    except Exception as e:
        print(f"❌ WebScraper import failed: {e}")
        return False

    try:
        from cart_automation import CartAutomation
        print("✓ CartAutomation imported successfully")
    except Exception as e:
        print(f"❌ CartAutomation import failed: {e}")
        return False

    print("\n✅ All imports work!\n")
    return True


def test_skill_handler_existing_methods():
    """Test that existing skill_handler methods still work"""
    print("=" * 60)
    print("TEST 4: Verify Existing Methods Still Work")
    print("=" * 60)

    skill = ShoppingListSkill()

    # Test process_query (should not error)
    try:
        result = skill.process_query("lentils")
        has_required_keys = all(k in result for k in ['list_markdown', 'products', 'metadata'])
        print(f"✓ process_query works: {has_required_keys}")
    except Exception as e:
        print(f"❌ process_query failed: {e}")
        return False

    # Test get_cart_summary
    try:
        result = skill.get_cart_summary()
        has_required_keys = all(k in result for k in ['items', 'total_items', 'cart_total'])
        print(f"✓ get_cart_summary works: {has_required_keys}")
    except Exception as e:
        print(f"❌ get_cart_summary failed: {e}")
        return False

    # Test add_item_to_cart
    try:
        # Get a valid product ID first
        result = skill.process_query("lentils")
        if result['products']:
            product_id = result['products'][0]['id']
            cart_result = skill.add_item_to_cart(product_id)
            has_required_keys = all(k in cart_result for k in ['success', 'message', 'cart_total'])
            print(f"✓ add_item_to_cart works: {has_required_keys}")
        else:
            print("⚠️ Could not test add_item_to_cart (no products found)")
    except Exception as e:
        print(f"❌ add_item_to_cart failed: {e}")
        return False

    print("\n✅ All existing methods still work!\n")
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  Task 5: Browser Integration - Integration Tests         ║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        ("Method Existence", test_method_existence),
        ("Return Dict Structures", test_return_dict_structure),
        ("Imports Work", test_imports_work),
        ("Existing Methods", test_skill_handler_existing_methods),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}\n")
            results.append((test_name, False))

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result for _, result in results)
    print()
    if all_passed:
        print("🎉 All tests PASSED!")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
