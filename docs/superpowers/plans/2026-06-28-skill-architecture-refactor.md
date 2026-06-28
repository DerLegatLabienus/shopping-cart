# Skill Architecture Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decompose `skill/skill_handler.py` (1,496 lines) into focused modules with a formal `Store` ABC so the core skill has zero knowledge of Rami Levy.

**Architecture:** A `Store` ABC defines the contract (`search`, `add_to_cart`, `get_cart`, `verify_cart`). `RamiLevyStore` implements it, owning all browser modules and a TTL-based `ProductCache`. `ShoppingListSkill` is injected with a `Store` at construction — it never imports Rami Levy directly. `QueryParser` and `CartManager` are extracted from `skill_handler.py`.

**Tech Stack:** Python 3.8+, dataclasses, abc, unittest.mock (tests only), Playwright (browser layer — unchanged)

## Global Constraints

- All skill code lives in `skill/` — no files outside that directory
- Tests live in `dev/tests/` — existing test files must not be broken
- `formatters.py`, `search_engine.py`, and all browser modules (`browser_manager.py`, `chrome_connector.py`, `web_scraper.py`, `cart_automation.py`, `smart_shopper.py`, `rami_levy_web.py`) must not be modified
- `rami_levy_products.json` stays at `skill/rami_levy_products.json` — `ProductCache` adds a `_cache_updated_at` key to the top-level JSON object, no other format changes
- The website cart is always the source of truth — `verify_cart()` must read from the live site, never from local state
- `skill_handler.py` must have zero imports of `RamiLevyStore` or any Rami Levy module after refactor
- Every new module must stay under 300 lines
- Python imports inside `skill/` use bare module names (e.g. `from store import Product`) — no relative imports

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `skill/store.py` | **Create** | Store ABC + Product, CartItem, Cart, SearchFilters dataclasses |
| `skill/product_cache.py` | **Create** | JSON cache with TTL; transparent to callers above it |
| `skill/query_parser.py` | **Create** | NL query → SearchFilters; extracted from skill_handler.py |
| `skill/cart_manager.py` | **Create** | Local session cart state; extracted from skill_handler.py |
| `skill/rami_levy_store.py` | **Create** | RamiLevyStore(Store) — wraps browser modules + cache |
| `skill/skill_handler.py` | **Rewrite** | Thin orchestrator; injected with Store; ~150 lines |
| `dev/tests/test_store.py` | **Create** | Tests for store.py dataclasses |
| `dev/tests/test_product_cache.py` | **Create** | Tests for product_cache.py |
| `dev/tests/test_query_parser.py` | **Create** | Tests for query_parser.py |
| `dev/tests/test_cart_manager.py` | **Create** | Tests for cart_manager.py |
| `dev/tests/test_rami_levy_store.py` | **Create** | Tests for rami_levy_store.py (mocks browser) |
| `dev/tests/test_skill_handler.py` | **Create** | Tests for skill_handler.py (mocks Store) |
| `skill/rami_levy_api.py` | **Delete** | Absorbed into rami_levy_store.py |

---

### Task 1: `store.py` — Data Types and Store ABC

**Files:**
- Create: `skill/store.py`
- Create: `dev/tests/test_store.py`

**Interfaces:**
- Produces: `Product`, `CartItem`, `Cart`, `SearchFilters`, `Store` — used by every subsequent task

- [ ] **Step 1: Write the failing tests**

Create `dev/tests/test_store.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skill'))

from store import Product, CartItem, Cart, SearchFilters, Store
from abc import ABC


def _product(pid="p1", price=7.0) -> Product:
    return Product(id=pid, name="Red Lentils", category="legumes",
                   price=price, attributes=["vegan"], size="500g", brand="RL")


def test_cart_total_sums_price_times_quantity():
    cart = Cart(items=[
        CartItem(product=_product("p1", 7.0), quantity=2),
        CartItem(product=_product("p2", 5.0), quantity=1),
    ])
    assert cart.total == 19.0


def test_cart_total_empty():
    assert Cart(items=[]).total == 0.0


def test_cart_item_defaults_unverified():
    item = CartItem(product=_product(), quantity=1)
    assert item.verified is False


def test_search_filters_defaults():
    f = SearchFilters()
    assert f.keywords == []
    assert f.categories == []
    assert f.attributes == []
    assert f.max_price is None
    assert f.min_price is None


def test_store_is_abstract():
    assert issubclass(Store, ABC)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/aavitan/claude-projects/shopping-cart
python -m pytest dev/tests/test_store.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'store'`

- [ ] **Step 3: Create `skill/store.py`**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Product:
    id: str
    name: str
    category: str
    price: float
    attributes: List[str]
    size: str
    brand: str


@dataclass
class CartItem:
    product: Product
    quantity: int
    verified: bool = False


@dataclass
class Cart:
    items: List[CartItem] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(i.product.price * i.quantity for i in self.items)


@dataclass
class SearchFilters:
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    attributes: List[str] = field(default_factory=list)


