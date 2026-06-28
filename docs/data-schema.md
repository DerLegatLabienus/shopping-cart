# Data Schema - Rami Levy Shopping Cart System

## Product Schema

### Product Object
```json
{
  "id": "string (unique product ID)",
  "name": "string",
  "category": "string (e.g., 'vegetables', 'legumes', 'dairy')",
  "brand": "string",
  "sizes": [
    {
      "size": "string (e.g., '1kg', '500g')",
      "price": "float (shekel price)",
      "availability": "boolean"
    }
  ],
  "attributes": ["string"] (e.g., ['vegan', 'organic', 'kosher']),
  "url": "string (product page URL, optional)"
}
```

## Cart State Schema

### ShoppingListSkill.cart
```json
{
  "product_id": {
    "product_id": "string",
    "name": "string",
    "category": "string",
    "brand": "string",
    "price_per_unit": "float",
    "quantity": "float",
    "subtotal": "float",
    "verified": "boolean",
    "added_timestamp": "string (ISO 8601)"
  }
}
```

### CartAutomation.added_items
```json
[
  {
    "name": "string (product name)",
    "url": "string (product page URL)",
    "quantity": "integer"
  }
]
```

## API Response Schemas

### add_to_cart() Response
```json
{
  "success": "boolean",
  "message": "string (status message)",
  "product_name": "string",
  "quantity": "integer"
}
```

**Success example:**
```json
{
  "success": true,
  "message": "✅ Added Tomatoes (qty: 2) to cart",
  "product_name": "Tomatoes",
  "quantity": 2
}
```

**Error example:**
```json
{
  "success": false,
  "message": "❌ Page is None - cannot add to cart",
  "product_name": "",
  "quantity": 1
}
```

### verify_in_cart() Response
```json
{
  "verified": "boolean",
  "quantity": "integer",
  "message": "string"
}
```

**Success example:**
```json
{
  "verified": true,
  "quantity": 2,
  "message": "✅ Tomatoes verified in cart (qty: 2)"
}
```

**Error example:**
```json
{
  "verified": false,
  "quantity": 0,
  "message": "❌ Tomatoes not found in cart"
}
```

### get_cart_total() Response
```
float (total price in shekels, or 0.0 on error)
```

**Examples:**
- Success: `250.50`
- Error or no page: `0.0`

### get_added_items() Response
```json
[
  {
    "name": "string",
    "url": "string",
    "quantity": "integer"
  }
]
```

**Example:**
```json
[
  {
    "name": "Tomatoes",
    "url": "https://www.rami-levy.co.il/he/online/product/123",
    "quantity": 2
  },
  {
    "name": "Red Lentils",
    "url": "https://www.rami-levy.co.il/he/online/product/456",
    "quantity": 1
  }
]
```

## Search Results Schema

### advanced_search() Return
```json
{
  "products": ["array of Product objects"],
  "metadata": {
    "total": "integer",
    "filtered": "integer",
    "time_ms": "integer",
    "filters_applied": {
      "budget": ["min", "max"],
      "categories": ["array of category strings"],
      "attributes": ["array of dietary preference strings"]
    }
  }
}
```

## Session State Schema

### BrowserManager Session Config (~/.rami-levi-session.json)
```json
{
  "active": "boolean",
  "browser_pid": "integer or null",
  "ws_endpoint": "string or null",
  "opened_at": "string (ISO 8601)",
  "items_added": "integer",
  "cart_total": "float",
  "last_updated": "string (ISO 8601)"
}
```

## HTML Element Selectors

### Cart Automation Expects These HTML Attributes

**Product Name:**
```html
<element data-productname="Product Name">...</element>
```

**Quantity Input:**
```html
<input data-quantity type="number" value="1" />
```

**Add to Cart Button (one of):**
```html
<button data-action="add-to-cart">Add to Cart</button>
<!-- OR -->
<button>הוסף לסל</button>  <!-- Hebrew -->
<!-- OR -->
<button>Add to cart</button>
```

**Cart Page Items:**
```html
<div data-cartitem>
  <span data-productname="Product Name">...</span>
  <input data-quantity="2" />
</div>
```

**Cart Total:**
```html
<div data-carttotal>₪250.50</div>
<!-- OR -->
<div class="cart-total">Total: ₪250.50</div>
```

## Price Format

Prices are stored and manipulated as floats in shekels (₪).

**Formatting for display:**
- `₪{price:.2f}` (e.g., "₪150.50")
- With thousand separator: `₪{price:,.2f}` (e.g., "₪1,250.50")

**Parsing from HTML:**
- Remove shekel symbol: `text.replace('₪', '')`
- Remove thousand separators: `.replace(',', '')`
- Extract number: `re.search(r'[\d]+(?:\.\d+)?', text)`
- Convert to float: `float(match.group())`
