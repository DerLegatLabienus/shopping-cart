"""
Rami Levy Vegetarian Shopping List - Search Engine
Handles product search, filtering, and ranking
"""

import json
import os
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher

class SearchEngine:
    def __init__(self, products_db_path: str = "rami_levy_products.json"):
        """Initialize search engine with product database"""
        self.products = []
        self.load_products(products_db_path)

    def load_products(self, db_path: str):
        """Load products from JSON database"""
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.products = data.get('products', [])
                print(f"✓ Loaded {len(self.products)} products")
        except FileNotFoundError:
            print(f"Error: Product database not found at {db_path}")
            self.products = []

    def fuzzy_match(self, query: str, target: str, threshold: float = 0.6) -> float:
        """
        Fuzzy string matching with similarity score
        Returns score between 0 and 1 (1 = perfect match)
        """
        query_lower = query.lower()
        target_lower = target.lower()

        # Exact match gets highest score
        if query_lower == target_lower:
            return 1.0

        # Substring match gets high score
        if query_lower in target_lower or target_lower in query_lower:
            return 0.9

        # Use SequenceMatcher for fuzzy matching
        ratio = SequenceMatcher(None, query_lower, target_lower).ratio()
        return ratio if ratio >= threshold else 0.0

    def search_by_name(self, query: str) -> List[Dict]:
        """Search products by name with fuzzy matching"""
        if not query or len(query.strip()) == 0:
            return []

        results = []
        for product in self.products:
            # Check product name
            name_score = self.fuzzy_match(query, product['name'])

            # Also check brand
            brand_score = self.fuzzy_match(query, product.get('brand', ''))

            # Take best score
            best_score = max(name_score, brand_score)

            if best_score > 0.6:
                results.append({
                    'product': product,
                    'score': best_score,
                    'match_type': 'name' if name_score > brand_score else 'brand'
                })

        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def filter_by_category(self, products: List[Dict], categories: List[str]) -> List[Dict]:
        """Filter products by one or more categories"""
        if not categories or len(categories) == 0:
            return products

        categories_lower = [c.lower() for c in categories]
        return [p for p in products if p['category'].lower() in categories_lower]

    def filter_by_price_range(self, products: List[Dict], min_price: float = 0,
                             max_price: float = float('inf')) -> List[Dict]:
        """Filter products within price range"""
        filtered = []
        for product in products:
            # Get minimum price across all sizes
            if product.get('sizes'):
                min_product_price = min(size['price'] for size in product['sizes'])
                if min_price <= min_product_price <= max_price:
                    filtered.append(product)
        return filtered

    def filter_by_attributes(self, products: List[Dict], attributes: List[str]) -> List[Dict]:
        """Filter products by attributes (e.g., 'organic', 'vegan', 'ready-to-eat')"""
        if not attributes:
            return products

        attributes_lower = [a.lower() for a in attributes]
        filtered = []

        for product in products:
            product_attrs = [attr.lower() for attr in product.get('attributes', [])]
            # Product must have at least one matching attribute
            if any(attr in product_attrs for attr in attributes_lower):
                filtered.append(product)
            # Also check organic flag
            elif 'organic' in attributes_lower and product.get('organic', False):
                filtered.append(product)

        return filtered

    def rank_results(self, products: List[Dict], sort_by: str = 'relevance',
                    reverse: bool = False) -> List[Dict]:
        """
        Sort results by specified criteria
        sort_by: 'relevance', 'price', 'name', 'category'
        """
        if sort_by == 'price':
            # Sort by minimum price in each product
            return sorted(products,
                         key=lambda p: min(size['price'] for size in p.get('sizes', [{}])),
                         reverse=reverse)
        elif sort_by == 'name':
            return sorted(products, key=lambda p: p['name'], reverse=reverse)
        elif sort_by == 'category':
            return sorted(products, key=lambda p: p['category'], reverse=reverse)
        else:  # relevance (default)
            return products  # Already sorted by relevance score from search

    def get_categories(self) -> List[str]:
        """Get all available categories"""
        categories = set()
        for product in self.products:
            categories.add(product['category'])
        return sorted(list(categories))

    def get_price_stats(self, products: List[Dict]) -> Dict:
        """Get min, max, and average prices from products"""
        if not products:
            return {'min': 0, 'max': 0, 'avg': 0, 'count': 0}

        prices = []
        for product in products:
            for size in product.get('sizes', []):
                prices.append(size['price'])

        if not prices:
            return {'min': 0, 'max': 0, 'avg': 0, 'count': 0}

        return {
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices),
            'count': len(prices)
        }

    def advanced_search(self, name_query: str = "", categories: List[str] = None,
                       min_price: float = 0, max_price: float = float('inf'),
                       attributes: List[str] = None, sort_by: str = 'relevance',
                       limit: int = None) -> Tuple[List[Dict], Dict]:
        """
        Advanced search combining all filters
        Returns: (filtered_products, metadata)
        """
        # Start with all products
        results = self.products[:]

        # Apply name search if provided
        if name_query:
            search_results = self.search_by_name(name_query)
            results = [r['product'] for r in search_results]

        # Apply filters
        if categories:
            results = self.filter_by_category(results, categories)

        results = self.filter_by_price_range(results, min_price, max_price)

        if attributes:
            results = self.filter_by_attributes(results, attributes)

        # Sort results
        results = self.rank_results(results, sort_by)

        # Apply limit
        if limit:
            results = results[:limit]

        # Generate metadata
        metadata = {
            'query': name_query,
            'categories_filter': categories,
            'price_range': {'min': min_price, 'max': max_price},
            'attributes_filter': attributes,
            'total_results': len(results),
            'price_stats': self.get_price_stats(results)
        }

        return results, metadata

    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get a specific product by ID"""
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None

    def get_products_by_ids(self, product_ids: List[str]) -> List[Dict]:
        """Get multiple products by their IDs"""
        results = []
        for product_id in product_ids:
            product = self.get_product_by_id(product_id)
            if product:
                results.append(product)
        return results


if __name__ == "__main__":
    # Test the search engine
    engine = SearchEngine()

    # Test 1: Simple name search
    print("\n=== Test 1: Search for 'lentils' ===")
    results, meta = engine.advanced_search(name_query="lentils", limit=3)
    print(f"Found {meta['total_results']} results:")
    for r in results:
        print(f"  - {r['name']} ({r['category']}) - ₪{r['sizes'][0]['price']}")

    # Test 2: Category filter
    print("\n=== Test 2: Search for vegetables under ₪5 ===")
    results, meta = engine.advanced_search(
        categories=["vegetables"],
        max_price=5,
        limit=5
    )
    print(f"Found {meta['total_results']} results:")
    for r in results:
        price = r['sizes'][0]['price'] if r['sizes'] else 'N/A'
        print(f"  - {r['name']} - ₪{price}")

    # Test 3: Organic filter
    print("\n=== Test 3: Organic products ===")
    results, meta = engine.advanced_search(
        attributes=["organic"],
        limit=5
    )
    print(f"Found {meta['total_results']} organic results:")
    for r in results:
        print(f"  - {r['name']} ({r['category']}) - ₪{r['sizes'][0]['price']}")

    # Test 4: Vegan products under budget
    print("\n=== Test 4: Vegan products under ₪50 ===")
    results, meta = engine.advanced_search(
        attributes=["vegan"],
        max_price=50,
        sort_by="price",
        limit=5
    )
    print(f"Found {meta['total_results']} results (sorted by price):")
    for r in results:
        print(f"  - {r['name']} - ₪{r['sizes'][0]['price']}")

    # Test 5: Categories available
    print("\n=== Available Categories ===")
    categories = engine.get_categories()
    print(f"Total categories: {len(categories)}")
    print(f"Categories: {', '.join(categories)}")