class Store(ABC):
    @abstractmethod
    def search(self, filters: SearchFilters) -> List[Product]: ...

    @abstractmethod
    def add_to_cart(self, product_id: str, quantity: int = 1) -> CartItem: ...

    @abstractmethod
    def get_cart(self) -> Cart: ...

    @abstractmethod
    def verify_cart(self) -> Dict[str, bool]: ...
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest dev/tests/test_store.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add skill/store.py dev/tests/test_store.py
git commit -m "feat: add Store ABC and shared data types"
```

---

### Task 2: `product_cache.py` — TTL Cache

**Files:**
- Create: `skill/product_cache.py`
- Create: `dev/tests/test_product_cache.py`

**Interfaces:**
- Consumes: nothing from this project (stdlib only)
- Produces:
  - `ProductCache(path: str, ttl_seconds: int = 3600)`
  - `.get_all() -> Optional[List[Dict]]` — None if stale/missing
  - `.set_all(products: List[Dict]) -> None`
  - `.refresh(fetcher: Callable[[], List[Dict]]) -> List[Dict]]`
  - `.is_stale: bool`
  - `.age_seconds: Optional[float]`

- [ ] **Step 1: Write the failing tests**

Create `dev/tests/test_product_cache.py`:

```python
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skill'))

import pytest
from product_cache import ProductCache


PRODUCTS = [{"id": "p1", "name": "Lentils", "sizes": [{"price": 7.0}]}]


def test_stale_when_file_missing(tmp_path):
    cache = ProductCache(str(tmp_path / "nope.json"))
    assert cache.is_stale
    assert cache.age_seconds is None
    assert cache.get_all() is None


def test_stale_when_old_timestamp(tmp_path):
    path = str(tmp_path / "cache.json")
    with open(path, "w") as f:
        json.dump({"products": PRODUCTS, "_cache_updated_at": time.time() - 7200}, f)
    cache = ProductCache(path, ttl_seconds=3600)
    assert cache.is_stale
    assert cache.get_all() is None


def test_fresh_returns_products(tmp_path):
    path = str(tmp_path / "cache.json")
    cache = ProductCache(path)
    cache.set_all(PRODUCTS)
    result = cache.get_all()
    assert result == PRODUCTS


def test_set_all_preserves_existing_keys(tmp_path):
    path = str(tmp_path / "cache.json")
    with open(path, "w") as f:
        json.dump({"products": [], "other_key": "value"}, f)
    cache = ProductCache(path)
    cache.set_all(PRODUCTS)
    with open(path) as f:
        data = json.load(f)
    assert data["other_key"] == "value"
    assert data["products"] == PRODUCTS


def test_refresh_calls_fetcher_and_updates_cache(tmp_path):
    path = str(tmp_path / "cache.json")
    called = []
    def fetcher():
        called.append(True)
        return PRODUCTS
    cache = ProductCache(path)
    result = cache.refresh(fetcher)
    assert result == PRODUCTS
    assert len(called) == 1
    assert cache.get_all() == PRODUCTS


def test_age_seconds_is_reasonable(tmp_path):
    path = str(tmp_path / "cache.json")
    cache = ProductCache(path)
    cache.set_all(PRODUCTS)
    assert 0 <= cache.age_seconds < 5
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest dev/tests/test_product_cache.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'product_cache'`

- [ ] **Step 3: Create `skill/product_cache.py`**

```python
import json
import os
import time
from typing import Callable, Dict, List, Optional


class ProductCache:
    def __init__(self, path: str, ttl_seconds: int = 3600):
        self.path = path
        self.ttl_seconds = ttl_seconds

    @property
    def is_stale(self) -> bool:
        age = self.age_seconds
        return age is None or age > self.ttl_seconds

    @property
    def age_seconds(self) -> Optional[float]:
        data = self._read_raw()
        if data is None or "_cache_updated_at" not in data:
            return None
        return time.time() - data["_cache_updated_at"]

    def get_all(self) -> Optional[List[Dict]]:
        if self.is_stale:
            return None
        data = self._read_raw()
        return data.get("products") if data else None

    def set_all(self, products: List[Dict]) -> None:
        data = self._read_raw() or {}
        data["products"] = products
        data["_cache_updated_at"] = time.time()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def refresh(self, fetcher: Callable[[], List[Dict]]) -> List[Dict]:
        products = fetcher()
        self.set_all(products)
        return products

    def _read_raw(self) -> Optional[Dict]:
        if not os.path.exists(self.path):
            return None
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest dev/tests/test_product_cache.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add skill/product_cache.py dev/tests/test_product_cache.py
git commit -m "feat: add ProductCache with TTL support"
```

---

### Task 3: `query_parser.py` — Natural Language → SearchFilters

**Files:**
- Create: `skill/query_parser.py`
- Create: `dev/tests/test_query_parser.py`

**Interfaces:**
- Consumes: `SearchFilters` from `store.py`
- Produces:
  - `QueryParser()`
  - `.parse(query: str) -> SearchFilters`
  - `.needs_clarification(query: str) -> List[str]`
  - `.is_buy_intent(query: str) -> bool`

- [ ] **Step 1: Write the failing tests**

Create `dev/tests/test_query_parser.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skill'))

from query_parser import QueryParser


