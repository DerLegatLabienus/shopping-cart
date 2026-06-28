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
