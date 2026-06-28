# Rami Levy Shopping Skill — Browser Automation Design

**Date:** June 28, 2026  
**Status:** Approved for Implementation  
**Approach:** Playwright + Session Config

---

## Executive Summary

Upgrade the Rami Levy shopping skill to **open Chrome, fetch real products from the Rami Levy website, and automatically add items to their live shopping cart**. The browser stays open and persistent, allowing follow-up commands to continue adding items to the same cart session.

**Key Goals:**
- ✅ Automate real shopping on rami-levy.co.il
- ✅ Keep browser visible and interactive
- ✅ Support persistent sessions across multiple skill invocations
- ✅ Gracefully handle missing items with summary reporting
- ✅ Guest-mode preferred, ask for login if needed

---

## Architecture

### System Overview

```
User Query
    ↓
Skill Handler (Parse + Build List)
    ↓
Browser Session Manager (Check for open session)
    ├─ Session exists? → Reuse it
    └─ No session? → Launch Playwright
    ↓
Web Scraper (Search Rami Levy for products)
    ↓
Playwright Automation (Add items to cart)
    ↓
Session Config (~/.rami-levi-session.json) → Save browser reference
    ↓
Chrome Window (Visible, shows filled cart)
    ↓
Report (What was added, what failed)
```

### Components

#### **1. Browser Manager (`browser_manager.py`)**

Manages Playwright browser lifecycle and session persistence.

**Key Methods:**
- `open_browser()` — Launch Chrome, save session reference to config file
- `get_browser()` — Retrieve existing session from `~/.rami-levi-session.json`
- `is_browser_open()` — Check if session is still active
- `close_browser()` — Kill browser and cleanup config
- `navigate_to_cart()` — Navigate to Rami Levy cart page
- `get_browser_state()` — Return current session state (for follow-ups)

**Session Persistence:**
- Uses `~/.rami-levi-session.json` to track active browser
- Stores: browser PID, WebSocket endpoint, opened timestamp, items added count
- Allows multiple skill invocations to reuse same browser window

#### **2. Web Scraper (`web_scraper.py`)**

Scrapes Rami Levy website to find products and get real-time data.

**Key Methods:**
- `search_product(product_name)` — Search for product, return URL + metadata
- `get_product_details(product_url)` — Extract price, availability, attributes
- `is_product_available(product_url)` — Check if in stock

**Approach:**
- Use Playwright to navigate site (handles JavaScript rendering)
- Parse HTML for product links and prices
- Extract product URLs for cart automation

#### **3. Cart Automation (`cart_automation.py`)**

Automates adding items to cart via Playwright browser control.

**Key Methods:**
- `add_to_cart(browser, product_url, quantity)` — Navigate to product, click add, set quantity
- `verify_in_cart(browser, product_name)` — Check if item appears in cart
- `get_cart_total(browser)` — Scrape current cart total from page
- `handle_missing_item(product_name)` — Track failed additions

**Error Handling:**
- If product page not found: Skip, add to missing items list
- If add-to-cart fails: Retry once, then skip
- If login required: Show prompt to user

#### **4. Enhanced Skill Handler (`skill_handler.py`)**

Add new methods to orchestrate browser integration.

**New Methods:**
- `process_query_with_browser(query)` — Build list + add items to website
- `handle_missing_items(missing_list)` — Compile summary of unfound items
- `generate_cart_summary(added_count, missing_count, cart_total)` — Final report
- `cleanup_browser_session()` — Close browser and remove config

---

## Data Flow Examples

### Example 1: Initial Shopping List

```
User: "build shopping list for 500 shekels"

Step 1: Parse Query
  ├─ Budget: 500 shekels
  ├─ Categories: all
  └─ Build optimized list: [Tomatoes, Milk, Lentils, Chickpeas, Bread, Yogurt, ...]

Step 2: Check Browser Session
  ├─ ~/.rami-levi-session.json not found
  ├─ Launch Playwright
  ├─ Open Chrome to https://www.rami-levy.co.il
  └─ Save session reference to config

Step 3: Search & Add Items
  For each item in list:
    ├─ Search product on rami-levy.co.il
    ├─ If found:
    │   ├─ Navigate to product URL
    │   ├─ Click "Add to Cart"
    │   ├─ Set quantity: 1
    │   ├─ Verify added
    │   └─ Track as added
    └─ If not found:
        └─ Track as missing

Step 4: Report
  ✅ Added 8 items to cart
  ❌ Missing: 1 item ("Red Lentil Flour" not found on site)
  💰 Cart total: ₪63.50
  📂 Browser session active — ready for follow-up commands
```

### Example 2: Follow-up Command

```
User: "add more organic vegetables"

Step 1: Parse Query
  ├─ Category: vegetables
  ├─ Attribute: organic
  └─ Find: [Organic Tomatoes, Organic Spinach, Organic Carrots, ...]

Step 2: Check Browser Session
  ├─ ~/.rami-levi-session.json exists
  ├─ Browser PID 12345 still running
  └─ Reuse existing browser (NO new Chrome window)

Step 3: Add Items to Existing Cart
  For each new item:
    ├─ Search on already-open browser
    ├─ Add to cart (same session)
    └─ Update cart display

Step 4: Report
  ✅ Added 2 more items
  💰 New cart total: ₪78.30
  📝 Cart now has 10 items
```

### Example 3: Cleanup

```
User: "cleanup"

Step 1: Check Session
  ├─ ~/.rami-levi-session.json found
  └─ Browser PID 12345 running

Step 2: Close Browser
  ├─ Terminate Playwright browser
  ├─ Close Chrome window
  └─ Delete session config file

Step 3: Report
  ✅ Browser closed
  ✅ Session cleaned up
```

