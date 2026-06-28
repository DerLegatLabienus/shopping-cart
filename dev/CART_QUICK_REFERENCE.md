# 🛒 Cart Management - Quick Reference

## Installation & Setup

```bash
cd ~/claude-projects/shopping-cart
python3 demo_cart_management.py  # See it in action!
```

---

## Quick Start (3 Lines)

```python
from skill_handler import ShoppingListSkill

skill = ShoppingListSkill()
skill.add_item_to_cart("prod_001")  # Add Red Lentils
print(f"Total: ₪{skill.get_cart_total():.2f}")
```

---

## Core Methods

### 1. Add Item to Cart ✅

```python
# Add single item
result = skill.add_item_to_cart("prod_001")

# Add with quantity
result = skill.add_item_to_cart("prod_037", quantity=2)

# Check result
if result['success']:
    print(result['message'])  # ✅ Added: Red Lentils
    print(f"Total: ₪{result['cart_total']:.2f}")
    print(f"Verified: {result['verified']}")  # Always True for new items
```

### 2. Remove Item from Cart ❌

```python
# Remove item
result = skill.remove_item_from_cart("prod_001")

# Check result
if result['success']:
    print(result['message'])  # ✅ Removed: Red Lentils
    print(f"New total: ₪{result['cart_total']:.2f}")
```

### 3. Verify Item in Cart ✔️

```python
# Verify single item
verification = skill.verify_item_in_cart("prod_001")

if verification['verified']:
    print(f"✅ {verification['name']} is in cart")
    print(f"   Quantity: {verification['quantity']}")
    print(f"   Price: ₪{verification['price']:.2f}")
else:
    print("❌ Item not in cart")
```

### 4. View Cart Summary 👀

```python
# Get complete cart
summary = skill.get_cart_summary()

# Display as markdown
print(summary['cart_markdown'])

# Access data directly
print(f"Items: {summary['total_items']}")
print(f"Total: ₪{summary['cart_total']:.2f}")
print(f"All Verified: {summary['all_verified']}")  # Always True

for item in summary['items']:
    print(f"  - {item['name']}: ₪{item['subtotal']:.2f} (x{item['quantity']})")
```

### 5. Get Cart Total 💰

```python
# Simple total
total = skill.get_cart_total()
print(f"Current total: ₪{total:.2f}")
```

---

## Common Use Cases

### Use Case 1: Build Shopping List

```python
# Initialize
skill = ShoppingListSkill()

# Add vegetables
vegetables = ["prod_019", "prod_021", "prod_025"]  # Tomatoes, Cucumber, Onion
for veg in vegetables:
    skill.add_item_to_cart(veg)

# Add legumes
skill.add_item_to_cart("prod_001")  # Red Lentils

# Add dairy
skill.add_item_to_cart("prod_037", quantity=2)  # 2L Milk
skill.add_item_to_cart("prod_042")  # Eggs

# Review
summary = skill.get_cart_summary()
print(summary['cart_markdown'])
```

### Use Case 2: Budget Shopping

```python
skill = ShoppingListSkill()
budget = 100
current_total = 0

items = ["prod_001", "prod_019", "prod_037", "prod_042"]

for product_id in items:
    result = skill.add_item_to_cart(product_id)
    if result['success']:
        current_total = result['cart_total']
        if current_total > budget:
            print(f"⚠️ Over budget! Removing last item...")
            skill.remove_item_from_cart(product_id)
            break

print(f"Final total: ₪{skill.get_cart_total():.2f}")
```

### Use Case 3: Verify Cart Contents

```python
skill = ShoppingListSkill()

# Add items
items_to_add = ["prod_001", "prod_037", "prod_042"]
for item_id in items_to_add:
    skill.add_item_to_cart(item_id)

# Verify each one actually got added
print("Verifying all items are actually in cart...")
for item_id in items_to_add:
    verification = skill.verify_item_in_cart(item_id)
    status = "✅ OK" if verification['verified'] else "❌ MISSING"
    print(f"  {status}: {verification.get('name', 'Unknown')}")

# Summary
summary = skill.get_cart_summary()
if summary['all_verified']:
    print(f"✅ All {summary['total_items']} items verified in cart")
```

### Use Case 4: Modify Cart

