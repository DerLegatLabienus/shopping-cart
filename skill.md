# Rami Levy Shopping Assistant Skill

Automate shopping on Rami Levy supermarket with live browser automation, or guide you manually through adding items with automatic verification. Search real products, build optimized budgets, and verify items in your live shopping cart.

**NEW:** Browser automation mode opens Chrome, searches products, adds items automatically, and fills your cart in real-time!

---

## What This Skill Does

### 🌐 Browser Automation Mode (NEW)
This skill can now automate your entire shopping experience:
1. **Open Chrome** - Opens Rami Levy website in a visible browser window
2. **Search products** - Automatically web scrapes real products and prices
3. **Add to cart** - Adds items directly to your live shopping cart
4. **Verify items** - Confirms each item actually added to the site
5. **Keep browser open** - Session persists across multiple commands
6. **Track missing items** - Reports which products couldn't be found
7. **Cleanup** - Close browser and cleanup session when done

### 📋 Manual Guided Mode
Or use the traditional step-by-step approach:
1. **Find products** - Search Rami Levy's vegetarian catalog
2. **Plan shopping list** - Build optimized lists within your budget
3. **Guide you through adding** - Tell you what to click and where
4. **Verify items** - Track what you've added and confirm they're in cart
5. **Refine list** - Help you adjust quantities and items as needed

---

## How to Use

### 🌐 Browser Automation Mode (NEW)

**Fully Automated Shopping - Browser opens and fills your cart automatically!**

**User:** "Build shopping list for ₪500 vegetarian and add to cart automatically"

**Skill Response:**
- Opens visible Chrome window on Rami Levy website
- Searches for each product on the real website
- Adds items directly to your live shopping cart
- Verifies each item is actually in the cart
- Reports results with cart total
- Browser stays open for further commands

**To close when done:**
- Simply say: "Close the browser" or "Cleanup browser session"

---

### 📋 Manual Guided Mode

For when you prefer to shop yourself or want step-by-step guidance:

#### Simple Usage

**User:** "I want to shop for ₪500 vegetarian items on Rami Levy"

**Skill Response:**
- Generates optimized shopping list
- Shows step-by-step workflow
- For each item: tells you what to search for and click

**Then for each item:**

**User:** "Added Red Lentils to cart"

**Skill Response:**
- ✅ Verifies it's tracked
- Asks you to confirm you see it in the cart
- Moves to next item

---

## Example Conversation

```
User: "Help me shop for vegetables and legumes, around ₪500"

Skill: "Perfect! I'll build you a shopping list. Here's what we'll add:

🛒 Your Shopping List:
1. Red Lentils 1kg - ₪13.80
2. Fresh Tomatoes (2kg) - ₪5.80
3. Cucumber (1kg) - ₪2.90
4. Yellow Onion (2kg) - ₪7.00
5. Milk 1L (2x) - ₪17.00
... (more items)

**Next Step:** Go to Rami Levy website and search for 'Red Lentils'
When you find it, click 'Add to Cart' and let me know"

---

User: "I added red lentils"

Skill: "Great! ✅ Red Lentils is now tracked.
Can you confirm you see it in your shopping cart at the top of the website?
(Just tell me 'yes' or 'no')"

---

User: "Yes, I see it"

Skill: "Perfect! ✅ Red Lentils verified.

**Next item:** Fresh Tomatoes
Search for 'עגבניה' or 'tomatoes' in the fresh vegetables section
Add 2kg and let me know when done"

... (continues for all items)
```

---

## Browser Integration (NEW)

### ✨ New Automated Features

This skill now integrates with browser automation via Playwright to handle live shopping on rami-levy.co.il:

#### 🖥️ Open Chrome
- Launches visible Chrome window
- Navigates to Rami Levy website
- Keeps browser open across multiple commands
- Full visibility of all automation steps

