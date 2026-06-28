---
name: rami-levi-shopping-cart
description: "Search, filter, and manage vegetarian shopping lists from Rami Levy supermarket. Use when users need to find specific products, build budget-conscious shopping lists, filter by dietary preferences (vegan, organic, kosher), or manage a shopping cart with item verification. Handles natural language queries like 'lentils under 50 shekels', 'organic vegetables', or 'build a shopping list for 100-200 shekels'."
triggers:
  - rami levi
  - rami levy
  - shopping cart
  - shopping list
  - vegetarian products
  - kosher products
  - organic vegetables
  - budget shopping
  - price range shopping
---

# Rami Levy Vegetarian Shopping List Skill

Search and discover vegetarian products from Rami Levy supermarket with smart filtering and multiple output formats.

## When to Use This Skill

Use this skill whenever the user wants to:
- **Search for specific products** — "Find lentils", "Show me chickpeas", "What vegetables do you have?"
- **Build budget-conscious lists** — "Shopping list under 50 shekels", "Ingredients for 100-200 shekels"
- **Filter by dietary preferences** — "Vegan products", "Organic vegetables", "Kosher options"
- **Manage a shopping cart** — Add items, verify they're in the cart, check totals, remove items
- **Get product recommendations** — "What legumes are available?", "Cheap organic options?"
- **Export shopping lists** — Markdown, JSON, CSV, HTML, or plain text formats

## Capabilities

### Search & Discovery
- **Product Name Search** with fuzzy matching — finds items even with typos
- **Category Filtering** — legumes, vegetables, dairy, organic, frozen, grains, bread, condiments, fruits, pantry
- **Price Range Filtering** — "under 50", "100-200", natural language budget parsing
- **Dietary Preferences** — vegan, organic, kosher, ready-to-eat attributes

### Shopping Cart Management
- **Add items** with automatic verification
- **Remove items** anytime
- **Verify items** in cart with confirmation
- **View cart summary** with all items, quantities, prices
- **Calculate totals** in real-time

### Output Formats
- 📋 **Markdown** — pretty formatted shopping list (default)
- 📊 **JSON** — structured data for integration
- 📈 **CSV** — spreadsheet-compatible format
- 🌐 **HTML Table** — interactive web format
- 📝 **Plain Text** — simple checklist with checkboxes

### Conversational Features
- Asks clarifying questions when queries are ambiguous
- Suggests refinements based on user criteria
- Provides product summaries with prices
- Calculates total cost automatically

## Input Format

Accept user queries in natural language:

```
"Find lentils"
"Chickpeas under 10 shekels"
"Organic vegetables"
"Build a shopping list for 100-200 shekels"
"Vegan products"
"Add prod_001 to cart"
"What's in my cart?"
"Export as CSV"
```

## Output Format

Default: Markdown shopping list with:
- Product names and categories
- Prices in Israeli Shekels (₪)
- Dietary attributes (vegan, organic, kosher, etc.)
- Total price

Alternative formats available: JSON, CSV, HTML, plain text.

Example markdown output:
```markdown
# Shopping List: Legumes

| Product | Category | Price | Attributes |
|---------|----------|-------|-----------|
| Red Lentils | legumes | ₪7.00 | vegan |
| Hummus | legumes | ₪9.50 | vegan |

**Total: ₪16.50** (2 items)
```

## Success Criteria

✅ User's query is understood and products are found  
✅ Results are filtered correctly by budget/diet/category  
✅ Cart items are added/removed/verified successfully  
✅ Output is in the requested format  
✅ Total price is calculated correctly  
✅ Clarifying questions help when results are ambiguous  

## Constraints & Pitfalls

### Data Limitations
- Static product database (87 items, updated monthly)
- Prices may vary by location/time
- Limited to primary size options
- Real-time inventory not checked
- Rami Levy stores only

### Search Pitfalls
- Typos in product names still work (fuzzy matching) but may return unexpected results
- Price ranges must be numeric (e.g., "100-200" not "one hundred to two hundred")
- Some categories have aliases ("veggies" → "vegetables") but not all colloquialisms are recognized

### Cart Management
- Cart is session-scoped (resets between sessions)
- Quantity tracking works but no stock validation
- Verification is local, not checked against Rami Levy inventory

## Verification Steps

1. **Search works:** Query "lentils" returns lentil products
2. **Budget parsing:** Query "under 50" correctly extracts price limit
3. **Category detection:** Query "organic vegetables" finds both attributes
4. **Cart operations:** Add item, verify it's there, remove it, verify it's gone
5. **Format export:** Same query in markdown/JSON/CSV produces consistent data
6. **Empty results:** Ambiguous query generates helpful clarifying questions
7. **Total calculation:** Adding 3 items shows correct sum

## Architecture

### Components
- **SearchEngine** — Product database, fuzzy matching, filtering
- **OutputFormatter** — Multi-format conversion (markdown, JSON, CSV, HTML, text)
- **ShoppingListSkill** — Query parser, clarifying questions, cart management

### Data Model
```json
{
  "product": {
    "id": "prod_001",
    "name": "Red Lentils",
    "category": "legumes",
    "brand": "Rami Levy",
    "sizes": [{"size": "500g", "price": 7.00}],
    "attributes": ["vegetarian", "vegan"],
    "organic": false
  },
  "cart_item": {
    "product_id": "prod_001",
    "quantity": 1,
    "verified": true
  }
}
```

## Example Workflows

### Workflow 1: Simple Search
```
User: "Find lentils"
→ Skill searches by name with fuzzy matching
→ Returns all lentil products sorted by price
→ Offers clarifying questions (size, budget, etc.)
```

### Workflow 2: Budget Shopping
```
User: "I have 100 shekels, what legumes can I get?"
→ Parses budget constraint
→ Extracts category preference
→ Returns legumes under ₪100
→ Calculates total cost
```

### Workflow 3: Diet-Specific
```
User: "Vegan shopping list"
→ Recognizes dietary preference
→ Asks which categories matter most
→ Filters for vegan attribute
→ Returns organized list
```

### Workflow 4: Cart Management
```
User: "Add prod_001 to my cart"
→ Adds item with verification
User: "What's in my cart?"
→ Shows cart summary with items and total
User: "Remove prod_001"
→ Removes item, updates total
```

## Open Questions / Notes

- Currently no user preference persistence across sessions
- Could add recipe templates in future
- Nutritional info not yet included in database
- Price comparison with other stores not supported
- No meal planning or combination suggestions yet

## Implementation Notes

- Uses fuzzy matching (difflib) for typo tolerance
- Budget parsing handles multiple formats: "under X", "X-Y", "X shekels"
- Category aliases reduce friction for colloquial language
- All output formats derived from same data model
- Cart verification is local; no sync with actual Rami Levy inventory
