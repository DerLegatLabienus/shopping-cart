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
