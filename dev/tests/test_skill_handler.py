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
    prods = [_product()] if products is None else products
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
    # Only check module-level code (before create_skill factory) has no RamiLevy coupling
    module_level = source[:source.index("def create_skill")]
    assert "rami_levy" not in module_level
    assert "RamiLevyStore" not in module_level