#### 🔍 Product Search
- Web scrapes real Rami Levy products and prices
- Searches for each item on the live website
- Matches products by name (Hebrew and English)
- Returns actual prices, not cached data

#### 🛒 Automatic Add to Cart
- Adds items directly to live shopping cart
- Sets quantities automatically
- Confirms each addition to the site
- All changes visible in browser

#### ✅ Cart Verification
- Confirms items appear in live cart
- Checks product names and prices
- Validates quantities match requests
- Reports verification status for each item

#### 🌐 Session Persistence
- Browser stays open between commands
- Continue shopping without restarting
- Session data stored in ~/.rami-levi-session.json
- All progress maintained across requests

#### 👤 Guest Mode
- Works without login to Rami Levy
- Prompts if authentication needed
- Cart accessible as guest user
- No account required

#### 📊 Missing Items Report
- Tracks products that couldn't be found
- Reports which items failed to add
- Suggests alternatives for missing products
- Summary at end of shopping session

#### 🧹 Browser Cleanup
- Command: "Close the browser" or "Cleanup browser session"
- Closes Chrome window cleanly
- Removes session data
- Frees system resources

### 📋 Browser Session Management

All browser automation is managed locally through a Playwright instance:

- **Session config:** `~/.rami-levi-session.json` stores session state
- **Browser reusable:** Same browser instance across commands
- **Auto-cleanup:** Sessions cleaned up on user request
- **Local automation:** All actions run locally via Playwright
- **No remote calls:** Browser control stays on your machine

---

## Query Types

### Type 1: Build Shopping List

```
"Create a shopping list for ₪300 vegetarian"
→ Shows items + shopping workflow

"I need vegetables for the week, around ₪200"
→ Finds vegetables within budget

"Shopping list with legumes, dairy, and grains - ₪500"
→ Multi-category list
```

### Type 2: Search for Product

```
"Find lentils on Rami Levy"
→ Shows all lentil products with prices

"What vegetarian options are under ₪10?"
→ Searches by price

"Show me organic products"
→ Filters for organic items
```

### Type 3: Add to Cart

```
"I added Red Lentils to the cart"
→ Tracks it + asks for verification

"Just added milk and eggs"
→ Tracks multiple items

"I couldn't find the tomatoes"
→ Suggests alternatives or search tips
```

### Type 4: Verify Cart

```
"Can you check what I've added so far?"
→ Shows all tracked items + which are verified

"Is the milk in my cart?"
→ Checks if tracked item is verified

"What's my cart total?"
→ Calculates estimated total
```

---

## Example Workflows

### Workflow 1: Live Shopping with Browser Automation

Complete automated shopping experience with real-time browser updates.

**User:** "Build shopping list for ₪500 and add to cart automatically"

**Process:**
1. Skill parses budget and constraints
2. Opens Chrome on Rami Levy website
3. For each item:
   - Searches website for product
   - Adds to cart automatically
   - Verifies in live cart
4. Reports final cart total and status

**Result:**
- Browser stays open showing filled cart
- All items verified as added
- Ready to proceed to checkout
- Browser available for additional commands

---

### Workflow 2: Continue Shopping (Browser Reuse)

Reuse the same browser session from previous command.

**Context:** Browser still open from Workflow 1

**User:** "Add more organic vegetables, around ₪100"

**Process:**
1. Reuses same browser session
2. Searches for organic vegetable products
3. Adds new items to existing cart
4. Updates cart total

**Result:**
- Same browser window updated
- Cart total now reflects new items
- Can continue adding more items
- No need to restart browser

---

### Workflow 3: Search Only (No Add)

Find products without automatic adding.

**User:** "What organic lentils are available?"

**Process:**
1. Opens browser
2. Searches for organic lentils
3. Shows results with prices
4. Does NOT add to cart

**Result:**
- See all available products
- Prices and descriptions visible
- Choose whether to add manually or use auto-add

---

### Workflow 4: Manual Shopping with Guidance

Original step-by-step guided approach without automation.

