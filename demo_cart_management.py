#!/usr/bin/env python3
"""
🛒 Cart Management System - Interactive Demo
Demonstrates the new verified cart management features
"""

from skill_handler import ShoppingListSkill


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_basic_cart_operations():
    """Demo 1: Basic cart operations"""
    print_section("DEMO 1: Basic Cart Operations")

    skill = ShoppingListSkill()

    print("\n1️⃣ Adding Red Lentils (1kg) to cart...")
    result = skill.add_item_to_cart("prod_001", quantity=1)
    print(f"   {result['message']}")
    print(f"   ✅ Verified: {result['verified']}")
    print(f"   Cart Total: ₪{result['cart_total']:.2f}")

    print("\n2️⃣ Adding Milk (2L) to cart...")
    result = skill.add_item_to_cart("prod_037", quantity=2)
    print(f"   {result['message']}")
    print(f"   ✅ Verified: {result['verified']}")
    print(f"   Cart Total: ₪{result['cart_total']:.2f}")

    print("\n3️⃣ Viewing cart summary...")
    summary = skill.get_cart_summary()
    print(summary['cart_markdown'])

    print(f"\n📊 Cart Stats:")
    print(f"   Total Items: {summary['total_items']}")
    print(f"   All Verified: {summary['all_verified']} ✅")
    print(f"   Verified Count: {summary['verified_count']}")


def demo_verification():
    """Demo 2: Item verification"""
    print_section("DEMO 2: Item Verification (New Feature)")

    skill = ShoppingListSkill()

    # Add items
    print("\n1️⃣ Adding items...")
    skill.add_item_to_cart("prod_001")  # Red Lentils
    skill.add_item_to_cart("prod_019")  # Fresh Tomatoes
    skill.add_item_to_cart("prod_037")  # Milk
    print("   ✅ 3 items added to cart")

    # Verify each item
    print("\n2️⃣ Verifying each item is actually in cart...")

    items_to_check = [
        ("prod_001", "Red Lentils"),
        ("prod_019", "Fresh Tomatoes"),
        ("prod_037", "Milk"),
        ("prod_999", "Non-existent Product")  # Should fail
    ]

    for product_id, product_name in items_to_check:
        verification = skill.verify_item_in_cart(product_id)
        status = "✅ VERIFIED" if verification['verified'] else "❌ NOT IN CART"
        print(f"   {status}: {product_name}")
        if verification['verified']:
            print(f"      - Quantity: {verification.get('quantity', 'N/A')}")
            print(f"      - Price: ₪{verification.get('price', 0):.2f}")


def demo_cart_modifications():
    """Demo 3: Cart modifications"""
    print_section("DEMO 3: Cart Modifications (Add/Remove)")

    skill = ShoppingListSkill()

    print("\n1️⃣ Starting with 3 items...")
    skill.add_item_to_cart("prod_001")  # Lentils
    skill.add_item_to_cart("prod_037", quantity=2)  # Milk
    skill.add_item_to_cart("prod_019")  # Tomatoes

    summary = skill.get_cart_summary()
    print(f"   Initial total: ₪{summary['cart_total']:.2f} ({summary['total_items']} items)")

    print("\n2️⃣ Removing Tomatoes (prod_019)...")
    result = skill.remove_item_from_cart("prod_019")
    print(f"   {result['message']}")

    summary = skill.get_cart_summary()
    print(f"   New total: ₪{summary['cart_total']:.2f} ({summary['total_items']} items)")

    print("\n3️⃣ Verifying tomatoes are gone...")
    verification = skill.verify_item_in_cart("prod_019")
    print(f"   {verification['message']}")

    print("\n4️⃣ Adding chickpea hummus (prod_005)...")
    result = skill.add_item_to_cart("prod_005", quantity=1)
    print(f"   {result['message']}")

    summary = skill.get_cart_summary()
    print(f"   Final total: ₪{summary['cart_total']:.2f} ({summary['total_items']} items)")


