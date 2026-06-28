"""
Hebrew Translator for Rami Levy website queries.
Translates English product names to Hebrew before searching.
"""

import json
import os


class HebrewTranslator:
    """Translate English product names to Hebrew for Rami Levy website."""

    def __init__(self):
        """Load product database for translation mappings."""
        module_dir = os.path.dirname(os.path.abspath(__file__))
        products_path = os.path.join(module_dir, "rami_levy_products.json")

        self.product_map = {}  # English name -> Hebrew name
        self.hebrew_names = {}  # Product ID -> Hebrew name

        try:
            with open(products_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for product in data.get('products', []):
                    name = product.get('name', '').lower()
                    hebrew = product.get('hebrew_name', '')
                    if name and hebrew:
                        self.product_map[name] = hebrew
                        self.hebrew_names[product.get('id')] = hebrew
        except Exception:
            # If product file doesn't load, continue with empty map
            pass

    def translate(self, english_query: str) -> str:
        """
        Translate English product name to Hebrew.

        Args:
            english_query: English product name or search term

        Returns:
            Hebrew translation if found, otherwise original query
        """
        query_lower = english_query.lower().strip()

        # Direct match in product map
        if query_lower in self.product_map:
            return self.product_map[query_lower]

        # Partial match (first word)
        words = query_lower.split()
        if words and words[0] in self.product_map:
            return self.product_map[words[0]]

        # Fallback: return original (will fail on Rami Levy)
        return english_query

    def translate_batch(self, queries: list) -> list:
        """
        Translate multiple queries to Hebrew.

        Args:
            queries: List of English product names

        Returns:
            List of Hebrew translations
        """
        return [self.translate(q) for q in queries]

    def get_hebrew_name(self, product_id: str) -> str:
        """Get Hebrew name for a product by ID."""
        return self.hebrew_names.get(product_id, "")
