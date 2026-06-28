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
