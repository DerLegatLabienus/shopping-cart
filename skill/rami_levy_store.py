import json
import os
from typing import Dict, List, Optional

from product_cache import ProductCache
from search_engine import SearchEngine
from store import Cart, CartItem, Product, SearchFilters, Store
from hebrew_translator import HebrewTranslator


class RamiLevyStore(Store):
    def __init__(self, cache_path: Optional[str] = None, cache_ttl: int = 3600):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        path = cache_path or os.path.join(module_dir, "rami_levy_products.json")
        self.cache = ProductCache(path, ttl_seconds=cache_ttl)
        self.search_engine = SearchEngine(path)
        self.translator = HebrewTranslator()
        self._shopper = None

    def search(self, filters: SearchFilters) -> List[Product]:
        raw = self.cache.get_all()
        if raw is None:
            raw = self._fetch_from_site()
            self.cache.set_all(raw)
        products, _ = self.search_engine.advanced_search(
            name_query=" ".join(filters.keywords),
            categories=filters.categories or None,
            min_price=0 if filters.min_price is None else filters.min_price,
            max_price=float("inf") if filters.max_price is None else filters.max_price,
            attributes=filters.attributes or None,
        )
        return [self._to_product(p) for p in products]

    def add_to_cart(self, product_id: str, quantity: int = 1) -> CartItem:
        raw = self.search_engine.get_product_by_id(product_id)
        if not raw:
            raise ValueError(f"Product not found: {product_id}")
        shopper = self._get_shopper()
        # Translate product name to Hebrew before searching on website
        hebrew_name = self.translator.translate(raw["name"])
        shopper.search_for_products([hebrew_name])
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
