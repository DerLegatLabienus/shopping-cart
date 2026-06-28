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