def test_parse_budget_under():
    f = QueryParser().parse("lentils under 20 shekels")
    assert f.max_price == 20.0
    assert f.min_price == 0.0


def test_parse_budget_range():
    f = QueryParser().parse("vegetables 50-100")
    assert f.min_price == 50.0
    assert f.max_price == 100.0


def test_parse_no_budget():
    f = QueryParser().parse("show me lentils")
    assert f.min_price is None
    assert f.max_price is None


def test_parse_category_direct():
    f = QueryParser().parse("show me vegetables")
    assert "vegetables" in f.categories


def test_parse_category_alias_lentils():
    f = QueryParser().parse("I want some lentils and beans")
    assert "legumes" in f.categories


def test_parse_category_alias_veggies():
    f = QueryParser().parse("fresh veggies please")
    assert "vegetables" in f.categories


def test_parse_attributes_vegan():
    f = QueryParser().parse("vegan products under 30")
    assert "vegan" in f.attributes


def test_parse_attributes_organic():
    f = QueryParser().parse("organic bread")
    assert "organic" in f.attributes


def test_parse_keywords_extracted():
    f = QueryParser().parse("chickpeas under 15 shekels")
    assert "chickpeas" in f.keywords


def test_needs_clarification_no_category_no_budget():
    q = QueryParser().needs_clarification("give me stuff")
    assert any("categor" in s.lower() for s in q)
    assert any("budget" in s.lower() for s in q)


def test_needs_clarification_full_query_asks_format():
    q = QueryParser().needs_clarification("vegan vegetables under 50")
    assert len(q) == 1
    assert "format" in q[0].lower()


def test_is_buy_intent_true():
    assert QueryParser().is_buy_intent("add milk to cart")
    assert QueryParser().is_buy_intent("buy chickpeas")


def test_is_buy_intent_false():
    assert not QueryParser().is_buy_intent("show me lentils")
    assert not QueryParser().is_buy_intent("what vegetables do you have")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest dev/tests/test_query_parser.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'query_parser'`

- [ ] **Step 3: Create `skill/query_parser.py`**

```python
import re
from typing import List, Optional, Tuple
from store import SearchFilters


class QueryParser:
    AVAILABLE_CATEGORIES = [
        "bread", "condiments", "dairy", "frozen", "fruits",
        "grains", "legumes", "organic", "pantry", "vegetables",
    ]
    CATEGORY_ALIASES = {
        "vegetables": ["veggies", "produce", "fresh"],
        "legumes": ["beans", "lentils", "chickpeas", "peas", "pulses"],
        "grains": ["rice", "pasta", "couscous"],
        "dairy": ["milk", "cheese", "yogurt", "butter", "eggs"],
        "fruits": ["fruit", "apple", "banana", "orange"],
    }
    DIETARY_TERMS = ["vegan", "organic", "kosher", "ready-to-eat"]
    BUY_KEYWORDS = [
        "קנה", "קנו", "קניה", "buy", "purchase", "shop",
        "add", "cart", "נקנה", "בוא נקנה", "בואו נקנה",
    ]
    _STOP_WORDS = {
        "the", "a", "an", "and", "or", "for", "with", "please",
        "shekels", "shekel", "under", "below", "less", "than",
        "list", "shopping", "products", "show", "me", "want",
        "some", "give", "get",
    }

    def parse(self, query: str) -> SearchFilters:
        q = query.lower()
        min_p, max_p = self._parse_budget(q)
        return SearchFilters(
            keywords=self._extract_keywords(q),
            categories=self._extract_categories(q),
            min_price=min_p,
            max_price=max_p,
            attributes=self._extract_attributes(q),
        )

    def needs_clarification(self, query: str) -> List[str]:
        q = query.lower()
        questions = []
        if not self._extract_categories(q):
            questions.append("📂 Which categories? (e.g., vegetables, legumes, dairy)")
        if self._parse_budget(q)[1] is None:
            questions.append("💰 Do you have a budget? (e.g., under 50 shekels, 100-200)")
        if not self._extract_attributes(q):
            questions.append("🌱 Any dietary preferences? (vegan, organic, kosher)")
        if not questions:
            questions.append("📋 What format? (markdown, JSON, CSV)")
        return questions

    def is_buy_intent(self, query: str) -> bool:
        q = query.lower()
        return any(kw in q for kw in self.BUY_KEYWORDS)

    def _parse_budget(self, q: str) -> Tuple[Optional[float], Optional[float]]:
        if any(w in q for w in ("under", "below", "less")):
            words = q.split()
            for i, word in enumerate(words):
                if word in ("under", "below", "less") and i + 1 < len(words):
                    try:
                        amount = float("".join(c for c in words[i + 1] if c.isdigit() or c == "."))
                        if amount > 0:
                            return (0.0, amount)
                    except ValueError:
                        pass
        m = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", q)
        if m:
            lo, hi = float(m.group(1)), float(m.group(2))
            if lo > 0 and hi > 0:
                return (lo, hi)
        return (None, None)

    def _extract_categories(self, q: str) -> List[str]:
        matched = [c for c in self.AVAILABLE_CATEGORIES if c in q or c.replace("_", " ") in q]
        for cat, aliases in self.CATEGORY_ALIASES.items():
            if cat not in matched and any(a in q for a in aliases):
                if cat in self.AVAILABLE_CATEGORIES:
                    matched.append(cat)
        return list(dict.fromkeys(matched))

    def _extract_attributes(self, q: str) -> List[str]:
        return [t for t in self.DIETARY_TERMS if t in q]

    def _extract_keywords(self, q: str) -> List[str]:
        stop = self._STOP_WORDS | set(self.BUY_KEYWORDS)
        return [w for w in q.split() if w not in stop and len(w) > 2]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest dev/tests/test_query_parser.py -v