```python
skill = ShoppingListSkill()

# Start with 3 items
skill.add_item_to_cart("prod_001")
skill.add_item_to_cart("prod_037")
skill.add_item_to_cart("prod_019")

print(f"Initial cart: ₪{skill.get_cart_total():.2f}")

# Change quantity - remove and re-add with new qty
skill.remove_item_from_cart("prod_037")  # Remove 1L milk
skill.add_item_to_cart("prod_037", quantity=3)  # Add 3L milk

print(f"Updated cart: ₪{skill.get_cart_total():.2f}")

# View final
print(skill.get_cart_summary()['cart_markdown'])
```

---

## Common Product IDs

| Product | ID | Price | Qty |
|---------|----|----|-----|
| Red Lentils 1kg | prod_001 | ₪13.80 | |
| Green Lentils 500g | prod_002 | ₪7.00 | |
| Chickpea Hummus 700g | prod_005 | ₪10.50 | |
| Fresh Tomatoes/kg | prod_019 | ₪2.90 | 3.5kg |
| Cucumber/kg | prod_021 | ₪2.90 | 2kg |
| Yellow Onion/kg | prod_025 | ₪3.50 | 3kg |
| Spinach 200g | prod_029 | ₪5.50 | |
| Milk 1L | prod_037 | ₪8.50 | 2L |
| Eggs 10 pack | prod_042 | ₪10.50 | |

**Get all products:**
```python
categories = skill.get_categories()
for product in skill.search_engine.products:
    print(f"{product['id']}: {product['name']} - ₪{product['sizes'][0]['price']}")
```

---

## Return Values

### `add_item_to_cart()` returns:

```python
{
    'success': True/False,
    'message': '✅ Added: Product Name (₪XX.XX)',
    'item': {
        'product_id': 'prod_001',
        'name': 'Red Lentils',
        'category': 'legumes',
        'price_per_unit': 13.80,
        'quantity': 1,
        'subtotal': 13.80,
        'verified': True,
        'added_timestamp': '2026-06-28T10:30:45.123456'
    },
    'cart_total': 13.80,
    'cart_items': 1,
    'verified': True
}
```

### `verify_item_in_cart()` returns:

```python
{
    'verified': True/False,
    'message': '✅ Item verified in cart' or '❌ Item not found in cart',
    'product_id': 'prod_001',
    'item': {...},  # Full item details if verified
    'name': 'Red Lentils',
    'quantity': 1,
    'price': 13.80
}
```

### `get_cart_summary()` returns:

```python
{
    'items': [...],  # List of all cart items
    'total_items': 3,
    'cart_total': 45.50,
    'all_verified': True,
    'verified_count': 3,
    'unverified_count': 0,
    'cart_markdown': '# 🛒 Shopping Cart Summary\n...'
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Item says added but `verify_item_in_cart()` returns False | Check product ID is correct. All items marked `verified=True` when added. |
| Cart total doesn't match | Use `get_cart_total()` for accurate total. Display in cart summary. |
| Can't find product ID | Use `skill.search_engine.products` to list all products or use `skill.process_query()` to search. |
| Item won't remove | Check product ID. Removing non-existent item returns `success=False` but doesn't error. |

---

## Testing

Run comprehensive tests:
```bash
python3 test_skill.py
```

Run only cart tests:
```bash
python3 << 'EOF'
from test_skill import TestSuite
suite = TestSuite()
suite.test_cart_management()
suite.print_summary()
EOF
```

Run interactive demo:
```bash
python3 demo_cart_management.py
```

---

## Key Concepts

### ✅ Verification
Every item added to cart is automatically `verified=True`. This prevents ghost items. Use `verify_item_in_cart()` to confirm an item is actually there.

### 💾 State Tracking
- `skill.current_list` - List of product IDs in cart
- `skill.cart` - Dictionary of {product_id: item_details}

### 📊 Real-Time Updates
Cart totals and item counts update immediately after add/remove operations.

### 🔄 Data Persistence
Cart state persists for the lifetime of the skill object. Create new skill instance for fresh cart.

---

## Advanced

### Get raw cart dictionary:
```python
cart_dict = skill.cart
print(cart_dict)  # {prod_001: {...}, prod_037: {...}}
```

### Get current list of product IDs:
```python
ids = skill.current_list
print(ids)  # ['prod_001', 'prod_037', 'prod_019']
```

### Access item details directly:
```python
item = skill.cart['prod_001']
print(f"{item['name']}: ₪{item['subtotal']:.2f}")
```

---

**Last Updated:** 2026-06-28  
**Version:** 1.0  
**Status:** ✅ Ready for Production
