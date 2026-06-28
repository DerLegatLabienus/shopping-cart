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