```

Expected: 13 passed

- [ ] **Step 5: Commit**

```bash
git add skill/query_parser.py dev/tests/test_query_parser.py
git commit -m "feat: add QueryParser, extracted from skill_handler"
```

---

### Task 4: `cart_manager.py` — Local Session Cart

**Files:**
- Create: `skill/cart_manager.py`
- Create: `dev/tests/test_cart_manager.py`

**Interfaces:**
- Consumes: `CartItem`, `Cart`, `Product` from `store.py`
- Produces:
  - `CartManager()`
  - `.add(item: CartItem) -> None` — merges quantity if product already present
  - `.remove(product_id: str) -> bool`
  - `.get() -> Cart`
  - `.mark_verified(product_id: str) -> None`
  - `.mark_unverified(product_id: str) -> None`
  - `.clear() -> None`

- [ ] **Step 1: Write the failing tests**

Create `dev/tests/test_cart_manager.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skill'))

from cart_manager import CartManager
from store import CartItem, Product


def _product(pid="p1", price=7.0) -> Product:
    return Product(id=pid, name="Lentils", category="legumes",
                   price=price, attributes=[], size="500g", brand="RL")


def test_add_single_item():
    mgr = CartManager()
    mgr.add(CartItem(product=_product(), quantity=1))
    assert len(mgr.get().items) == 1


def test_add_same_product_merges_quantity():
    mgr = CartManager()
    p = _product()
    mgr.add(CartItem(product=p, quantity=1))
    mgr.add(CartItem(product=p, quantity=3))
    cart = mgr.get()
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 4


def test_add_different_products():
    mgr = CartManager()
    mgr.add(CartItem(product=_product("p1"), quantity=1))
    mgr.add(CartItem(product=_product("p2"), quantity=1))
    assert len(mgr.get().items) == 2


def test_remove_existing_item():
    mgr = CartManager()
    mgr.add(CartItem(product=_product("p1"), quantity=1))
    result = mgr.remove("p1")
    assert result is True
    assert len(mgr.get().items) == 0


def test_remove_nonexistent_returns_false():
    mgr = CartManager()
    assert mgr.remove("nope") is False


def test_mark_verified():
    mgr = CartManager()
    mgr.add(CartItem(product=_product(), quantity=1))
    mgr.mark_verified("p1")
    assert mgr.get().items[0].verified is True


def test_mark_unverified():
    mgr = CartManager()
    mgr.add(CartItem(product=_product(), quantity=1, verified=True))
    mgr.mark_unverified("p1")
    assert mgr.get().items[0].verified is False


def test_clear_empties_cart():
    mgr = CartManager()
    mgr.add(CartItem(product=_product("p1"), quantity=1))
    mgr.add(CartItem(product=_product("p2"), quantity=1))
    mgr.clear()
    assert len(mgr.get().items) == 0


def test_cart_total_via_get():
    mgr = CartManager()
    mgr.add(CartItem(product=_product("p1", 7.0), quantity=2))
    mgr.add(CartItem(product=_product("p2", 5.0), quantity=1))
    assert mgr.get().total == 19.0


def test_mark_verified_unknown_product_is_noop():
    mgr = CartManager()
    mgr.mark_verified("unknown")  # must not raise
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest dev/tests/test_cart_manager.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'cart_manager'`

- [ ] **Step 3: Create `skill/cart_manager.py`**

```python
from typing import Dict
from store import Cart, CartItem


class CartManager:
    def __init__(self):
        self._items: Dict[str, CartItem] = {}

    def add(self, item: CartItem) -> None:
        existing = self._items.get(item.product.id)
        if existing:
            existing.quantity += item.quantity
        else:
            self._items[item.product.id] = item

    def remove(self, product_id: str) -> bool:
        if product_id not in self._items:
            return False
        del self._items[product_id]
        return True

    def get(self) -> Cart:
        return Cart(items=list(self._items.values()))

    def mark_verified(self, product_id: str) -> None:
        if product_id in self._items:
            self._items[product_id].verified = True

    def mark_unverified(self, product_id: str) -> None:
        if product_id in self._items:
            self._items[product_id].verified = False

    def clear(self) -> None:
        self._items.clear()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest dev/tests/test_cart_manager.py -v
```

Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add skill/cart_manager.py dev/tests/test_cart_manager.py
git commit -m "feat: add CartManager, extracted from skill_handler"
```

---

### Task 5: `rami_levy_store.py` — RamiLevyStore(Store)