---

## Session Config Format

**File:** `~/.rami-levi-session.json`

```json
{
  "active": true,
  "browser_pid": 12345,
  "ws_endpoint": "ws://127.0.0.1:9222/devtools/browser/abcd1234",
  "opened_at": "2026-06-28T11:30:00Z",
  "items_added": 8,
  "cart_total": 63.50,
  "last_updated": "2026-06-28T11:35:00Z",
  "last_query": "build shopping list for 500 shekels"
}
```

**Purpose:**
- Tracks which browser is currently open
- Allows follow-up invocations to reuse the session
- Persists across terminal sessions
- Can be cleaned up when user is done shopping

---

## Error Handling & Edge Cases

| Scenario | Behavior | Recovery |
|----------|----------|----------|
| Item not found on site | Skip, add to missing items list | Report in summary |
| Browser crashes | Detect via config check | Ask user to start fresh |
| Rami Levy requires login | Show login modal in browser | Ask user to authenticate, continue |
| Product out of stock | Try to add anyway | Report as failed in summary |
| Session config stale | Browser PID no longer running | Remove old config, launch new browser |
| Network error during search | Retry once | Skip item, report error |
| Quantity selector unavailable | Add with default quantity | Report item added with note |

---

## User Interface & Commands

### Command Syntax

```bash
# Build and add shopping list
/rami-levi-shopping-cart build shopping list for 500 shekels

# Add more items to existing cart (reuses browser)
/rami-levi-shopping-cart add organic vegetables

# Check current cart status
/rami-levi-shopping-cart show cart

# Close browser and cleanup
/rami-levi-shopping-cart cleanup
```

### Output Format

```
🛒 SHOPPING LIST AUTOMATION

Building list for 500 shekels...
├─ Budget: 500 shekels
├─ Items to add: 10
└─ Opening Rami Levy website...

Adding items to cart...
✅ Tomatoes - Fresh - ₪2.90
✅ Milk - 3% Mahdrin - ₪8.50
✅ Greek Yogurt - ₪9.90
✅ Cottage Cheese - ₪7.50
✅ Cheddar Cheese - ₪14.00
✅ Lentils - Red - ₪7.00
✅ Hummus - Large - ₪8.50
✅ Bread - White - ₪8.50
❌ Red Lentil Flour - Not found on website (SKIPPED)
✅ Olive Oil - Extra Virgin - ₪19.80

📊 SUMMARY
├─ Added: 9 items
├─ Missing: 1 item
├─ Cart Total: ₪86.10
└─ Browser: Open & Ready for Follow-ups
```

---

## Implementation Files

| File | Action | Purpose |
|------|--------|---------|
| `browser_manager.py` | CREATE | Browser lifecycle + session management |
| `web_scraper.py` | CREATE | Search + scrape Rami Levy website |
| `cart_automation.py` | CREATE | Playwright automation for cart ops |
| `skill_handler.py` | ENHANCE | Integrate browser, add orchestration |
| `SKILL.md` | UPDATE | Document new browser capabilities |
| `requirements.txt` | CREATE | Add Playwright, BeautifulSoup4 dependencies |
| `test_browser_integration.py` | CREATE | Tests for browser automation |

---

## Dependencies

**New packages:**
- `playwright` — Modern browser automation (replaces Selenium)
- `beautifulsoup4` — HTML parsing for scraping

**Installation:**
```bash
pip install playwright beautifulsoup4
playwright install chromium  # Download Chromium
```

---

## Testing Strategy

**Unit Tests:**
- Test browser manager (open, close, session tracking)
- Test web scraper (search, parse results, error handling)
- Test cart automation (add item, verify, error states)

**Integration Tests:**
- Full workflow: Query → Browse → Add → Verify
- Session persistence: Open browser → Close skill → Re-invoke → Reuse
- Error scenarios: Missing items, network errors, login prompts

**Manual Testing:**
- Run skill on actual Rami Levy website
- Verify items appear in live cart
- Test follow-up commands reuse same browser
- Confirm guest mode works (no login required)

---

## Success Criteria

✅ User builds shopping list → Browser opens with filled cart  
✅ Browser stays open for follow-up commands  
✅ Multiple invocations reuse same browser session  
✅ Items actually appear in Rami Levy cart  
✅ Missing items are tracked and reported  
✅ Guest mode works; login prompt shown if needed  
✅ Cleanup command closes browser and removes config  
✅ No external dependencies beyond Playwright + BeautifulSoup  

---

## Known Limitations & Future Work

**Current Phase:**
- Static product database still used for list building (can be upgraded to real-time scraping)
- Only supports Rami Levy store (not other supermarkets)
- No price tracking/historical comparisons yet

**Future Enhancements:**
- Real-time price updates from website
- Multi-store comparison
- Recipe-to-cart workflow
- User preferences/favorites
- Mobile app integration

---

## Rollout Plan

1. **Phase 1:** Implement core 3 modules (browser_manager, web_scraper, cart_automation)
2. **Phase 2:** Integrate with skill_handler, test on actual website
3. **Phase 3:** Add session persistence, follow-up command support
4. **Phase 4:** Comprehensive error handling and edge cases
5. **Phase 5:** Documentation, cleanup command, finalize

---

## References

- Playwright docs: https://playwright.dev/python/
- Rami Levy website: https://www.rami-levy.co.il/
- Session persistence pattern: Standard file-based config