**User:** "Guide me through shopping for ₪300 dairy and grains"

**Process:**
1. Generates shopping list
2. For each item, tells you where to click
3. You perform clicks manually
4. You report when added
5. Skill verifies based on your confirmation

**Result:**
- Full control over shopping
- Step-by-step guidance
- Verification through your reports

---

## Step-by-Step Workflow (Manual Mode)

### For each item you add:

1. **I tell you what to search for**
   - Product name
   - Category hint
   - Quantity needed

2. **You find it on Rami Levy website**
   - Use search bar or browse category
   - Note the price to verify

3. **You click "Add to Cart"**
   - Set quantity if needed
   - Click add button

4. **You tell me you added it**
   - Example: "Added Red Lentils"

5. **I ask you to verify**
   - "Can you see it in your cart?"
   - You confirm: "Yes" or "No"

6. **I track the verification**
   - ✅ Marked as verified
   - Or ❌ I help you fix it

---

## Cart Verification Examples

### Successful Verification

```
You: "I added the tomatoes"
Skill: "✅ Tracked! Can you see 'עגבניה / Tomatoes' in your cart?"
You: "Yes, it shows ₪5.80"
Skill: "✅ Perfect! Tomatoes verified in cart"
```

### Item Not Found

```
You: "I added the tomatoes"
Skill: "✅ Tracked! Can you see 'עגבניה / Tomatoes' in your cart?"
You: "No, I don't see it"
Skill: "❌ Tomatoes not showing in cart.

Let's try again:
1. Go back to Fresh Vegetables section
2. Search for 'עגבניה' (Hebrew for tomato)
3. Select the regular fresh tomatoes
4. Click the + button or Add to Cart
5. Set quantity to 3.5kg
6. Let me know when it's added"
```

---

## Key Features

### ✅ Verification System
Every item is verified by checking your actual cart. No ghost items!

### 📋 Budget Tracking
Real-time tracking of your total as items are added.

### 🔍 Smart Search
Helps you find products even if you don't know Hebrew names.

### 📝 Shopping Workflow
Step-by-step guidance for each item.

### 💾 Progress Tracking
Keeps track of what's verified vs. still needs adding.

---

## Supported Categories

- Vegetables (fresh)
- Legumes & Beans
- Dairy & Eggs
- Grains & Pasta
- Pantry Staples
- Bread & Baked Goods
- Frozen Items
- Organic Products

---

## Tips for Success

1. **Use the search bar** - Fastest way to find items
2. **Follow my Hebrew names** - I'll give exact names to search
3. **Confirm in cart** - Always check you see it in your cart
4. **Report quantities** - Tell me if quantity is different
5. **Ask for help** - Tell me if you can't find something

---

## What Happens After?

Once you've added and verified all items:

- ✅ Complete cart ready to review
- 💰 Total price calculated
- 📊 Summary of all items
- 🛒 Ready to proceed to checkout on website

---

## Constraints & Pitfalls

### With Browser Automation
- **Real-time product search** via web scraping - prices and availability subject to change
- **Live shopping cart** on rami-levy.co.il - browser must stay open during automation
- **Browser window management** via Playwright - requires visible Chrome window
- **Session persistence** - browser reusable but must be explicitly closed
- **Network dependent** - requires stable internet for web scraping

### General Constraints
- **Prices vary** by location and time on Rami Levy
- **Limited product sizes** - some items may only be available in specific quantities
- **Real-time inventory** - stock levels not checked; items may be out of stock during checkout
- **Budget approximation** - final total may vary based on available products
- **Vegetarian database** - curated from known Rami Levy catalog

---

## Example Full Conversation

See `CART_MANAGEMENT_FEATURE.md` for detailed walkthrough.

---

**Key Idea:** This skill turns shopping on Rami Levy into a guided, verified process. You browse the website, I help you find items and confirm they're actually in your cart. No more mystery about what's been added!
