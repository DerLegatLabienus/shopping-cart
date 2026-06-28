# Skill Architecture Refactor — Design Spec

**Date:** 2026-06-28  
**Status:** Approved  
**Goal:** Restructure the Rami Levy shopping skill for production-grade maintainability — loosely coupled modules, a formal `Store` abstraction layer, and a decomposed `skill_handler.py`.

---

## Problem Statement

The current `skill_handler.py` is 1,496 lines and does too much: query parsing, local search, browser orchestration, cart management, output formatting, and session state all live in one class. The Rami Levy web layer is directly imported at the top level, making the core skill coupled to a specific supermarket. Browser modules are imported inline inside methods as a workaround for optional dependencies. There is no formal boundary between generic shopping logic and Rami Levy-specific implementation.

---

## Design Principles

- Each module has one clear responsibility
- The core skill (`ShoppingListSkill`) depends only on the `Store` interface — never on Rami Levy directly
- Adding a new supermarket = one new file implementing `Store`, zero changes to core
- The local JSON file is a cache, not a source of truth — online access is primary
- Browser modules stay as-is; they just get owned by `RamiLevyStore` instead of `skill_handler.py`

---

## Module Map

```
skill/
├── skill_handler.py        # thin orchestrator only (~150 lines)
├── store.py                # Store ABC + Product/Cart/SearchFilters dataclasses
├── query_parser.py         # NL query → SearchFilters (extracted from skill_handler)
├── cart_manager.py         # local session cart state (extracted from skill_handler)
├── product_cache.py        # JSON cache with TTL
├── rami_levy_store.py      # RamiLevyStore(Store) — concrete implementation
│
│   # unchanged (already clean):
├── formatters.py
├── search_engine.py
│
│   # unchanged (browser layer, now owned by RamiLevyStore):
├── rami_levy_web.py
├── browser_manager.py
├── chrome_connector.py
├── web_scraper.py
├── cart_automation.py
├── smart_shopper.py
│
├── rami_levy_products.json   # cache file (not source of truth)
├── SKILL.md
└── requirements.txt
```

`rami_levy_api.py` is absorbed into `rami_levy_store.py` — it was thin and only used there.

---

## Data Types (`store.py`)

Plain dataclasses with no Rami Levy knowledge. These are the shared language of the system.

```python
@dataclass
class Product:
    id: str
    name: str
    category: str
    price: float
    attributes: List[str]   # e.g. ["vegan", "organic", "kosher"]
    size: str
    brand: str

@dataclass
class CartItem:
    product: Product
    quantity: int
    verified: bool = False

@dataclass
class Cart:
    items: List[CartItem]

    @property
    def total(self) -> float:
        return sum(i.product.price * i.quantity for i in self.items)

@dataclass
class SearchFilters:
    keywords: List[str]
    categories: List[str]
    max_price: Optional[float]
    min_price: Optional[float]
    attributes: List[str]    # dietary/organic filters
```

---

## Store Interface (`store.py`)

```python
class Store(ABC):
    @abstractmethod
    def search(self, filters: SearchFilters) -> List[Product]: ...

    @abstractmethod
    def add_to_cart(self, product_id: str, quantity: int = 1) -> CartItem: ...

    @abstractmethod
    def get_cart(self) -> Cart: ...

    @abstractmethod
    def verify_cart(self) -> Dict[str, bool]: ...  # product_id → confirmed in cart
```

`ShoppingListSkill` depends only on `Store`. The concrete implementation is injected at construction time.

---

## ProductCache (`product_cache.py`)

Sits transparently inside `RamiLevyStore`. The caller never interacts with it directly.

**Behavior:**
- Default TTL: 1 hour (configurable)
- `get_all()` returns products if fresh, `None` if stale or missing
- `set_all()` writes products + timestamp to JSON
- `refresh(fetcher)` force-fetches, updates cache, returns fresh products
- Exposes `is_stale: bool` and `age_seconds: float` properties

**Cache file:** `rami_levy_products.json` — same file as before, TTL metadata added.

**How `RamiLevyStore.search()` uses it:**
```python
def search(self, filters: SearchFilters) -> List[Product]:
    products = self.cache.get_all()
    if products is None:
        products = self._fetch_from_site()
        self.cache.set_all(products)
    return self.search_engine.filter(products, filters)
```

`add_to_cart()` always goes live — no caching on writes.

---

## Extracted Modules

### `query_parser.py`
Owns all natural language → structured filter logic currently in `skill_handler.py`.

```python
class QueryParser:
    def parse(self, query: str) -> SearchFilters: ...
    def needs_clarification(self, query: str) -> List[str]: ...
```

Handles: budget extraction ("under 50", "100-200"), category aliases ("veggies" → vegetables), dietary keywords ("vegan", "organic", "kosher").

### `cart_manager.py`
Owns local session cart state — currently the `self.cart` dict and ~6 methods in `skill_handler.py`.

```python
class CartManager:
    def add(self, item: CartItem) -> None: ...
    def remove(self, product_id: str) -> None: ...
    def get(self) -> Cart: ...
    def mark_verified(self, product_id: str) -> None: ...
    def clear(self) -> None: ...
```

No browser knowledge, no Rami Levy knowledge. Pure local state.

---

## Thin Orchestrator (`skill_handler.py`)

After the refactor the class drops to ~150 lines. The `store` is injected — the skill has no import of `RamiLevyStore`.

```python
class ShoppingListSkill:
    def __init__(self, store: Store):
        self.store = store
        self.parser = QueryParser()
        self.cart = CartManager()
        self.formatter = OutputFormatter()

    def process_query(self, query: str) -> Dict: ...
    def add_to_cart(self, product_id: str) -> Dict: ...
    def get_cart_summary(self) -> Dict: ...
    def verify_cart(self) -> Dict: ...
    def format_response(self, results, fmt: str = "markdown") -> str: ...
```

**Wiring (entry point or tests):**
```python
store = RamiLevyStore()
skill = ShoppingListSkill(store=store)
```

---

## What Stays Unchanged

| File | Reason |
|---|---|
| `formatters.py` | Already clean, no coupling |
| `search_engine.py` | Already clean, reused by `ProductCache` |
| `browser_manager.py` | Works, just moves under `RamiLevyStore`'s ownership |
| `chrome_connector.py` | Works, same |
| `web_scraper.py` | Works, same |
| `cart_automation.py` | Works, same |
| `smart_shopper.py` | Works, same |
| `rami_levy_web.py` | Works, same |

---

## Future Extensibility (not in scope today)

To add a new supermarket (e.g. Shufersal):
1. Create `shufersal_store.py` implementing `Store`
2. Wire it: `skill = ShoppingListSkill(store=ShufersalStore())`
3. Zero changes to `skill_handler.py`, `query_parser.py`, `cart_manager.py`, or `formatters.py`

---

## Success Criteria

- `skill_handler.py` under 200 lines
- No Rami Levy import in `skill_handler.py`
- `ShoppingListSkill` accepts any `Store` implementation
- `ProductCache` respects TTL and fetches live on miss
- All existing skill methods (`process_query`, `add_to_cart`, `verify_cart`, etc.) continue to work
- Every new module under 300 lines
