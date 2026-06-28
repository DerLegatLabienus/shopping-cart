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
        data = self._read_raw()
        if data is None:
            return None
        # Check staleness inline from the single read result
        cache_updated_at = data.get("_cache_updated_at")
        if cache_updated_at is None:
            return None
        age = time.time() - cache_updated_at
        if age > self.ttl_seconds:
            return None
        return data.get("products")

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
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return None