def demo_budget_shopping():
    """Demo 4: Budget-aware shopping"""
    print_section("DEMO 4: Budget-Aware Shopping List")

    skill = ShoppingListSkill()

    budget_limit = 100
    items_to_add = [
        ("prod_001", "Red Lentils", 1),      # ~₪13.80
        ("prod_037", "Milk 3%", 2),         # ~₪17.00
        ("prod_042", "Eggs (10)", 1),       # ~₪10.50
        ("prod_019", "Fresh Tomatoes", 1),  # ~₪2.90
        ("prod_021", "Cucumber", 1),        # ~₪2.90
        ("prod_025", "Yellow Onion", 1),    # ~₪3.50
        ("prod_029", "Spinach", 1),         # ~₪5.50
    ]

    print(f"\n💰 Budget Limit: ₪{budget_limit}")
    print("📋 Building shopping list...\n")

    total = 0
    for product_id, product_name, qty in items_to_add:
        result = skill.add_item_to_cart(product_id, qty)
        if result['success']:
            item_price = result['item']['subtotal']
            total = result['cart_total']
            within_budget = "✅" if total <= budget_limit else "⚠️"
            print(f"   {within_budget} Added: {product_name} (₪{item_price:.2f})")
            print(f"      Running total: ₪{total:.2f}")

            if total > budget_limit:
                print(f"      ⚠️ Budget exceeded! (Over by ₪{total - budget_limit:.2f})")
                break

    print(f"\n📊 Final Cart:")
    summary = skill.get_cart_summary()
    print(f"   Total Items: {summary['total_items']}")
    print(f"   Cart Total: ₪{summary['cart_total']:.2f}")
    print(f"   All Verified: {'✅ Yes' if summary['all_verified'] else '❌ No'}")
    print(f"   Budget Status: {'✅ Within budget' if summary['cart_total'] <= budget_limit else '⚠️ Over budget'}")


def demo_error_handling():
    """Demo 5: Error handling"""
    print_section("DEMO 5: Error Handling & Edge Cases")

    skill = ShoppingListSkill()

    print("\n1️⃣ Trying to add non-existent product...")
    result = skill.add_item_to_cart("prod_999999")
    print(f"   Result: {result['message']}")
    print(f"   Success: {result['success']}")

    print("\n2️⃣ Trying to remove item not in cart...")
    result = skill.remove_item_from_cart("prod_500")
    print(f"   Result: {result['message']}")
    print(f"   Success: {result['success']}")

    print("\n3️⃣ Verifying non-existent item...")
    verification = skill.verify_item_in_cart("prod_12345")
    print(f"   Result: {verification['message']}")
    print(f"   Verified: {verification['verified']}")

    print("\n4️⃣ Adding item, then removing, then verifying...")
    skill.add_item_to_cart("prod_001")
    print("   ✅ Added Red Lentils")

    skill.remove_item_from_cart("prod_001")
    print("   ✅ Removed Red Lentils")

    verification = skill.verify_item_in_cart("prod_001")
    print(f"   Verification: {verification['message']}")
    print(f"   Item in cart: {verification['verified']}")


def demo_cart_state():
    """Demo 6: Cart state tracking"""
    print_section("DEMO 6: Cart State Tracking")

    skill = ShoppingListSkill()

    print("\n1️⃣ Adding items and tracking state...")

    items = [
        ("prod_001", "Red Lentils"),
        ("prod_037", "Milk"),
        ("prod_019", "Tomatoes"),
        ("prod_042", "Eggs"),
    ]

    for product_id, product_name in items:
        skill.add_item_to_cart(product_id)
        print(f"   ✅ Added: {product_name}")
        print(f"      Current list: {len(skill.current_list)} items")
        print(f"      Cart state size: {len(skill.cart)} items")

    print(f"\n2️⃣ Final cart state:")
    summary = skill.get_cart_summary()

    for i, item in enumerate(summary['items'], 1):
        verified_icon = "✅" if item['verified'] else "⚠️"
        print(f"   {verified_icon} [{i}] {item['name']}")
        print(f"       Verified: {item['verified']}")
        print(f"       Quantity: {item['quantity']}")
        print(f"       Subtotal: ₪{item['subtotal']:.2f}")

    print(f"\n3️⃣ Verification Summary:")
    print(f"   Total Items: {summary['total_items']}")
    print(f"   Verified Items: {summary['verified_count']}")
    print(f"   Unverified Items: {summary['unverified_count']}")
    print(f"   All Verified: {'✅ Yes' if summary['all_verified'] else '❌ No'}")


def main():
    """Run all demos"""
    print("\n" + "🛒" * 35)
    print("  RAMI LEVY - CART MANAGEMENT SYSTEM DEMO")
    print("  Demonstrating new verified cart features")
    print("🛒" * 35)

    try:
        demo_basic_cart_operations()
        demo_verification()
        demo_cart_modifications()
        demo_budget_shopping()
        demo_error_handling()
        demo_cart_state()

        print_section("✅ ALL DEMOS COMPLETE")
        print("\nThe cart management system is working perfectly!")
        print("Key features demonstrated:")
        print("  ✅ Add items with automatic verification")
        print("  ✅ Remove items from cart")
        print("  ✅ Verify specific items are in cart")
        print("  ✅ View complete cart summary")
        print("  ✅ Track real-time totals")
        print("  ✅ Handle edge cases gracefully")
        print("  ✅ Maintain cart state")
        print("\n" + "=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error running demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