**Files:**
- Create: `skill/rami_levy_store.py`
- Delete: `skill/rami_levy_api.py` (absorbed)
- Create: `dev/tests/test_rami_levy_store.py`

**Interfaces:**
- Consumes: `Store`, `Product`, `CartItem`, `Cart`, `SearchFilters` from `store.py`; `ProductCache` from `product_cache.py`; `SearchEngine` from `search_engine.py`; `SmartShopper` from `smart_shopper.py`
- Produces:
  - `RamiLevyStore(cache_path: Optional[str] = None, cache_ttl: int = 3600)`
  - Implements all four `Store` abstract methods
  - `._to_product(raw: Dict) -> Product` (static, tested directly)

- [ ] **Step 1: Write the failing tests**

Create `dev/tests/test_rami_levy_store.py`:

```python
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skill'))

import pytest
from unittest.mock import MagicMock, patch
from rami_levy_store import RamiLevyStore
from store import SearchFilters, Product


SAMPLE_PRODUCTS = [
    {
        "id": "p1", "name": "Red Lentils", "category": "legumes",
        "brand": "RL", "sizes": [{"size": "500g", "price": 7.0}],
        "attributes": ["vegan", "vegetarian"], "organic": False,
    },
    {
        "id": "p2", "name": "Chickpeas", "category": "legumes",
        "brand": "RL", "sizes": [{"size": "400g", "price": 9.5}],
        "attributes": ["vegan", "kosher"], "organic": False,
    },
]


def _fresh_cache(tmp_path):
    path = str(tmp_path / "products.json")
    with open(path, "w") as f:
        json.dump({"products": SAMPLE_PRODUCTS, "_cache_updated_at": time.time()}, f)
    return path


def test_to_product_converts_raw_dict():
    raw = SAMPLE_PRODUCTS[0]
    p = RamiLevyStore._to_product(raw)
    assert isinstance(p, Product)
    assert p.id == "p1"
    assert p.price == 7.0
    assert p.size == "500g"
    assert "vegan" in p.attributes


def test_to_product_empty_sizes():
    raw = {"id": "p9", "name": "X", "category": "other", "brand": "B",
           "sizes": [], "attributes": [], "organic": False}
    p = RamiLevyStore._to_product(raw)
    assert p.price == 0.0
    assert p.size == ""


def test_search_returns_products_from_fresh_cache(tmp_path):
    store = RamiLevyStore(cache_path=_fresh_cache(tmp_path))
    results = store.search(SearchFilters(keywords=["lentils"]))
    assert any(p.id == "p1" for p in results)


def test_search_by_category(tmp_path):
    store = RamiLevyStore(cache_path=_fresh_cache(tmp_path))
    results = store.search(SearchFilters(categories=["legumes"]))
    assert len(results) == 2


def test_search_calls_fetcher_on_stale_cache(tmp_path):
    path = str(tmp_path / "products.json")
    with open(path, "w") as f:
        json.dump({"products": SAMPLE_PRODUCTS, "_cache_updated_at": time.time() - 7200}, f)
    store = RamiLevyStore(cache_path=path, cache_ttl=3600)
    # _fetch_from_site falls back to the JSON file itself — still returns products
    results = store.search(SearchFilters())
    assert len(results) == 2


def test_add_to_cart_raises_for_unknown_product(tmp_path):
    store = RamiLevyStore(cache_path=_fresh_cache(tmp_path))
    with patch.object(store, '_get_shopper'):
        with pytest.raises(ValueError, match="Product not found"):
            store.add_to_cart("nonexistent")


def test_add_to_cart_returns_cart_item(tmp_path):
    store = RamiLevyStore(cache_path=_fresh_cache(tmp_path))
    mock_shopper = MagicMock()
    mock_shopper.search_for_products.return_value = {"success": True, "shopping_list": []}
    with patch.object(store, '_get_shopper', return_value=mock_shopper):
        item = store.add_to_cart("p1", quantity=2)
    assert item.product.id == "p1"
    assert item.quantity == 2
    mock_shopper.search_for_products.assert_called_once_with(["Red Lentils"])


def test_get_cart_returns_empty_when_no_shopper(tmp_path):
    store = RamiLevyStore(cache_path=_fresh_cache(tmp_path))
    mock_shopper = MagicMock()
    mock_shopper.page = None
    with patch.object(store, '_get_shopper', return_value=mock_shopper):
        cart = store.get_cart()
    assert cart.items == []


def test_verify_cart_returns_dict_of_bools(tmp_path):
    store = RamiLevyStore(cache_path=_fresh_cache(tmp_path))
    mock_shopper = MagicMock()
    mock_shopper.page = None
    with patch.object(store, '_get_shopper', return_value=mock_shopper):
        result = store.verify_cart()
    assert isinstance(result, dict)
    assert all(isinstance(v, bool) for v in result.values())
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest dev/tests/test_rami_levy_store.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'rami_levy_store'`

- [ ] **Step 3: Create `skill/rami_levy_store.py`**

