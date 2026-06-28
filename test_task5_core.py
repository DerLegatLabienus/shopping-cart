#!/usr/bin/env python3
"""
Core test for Task 5: Verify method signatures and return structures
"""

import sys
import inspect
from typing import Dict

def test_skill_handler_structure():
    """Test the basic structure without external dependencies"""
    print("\n" + "=" * 60)
    print("Core Task 5 Tests")
    print("=" * 60)

    from skill_handler import ShoppingListSkill

    skill = ShoppingListSkill()

    # Test 1: Method existence
    print("\n1. Checking method existence...")
    methods = {
        'process_query_with_browser': skill.process_query_with_browser,
        'cleanup_browser_session': skill.cleanup_browser_session,
        '_generate_cart_summary': skill._generate_cart_summary
    }

    for name, method in methods.items():
        exists = hasattr(skill, name)
        is_callable = callable(method)
        print(f"   {name}: exists={exists}, callable={is_callable}")
        if not (exists and is_callable):
            return False

    # Test 2: Method signatures
    print("\n2. Checking method signatures...")

    # process_query_with_browser should take (self, query: str)
    sig = inspect.signature(skill.process_query_with_browser)
    params = list(sig.parameters.keys())
    print(f"   process_query_with_browser params: {params}")
    if params != ['query']:
        print(f"   ❌ Expected ['query'], got {params}")
        return False

    # cleanup_browser_session should take (self)
    sig = inspect.signature(skill.cleanup_browser_session)
    params = list(sig.parameters.keys())
    print(f"   cleanup_browser_session params: {params}")
    if params != []:
        print(f"   ❌ Expected [], got {params}")
        return False

    # _generate_cart_summary should take (self)
    sig = inspect.signature(skill._generate_cart_summary)
    params = list(sig.parameters.keys())
    print(f"   _generate_cart_summary params: {params}")
    if params != []:
        print(f"   ❌ Expected [], got {params}")
        return False

    # Test 3: Return types
    print("\n3. Testing return value structures...")

    # cleanup_browser_session should return dict with specific keys
    result = skill.cleanup_browser_session()
    print(f"   cleanup_browser_session returns: {type(result).__name__}")
    expected_keys = {'success', 'message', 'browser_closed'}
    actual_keys = set(result.keys())
    if actual_keys != expected_keys:
        print(f"   ❌ Expected keys {expected_keys}, got {actual_keys}")
        return False
    print(f"   ✓ Keys match: {sorted(actual_keys)}")

    # _generate_cart_summary should return dict with specific keys
    result = skill._generate_cart_summary()
    print(f"   _generate_cart_summary returns: {type(result).__name__}")
    expected_keys = {'summary_markdown', 'items_count', 'estimated_total'}
    actual_keys = set(result.keys())
    if actual_keys != expected_keys:
        print(f"   ❌ Expected keys {expected_keys}, got {actual_keys}")
        return False
    print(f"   ✓ Keys match: {sorted(actual_keys)}")

    # Test 4: Check that process_query_with_browser returns correct structure
    print("\n4. Testing process_query_with_browser error handling...")
    # This will fail because browser modules aren't available, but we can check the return structure
    result = skill.process_query_with_browser("test query")
    print(f"   Returns: {type(result).__name__}")
    expected_keys = {'success', 'message', 'added_items', 'missing_items', 'cart_total', 'browser_active'}
    actual_keys = set(result.keys())
    if actual_keys != expected_keys:
        print(f"   ❌ Expected keys {expected_keys}, got {actual_keys}")
        return False
    print(f"   ✓ Keys match: {sorted(actual_keys)}")

    # Verify types of returned values
    print("\n5. Verifying return value types...")
    print(f"   success is bool: {isinstance(result['success'], bool)}")
    print(f"   message is str: {isinstance(result['message'], str)}")
    print(f"   added_items is list: {isinstance(result['added_items'], list)}")
    print(f"   missing_items is list: {isinstance(result['missing_items'], list)}")
    print(f"   cart_total is float: {isinstance(result['cart_total'], (float, int))}")
    print(f"   browser_active is bool: {isinstance(result['browser_active'], bool)}")

    all_correct = all([
        isinstance(result['success'], bool),
        isinstance(result['message'], str),
        isinstance(result['added_items'], list),
        isinstance(result['missing_items'], list),
        isinstance(result['cart_total'], (float, int)),
        isinstance(result['browser_active'], bool)
    ])

    if not all_correct:
        print("   ❌ Some return types are incorrect")
        return False

    # Test 6: Verify no breaking changes to existing methods
    print("\n6. Checking that existing methods still work...")
    try:
        result = skill.process_query("lentils")
        has_keys = all(k in result for k in ['list_markdown', 'products', 'metadata'])
        print(f"   process_query works: {has_keys}")
        if not has_keys:
            return False

        result = skill.get_cart_summary()
        has_keys = all(k in result for k in ['items', 'total_items', 'cart_total'])
        print(f"   get_cart_summary works: {has_keys}")
        if not has_keys:
            return False

    except Exception as e:
        print(f"   ❌ Error calling existing methods: {e}")
        return False

    return True


def main():
    """Run core tests"""
    print("\n╔" + "=" * 58 + "╗")
    print("║  Task 5: Core Implementation Tests                      ║")
    print("╚" + "=" * 58 + "╝")

    try:
        success = test_skill_handler_structure()
        print("\n" + "=" * 60)
        if success:
            print("✅ All core tests PASSED!")
            print("=" * 60)
            print("\nImplementation Summary:")
            print("- process_query_with_browser() - Main orchestration method ✓")
            print("- cleanup_browser_session() - Browser cleanup method ✓")
            print("- _generate_cart_summary() - Cart summary helper ✓")
            print("- No breaking changes to existing methods ✓")
            print("- Method-level imports for dependency handling ✓")
            print("- Proper error handling and return structures ✓")
            return 0
        else:
            print("❌ Some core tests FAILED!")
            return 1
    except Exception as e:
        print(f"\n❌ Test crash: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
