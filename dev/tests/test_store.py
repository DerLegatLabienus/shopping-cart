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