```python
import json
import os
from typing import Dict, List, Optional

from product_cache import ProductCache
from search_engine import SearchEngine
from store import Cart, CartItem, Product, SearchFilters, Store


class RamiLevyStore(Store):
    def __init__(self, cache_path: Optional[str] = None, cache_ttl: int = 3600):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        path = cache_path or os.path.join(module_dir, "rami_levy_products.json")
        self.cache = ProductCache(path, ttl_seconds=cache_ttl)
        self.search_engine = SearchEngine(path)
        self._shopper = None

    def search(self, filters: SearchFilters) -> List[Product]:
        raw = self.cache.get_all()
        if raw is None:
            raw = self._fetch_from_site()
            self.cache.set_all(raw)
        products, _ = self.search_engine.advanced_search(
            name_query=" ".join(filters.keywords),
            categories=filters.categories or None,
            min_price=filters.min_price or 0,
            max_price=filters.max_price or float("inf"),
            attributes=filters.attributes or None,
        )
        return [self._to_product(p) for p in products]

    def add_to_cart(self, product_id: str, quantity: int = 1) -> CartItem:
        raw = self.search_engine.get_product_by_id(product_id)
        if not raw:
            raise ValueError(f"Product not found: {product_id}")
        shopper = self._get_shopper()
        shopper.search_for_products([raw["name"]])
        return CartItem(product=self._to_product(raw), quantity=quantity)

    def get_cart(self) -> Cart:
        shopper = self._get_shopper()
        if not shopper.page:
            return Cart(items=[])
        try:
            shopper.page.goto(
                "https://www.rami-levy.co.il/he/cart",
                wait_until="domcontentloaded",
                timeout=15000,
            )
            shopper.page.wait_for_timeout(2000)
            els = shopper.page.query_selector_all('[class*="cart-item"], [class*="cartItem"]')
            items = []
            for el in els:
                text = el.inner_text().strip()
                items.append(CartItem(
                    product=Product(id="live", name=text[:60], category="unknown",
                                    price=0.0, attributes=[], size="", brand=""),
                    quantity=1,
                    verified=True,
                ))
            return Cart(items=items)
        except Exception:
            return Cart(items=[])

    def verify_cart(self) -> Dict[str, bool]:
        live_cart = self.get_cart()
        live_names = {item.product.name.lower() for item in live_cart.items}
        return {
            p["id"]: any(
                p["name"].lower() in name or name in p["name"].lower()
                for name in live_names
            )
            for p in self.search_engine.products
        }

    def _get_shopper(self):
        if self._shopper is None:
            from smart_shopper import SmartShopper
            self._shopper = SmartShopper()
            self._shopper.connect_to_chrome()
        return self._shopper

    def _fetch_from_site(self) -> List[Dict]:
        # Falls back to the local JSON file when the cache is stale.
        # Replace this method with live catalog scraping when ready.
        if os.path.exists(self.cache.path):
            with open(self.cache.path, "r", encoding="utf-8") as f:
                return json.load(f).get("products", [])
        return []

    @staticmethod
    def _to_product(raw: Dict) -> Product:
        sizes = raw.get("sizes") or []
        price = sizes[0].get("price", 0.0) if sizes else 0.0
        size = sizes[0].get("size", "") if sizes else ""
        return Product(
            id=raw["id"],
            name=raw["name"],
            category=raw.get("category", ""),
            price=price,
            attributes=raw.get("attributes", []),
            size=size,
            brand=raw.get("brand", ""),
        )
```

- [ ] **Step 4: Delete `skill/rami_levy_api.py`**

```bash
rm /home/aavitan/claude-projects/shopping-cart/skill/rami_levy_api.py
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest dev/tests/test_rami_levy_store.py -v
```

Expected: 9 passed

- [ ] **Step 6: Commit**

```bash
git add skill/rami_levy_store.py dev/tests/test_rami_levy_store.py
git rm skill/rami_levy_api.py
git commit -m "feat: add RamiLevyStore implementing Store ABC, absorb rami_levy_api"
```

---

### Task 6: Refactor `skill_handler.py` — Thin Orchestrator

**Files:**
- Rewrite: `skill/skill_handler.py`
- Create: `dev/tests/test_skill_handler.py`

**Interfaces:**
- Consumes: `Store` from `store.py`; `QueryParser` from `query_parser.py`; `CartManager` from `cart_manager.py`; `OutputFormatter` from `formatters.py`
- Produces:
  - `ShoppingListSkill(store: Store)`
  - `.process_query(user_query: str) -> Dict`
  - `.add_to_cart(product_id: str, quantity: int = 1) -> Dict`
  - `.get_cart_summary() -> Dict`
  - `.verify_cart() -> Dict`
  - `.format_response(user_query: str, fmt: str = "markdown") -> str`
  - `create_skill() -> ShoppingListSkill` (module-level factory; only place that imports RamiLevyStore)

- [ ] **Step 1: Write the failing tests**

