# Rami Levy Shopping Cart - System Architecture

## Overview

This system automates shopping list generation and cart management for the Rami Levy supermarket website. It consists of several integrated modules working together to provide a seamless shopping experience.

## Core Modules

### 1. **SearchEngine** (`search_engine.py`)
- Loads and indexes product database
- Supports advanced search with filters (budget, category, dietary preferences)
- Returns sorted results by price or relevance

### 2. **OutputFormatter** (`formatters.py`)
- Formats search results in multiple output formats (Markdown, JSON, CSV, HTML, plain text)
- Calculates totals and generates summaries
- Creates markdown tables and lists

### 3. **ShoppingListSkill** (`skill_handler.py`)
- Main skill interface for conversational shopping list generation
- Processes natural language queries to extract budget, categories, and dietary preferences
- Integrates search engine and formatters
- Manages local shopping cart state (in-memory cart dictionary)

### 4. **RamiLevyWebIntegration** (`rami_levy_web.py`)
- Tracks items added to the website's shopping cart
- Provides verification workflow for user-confirmed items
- Maintains cart state and session logs
- Generates manual workflows for website shopping

### 5. **WebScraper** (`web_scraper.py`)
- Extracts product data from Rami Levy website using Playwright + BeautifulSoup
- Searches products and retrieves details
- Checks product availability

### 6. **BrowserManager** (`browser_manager.py`)
- Manages Playwright browser lifecycle (launch, close)
- Persists session state to `~/.rami-levi-session.json`
- Tracks browser PID and WebSocket endpoint
- Updates session metadata (items added, cart total)

### 7. **CartAutomation** (`cart_automation.py`) - **NEW**
- Automates adding items to cart through browser interaction
- Extracts product names from HTML attributes
- Finds and clicks "Add to Cart" buttons with selector fallback
- Verifies items are in cart
- Retrieves cart totals with price parsing
- Tracks added items in session memory

## Data Flow

```
User Query
    ↓
ShoppingListSkill.process_query()
    ↓
SearchEngine.advanced_search()
    ↓
OutputFormatter.format_*()
    ↓
User sees formatted results
    ↓
[User initiates cart automation]
    ↓
BrowserManager.open_browser()
    ↓
CartAutomation.add_to_cart() [for each item]
    ↓
CartAutomation.verify_in_cart()
    ↓
CartAutomation.get_cart_total()
    ↓
User sees cart summary
```

## Key Design Patterns

### Guard Clauses
All CartAutomation methods guard against `page=None` at the start, returning complete dict structures with error info rather than crashing.

### Selector Fallback
`add_to_cart()` tries multiple selectors for the "Add to Cart" button:
1. `[data-action="add-to-cart"]` (data attribute)
2. `:has-text("הוסף לסל")` (Hebrew)
3. `:has-text("Add to cart")` (English)

### Price Parsing
Robust regex-based extraction: `[\d]+(?:\.\d+)?`
- Removes currency symbols (₪) and thousand separators (,)
- Handles decimal numbers safely

### State Tracking
- **In-memory cart**: ShoppingListSkill maintains a `self.cart` dict
- **Website tracking**: RamiLevyWebIntegration tracks what was added
- **Session tracking**: CartAutomation maintains `self.added_items` list
- **Browser state**: BrowserManager persists config to disk

## Integration Points

1. **Skill Handler ↔ Search Engine**: Query parsing and product search
2. **Skill Handler ↔ Web Integration**: Adding items to website cart
3. **Browser Manager ↔ Cart Automation**: Browser lifecycle and automation
4. **Web Integration ↔ Cart Automation**: Verification workflow coordination

## Future Enhancements

- Automatic price comparison between in-memory and website versions
- Cart persistence across sessions
- Multi-browser support (Firefox, Safari)
- Headless mode for automated deployments
- Real-time inventory sync
