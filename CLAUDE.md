# Rami Levy Shopping Skill - Development Guidelines

## Core Principle: Skill-First Development

**All code changes must be part of the skill, not standalone scripts.**

## How to Use the Skill

### Step 1: Start Your Chrome
```bash
chrome --remote-debugging-port=9222
```

### Step 2: Use the Skill
```python
from skill_handler import ShoppingListSkill

skill = ShoppingListSkill()

# Get vegetarian family shopping list and add to cart
result = skill.shop_vegetarian_family()

print(f"Added: {result['added_count']} items")
print(f"Missing: {result['missing_count']} items")
print(f"Total: ₪{result['total_price']}")
```

## Key Implementation Details

- **Hebrew Website**: All search queries are automatically translated to Hebrew
- **Your Chrome**: Uses your existing Chrome browser session (no headless, no detection issues)
- **Persistent Session**: Your login and cart remain intact
- **Batch Operations**: Builds shopping list first, then adds all items at once

### What This Means

✅ **DO:**
- Modify `skill_handler.py` to add new features
- Add methods to `ShoppingListSkill` class
- Test via skill invocation: `/reload-skills` then run skill
- All helper modules (`web_scraper.py`, `cart_automation.py`, etc.) are imported BY the skill

❌ **DON'T:**
- Create debug scripts or test files
- Write code that runs outside skill context
- Use standalone Python scripts for testing
- Develop separate modules that aren't used by the skill

### Development Workflow

1. **Modify skill code** → Edit `skill_handler.py` or helper modules
2. **Reload skills** → `/reload-skills` to pick up changes
3. **Test via skill invocation** → Call `skill.method("query")` or use `/rami-levi-shopping-cart` command
4. **Verify results** → Check output from skill execution
5. **Commit changes** → Git commit with clear message

### Example: Adding a Feature

**WRONG:**
```python
# standalone_test.py (❌ DON'T DO THIS)
from smart_shopper import SmartShopper
shopper = SmartShopper()
shopper.search_for_products(["milk"])
```

**RIGHT:**
```python
# skill_handler.py (✅ DO THIS)
class ShoppingListSkill:
    def search_and_batch_add(self, queries: str) -> Dict:
        """Add items via smart Chrome connection."""
        queries = queries.split()
        shopper = SmartShopper()
        shopper.connect_to_chrome()
        result = shopper.search_for_products(queries)
        return shopper.batch_add_to_cart(result["shopping_list"])
```

Then test:
```bash
/reload-skills
# In skill or Python:
skill.search_and_batch_add("milk pita yogurt")
```

### File Organization

```
shopping-cart/
├── skill/                     # ⭐ THE SKILL — single, self-contained source of truth
│   ├── SKILL.md               #    Skill manifest (frontmatter: name/description/triggers)
│   ├── skill_handler.py       #    MAIN entry — ShoppingListSkill, all methods
│   ├── search_engine.py       #    Helper (imported by skill)
│   ├── formatters.py          #    Helper (imported by skill)
│   ├── rami_levy_web.py       #    Helper (imported by skill)
│   ├── browser_manager.py     #    Helper (imported by skill)
│   ├── web_scraper.py         #    Helper (imported by skill)
│   ├── cart_automation.py     #    Helper (imported by skill)
│   ├── smart_shopper.py       #    Helper (imported by skill)
│   ├── chrome_connector.py    #    Helper (imported by skill)
│   ├── rami_levy_api.py       #    Helper (imported by skill)
│   ├── rami_levy_products.json#    Product database (path-resolved relative to module)
│   └── requirements.txt       #    Runtime deps (Playwright, BeautifulSoup4)
├── dev/                       # Debug & dev-only: tests/, demos, design notes, old docs
├── docs/                      # Architecture / component / schema docs
├── install.sh                 # Sync ./skill into agent skills dirs (real dir copy)
├── README.md
└── CLAUDE.md                  # This file
```

**Everything the skill needs lives in `skill/` and nothing else does.** Tests, demos,
and scratch docs live in `dev/`. The skill is portable: `skill/` can be dropped into any
agent's skills directory as-is.

### Installing / loading the skill

The skill is **copied** (not symlinked) into the skills directories — the Claude Code
loader, which runs inside WSL, does **not** pick up symlinked skill folders:

```bash
bash install.sh            # copies ./skill -> ~/.claude/skills/rami-levi-shopping-cart
                           #           and    -> ~/.agents/skills/rami-levi-shopping-cart
```

Then restart the WSL `claude` session (or `/reload-skills`) to load it.

> Environment note: the `claude` engine runs **inside WSL** (`~/.claude` = `/home/aavitan/.claude`).
> A Windows terminal is only the client. Do all install/file ops from WSL (or `wsl bash`),
> never via Windows PowerShell symlinks — those create reparse points the Linux loader ignores.

**NO standalone test files, debug scripts, or temporary Python files in `skill/`.**

### Testing Pattern

Always test via skill:

```bash
# After modifying skill code:
/reload-skills

# Then invoke skill (in Python REPL or via /rami-levi-shopping-cart):
skill = ShoppingListSkill()
result = skill.search_and_batch_add("milk pita yogurt")
print(result)
```

### Commit Messages

Commits should reference skill features, not test scripts:

```bash
✅ git commit -m "feat: add search_and_batch_add method to skill"
✅ git commit -m "fix: improve Chrome connection detection in skill"

❌ git commit -m "test: debugging script changes"
❌ git commit -m "temp: trying something out"
```

### Key Principles

1. **Skill is the system** - Everything else supports it
2. **No standalone execution** - All code runs via skill methods
3. **Skill invocation is the test** - `/reload-skills` then call the method
4. **Clean repo** - No debug files, temp scripts, or test runners
5. **Clear integration** - Every module has a clear purpose in the skill

### Current Skill Methods

- `process_query()` - Search local database
- `process_query_with_browser()` - Automation with browser
- `open_persistent_browser()` - Start persistent Chrome session
- `continue_shopping()` - Add items with persistent browser
- `stop_shopping()` - Close browser
- `verify_cart_contents()` - Check cart contents

### Next: Implement in Skill

- `search_and_batch_add()` - Use SmartShopper with Chrome connector
- All SmartShopper functionality must be integrated into skill methods

---

**Remember: If it's not callable via the skill, it doesn't belong in the repo.**