Create `dev/tests/test_skill_handler.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skill'))

from unittest.mock import MagicMock
from skill_handler import ShoppingListSkill
from store import Product, CartItem, Cart, SearchFilters


def _product(pid="p1", price=7.0) -> Product:
    return Product(id=pid, name="Red Lentils", category="legumes",
                   price=price, attributes=["vegan"], size="500g", brand="RL")


def _mock_store(products=None):
    store = MagicMock()
    prods = products or [_product()]
    store.search.return_value = prods
    store.add_to_cart.return_value = CartItem(product=_product(), quantity=1)
    store.get_cart.return_value = Cart(items=[CartItem(product=_product(), quantity=1, verified=True)])
    store.verify_cart.return_value = {"p1": True}
    return store


def test_process_query_returns_products():
    skill = ShoppingListSkill(store=_mock_store())
    result = skill.process_query("lentils")
    assert len(result["products"]) == 1
    assert result["products"][0]["name"] == "Red Lentils"


def test_process_query_no_results_includes_clarifying_questions():
    store = _mock_store(products=[])
    skill = ShoppingListSkill(store=store)
    result = skill.process_query("xyzzy")
    assert len(result["clarifying_questions"]) > 0


def test_add_to_cart_success():
    skill = ShoppingListSkill(store=_mock_store())
    result = skill.add_to_cart("p1")
    assert result["success"] is True
    assert "Red Lentils" in result["message"]


def test_add_to_cart_failure_on_value_error():
    store = _mock_store()
    store.add_to_cart.side_effect = ValueError("Product not found: bad_id")
    skill = ShoppingListSkill(store=store)
    result = skill.add_to_cart("bad_id")
    assert result["success"] is False
    assert "not found" in result["message"].lower()


def test_get_cart_summary_warns_ground_truth():
    skill = ShoppingListSkill(store=_mock_store())
    skill.add_to_cart("p1")
    summary = skill.get_cart_summary()
    assert "verify_cart" in summary["warning"]
    assert "local" in summary["warning"].lower()


def test_get_cart_summary_never_calls_store_get_cart():
    store = _mock_store()
    skill = ShoppingListSkill(store=store)
    skill.add_to_cart("p1")
    skill.get_cart_summary()
    store.get_cart.assert_not_called()


def test_verify_cart_delegates_to_store():
    skill = ShoppingListSkill(store=_mock_store())
    skill.add_to_cart("p1")
    result = skill.verify_cart()
    assert result["live_cart_is_ground_truth"] is True
    assert result["all_confirmed"] is True
    assert result["missing"] == []


def test_verify_cart_marks_unverified_items():
    store = _mock_store()
    store.verify_cart.return_value = {"p1": False}
    skill = ShoppingListSkill(store=store)
    skill.add_to_cart("p1")
    result = skill.verify_cart()
    assert result["all_confirmed"] is False
    assert "Red Lentils" in result["missing"]


def test_format_response_markdown_default():
    skill = ShoppingListSkill(store=_mock_store())
    response = skill.format_response("lentils")
    assert isinstance(response, str)
    assert len(response) > 0


def test_no_rami_levy_import_in_skill_handler():
    path = os.path.join(os.path.dirname(__file__), '../../skill/skill_handler.py')
    source = open(path).read()
    assert "rami_levy" not in source
    assert "RamiLevyStore" not in source
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest dev/tests/test_skill_handler.py -v 2>&1 | head -30
```

Expected: multiple failures (old skill_handler imports RamiLevyWebIntegration, doesn't accept Store)

- [ ] **Step 3: Rewrite `skill/skill_handler.py`**

Replace the entire file:

```python
"""
Rami Levy Shopping Skill — thin orchestrator.
Depends only on the Store interface, never on Rami Levy directly.
"""
from typing import Dict, List
from store import Store
from query_parser import QueryParser
from cart_manager import CartManager
from formatters import OutputFormatter


class ShoppingListSkill:
    def __init__(self, store: Store):
        self.store = store
        self.parser = QueryParser()
        self.cart = CartManager()
        self.formatter = OutputFormatter()

    def process_query(self, user_query: str) -> Dict:
        filters = self.parser.parse(user_query)
        if self.parser.is_buy_intent(user_query):
            return self._handle_buy_intent(user_query, filters)
        products = self.store.search(filters)
        raw = [self._to_dict(p) for p in products]
        questions = self.parser.needs_clarification(user_query) if not products else []
        total = sum(p.price for p in products)
        return {
            "list_markdown": self.formatter.format_markdown(
                raw, title="Vegetarian Shopping List — Rami Levy"
            ),
            "products": raw,
            "clarifying_questions": questions,
            "summary": (
                f"✅ Found {len(products)} products totaling ₪{total:.2f}"
                if products else "❌ No products found"
            ),
            "applied_filters": {
                "categories": filters.categories,
                "budget": (filters.min_price, filters.max_price),
                "attributes": filters.attributes,
            },
        }

    def add_to_cart(self, product_id: str, quantity: int = 1) -> Dict:
        try:
            item = self.store.add_to_cart(product_id, quantity)
            self.cart.add(item)
            return {
                "success": True,
                "message": f"✅ Added: {item.product.name} (₪{item.product.price * quantity:.2f})",
                "cart_total": self.cart.get().total,
            }
        except ValueError as e:
            return {"success": False, "message": str(e), "cart_total": self.cart.get().total}

    def get_cart_summary(self) -> Dict:
        local = self.cart.get()
        return {
            "items": [
                {
                    "name": i.product.name,
                    "price": i.product.price,
                    "quantity": i.quantity,
                    "verified": i.verified,
                }
                for i in local.items
            ],
            "total": local.total,
            "warning": (
                "⚠️ Run verify_cart() before placing any order — "
                "local cart is an optimistic mirror only. "
                "The website cart is the ground truth."
            ),
        }

    def verify_cart(self) -> Dict:
        confirmed = self.store.verify_cart()
        for product_id, in_cart in confirmed.items():
            if in_cart:
                self.cart.mark_verified(product_id)
            else:
                self.cart.mark_unverified(product_id)
        local = self.cart.get()
        missing = [i.product.name for i in local.items if not i.verified]
        return {
            "confirmed": {k: v for k, v in confirmed.items() if v},
            "missing": missing,
            "all_confirmed": not missing,
            "live_cart_is_ground_truth": True,
        }

    def format_response(self, user_query: str, fmt: str = "markdown") -> str:
        result = self.process_query(user_query)
        products = result["products"]
        formatters = {
            "json": self.formatter.format_json,
            "csv": self.formatter.format_csv,
            "html": self.formatter.format_html_table,
            "text": self.formatter.format_plain_text,
        }
        if fmt in formatters:
            return formatters[fmt](products)
        response = result["list_markdown"]
        if result["clarifying_questions"]:
            response += "\n\n---\n\n**Help me refine:**\n\n"
            response += "\n".join(
                f"{i + 1}. {q}" for i, q in enumerate(result["clarifying_questions"])
            )
        return response

    def _handle_buy_intent(self, query: str, filters) -> Dict:
        try:
            products = self.store.search(filters)
            added = []
            for product in products[:10]:
                result = self.add_to_cart(product.id)
                if result["success"]:
                    added.append(product.name)
            return {
                "list_markdown": f"✅ Added {len(added)} items via browser",
                "products": [self._to_dict(p) for p in products],
                "clarifying_questions": [],
                "summary": f"Added: {', '.join(added)}" if added else "No items added",
                "browser_automation": True,
            }
        except Exception as e:
            return {
                "list_markdown": f"⚠️ Browser automation failed: {e}",
                "products": [],
                "clarifying_questions": [],
                "summary": str(e),
            }

    @staticmethod
    def _to_dict(p) -> Dict:
        return {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "price": p.price,
            "brand": p.brand,
            "attributes": p.attributes,
            "sizes": [{"size": p.size, "price": p.price}],
        }


def create_skill() -> ShoppingListSkill:
    """Entry point: wire up RamiLevyStore and return a ready skill instance."""
    from rami_levy_store import RamiLevyStore
    return ShoppingListSkill(store=RamiLevyStore())
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest dev/tests/test_skill_handler.py dev/tests/test_store.py dev/tests/test_product_cache.py dev/tests/test_query_parser.py dev/tests/test_cart_manager.py dev/tests/test_rami_levy_store.py -v
```

Expected: all 47 tests pass

- [ ] **Step 5: Verify line count and no Rami Levy imports**

```bash
wc -l /home/aavitan/claude-projects/shopping-cart/skill/skill_handler.py
grep -n "rami_levy\|RamiLevy" /home/aavitan/claude-projects/shopping-cart/skill/skill_handler.py | grep -v "create_skill"
```

Expected: under 200 lines; only `rami_levy_store` appears inside `create_skill()`

- [ ] **Step 6: Smoke test the full wiring (no browser required)**

```bash
python3 -c "
import sys; sys.path.insert(0, 'skill')
from rami_levy_store import RamiLevyStore
from skill_handler import ShoppingListSkill
from store import SearchFilters

store = RamiLevyStore()
skill = ShoppingListSkill(store=store)
result = skill.process_query('lentils')
print('Products found:', len(result['products']))
print('Summary:', result['summary'])
assert len(result['products']) > 0, 'Expected lentil results'
print('✅ Smoke test passed')
"
```

Expected output:
```
✓ Loaded 87 products
✓ Loaded 87 products
Products found: 4
Summary: ✅ Found 4 products totaling ₪XX.XX
✅ Smoke test passed
```

- [ ] **Step 7: Push to GitHub**

```bash
git add skill/skill_handler.py dev/tests/test_skill_handler.py
git commit -m "refactor: slim skill_handler to thin orchestrator with Store injection"
git push origin master
```

---

## Verification Checklist

After all tasks complete, confirm:

- [ ] `wc -l skill/skill_handler.py` → under 200 lines
- [ ] `grep -r "rami_levy\|RamiLevy" skill/skill_handler.py` → only inside `create_skill()`
- [ ] `python -m pytest dev/tests/ -v` → all new tests pass, no pre-existing failures introduced
- [ ] `python3 -c "import sys; sys.path.insert(0,'skill'); from skill_handler import create_skill; s=create_skill(); print(s.process_query('lentils')['summary'])"` → prints found products
- [ ] `ls skill/*.py | wc -l` → `rami_levy_api.py` is gone
