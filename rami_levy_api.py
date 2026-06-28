"""
Rami Levy API Client - No bot detection, no browser automation needed!
Uses the official Rami Levy API to fetch products and prices.
"""

import requests
import json
from typing import Dict, List, Optional


class RamiLevyAPI:
    """
    Client for Rami Levy's public API.

    API Endpoint: https://www.rami-levy.co.il/api/search

    Advantages over web scraping:
    - No bot detection
    - No CAPTCHA
    - Fast and reliable
    - Real-time data from website
    """

    BASE_URL = "https://www.rami-levy.co.il/api/search"

    def __init__(self):
        """Initialize API client with realistic headers"""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })

    def search_products(self, query: str, limit: int = 20) -> Dict:
        """
        Search for products by name/term.

        Args:
            query: Product name or search term (supports Hebrew)
            limit: Max results to return (default 20)

        Returns:
            {
                'success': bool,
                'query': str,
                'total': int,                    # Total matching products
                'products': [
                    {
                        'id': str,
                        'name': str,
                        'name_he': str,
                        'price': float,
                        'category': str,
                        'image_url': str,
                        'barcode': str
                    }
                ],
                'message': str
            }
        """
        try:
            response = self.session.get(
                self.BASE_URL,
                params={"q": query, "limit": limit},
                timeout=10
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "query": query,
                    "total": 0,
                    "products": [],
                    "message": f"API returned {response.status_code}"
                }

            data = response.json()

            # Parse API response
            products = []
            for item in data.get("data", []):
                products.append({
                    "id": item.get("id"),
                    "barcode": item.get("id"),
                    "name": item.get("name", ""),
                    "name_he": item.get("name", ""),
                    "price": float(item.get("price", 0)) if item.get("price") else 0,
                    "category": item.get("category", ""),
                    "image_url": item.get("images", {}).get("small", ""),
                })

            return {
                "success": True,
                "query": query,
                "total": data.get("total", len(products)),
                "products": products[:limit],
                "message": f"✅ Found {len(products)} products"
            }

        except Exception as e:
            return {
                "success": False,
                "query": query,
                "total": 0,
                "products": [],
                "message": f"❌ API Error: {str(e)}"
            }

    def search_multiple(self, queries: List[str]) -> Dict:
        """
        Search for multiple products at once.

        Args:
            queries: List of product names/terms

        Returns:
            {
                'success': bool,
                'total_products': int,
                'by_query': {
                    'milk': {...},
                    'bread': {...}
                }
            }
        """
        results = {}
        total_products = 0

        for query in queries:
            result = self.search_products(query, limit=5)
            results[query] = result
            total_products += len(result.get("products", []))

        return {
            "success": True,
            "total_products": total_products,
            "by_query": results
        }

    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """
        Get product details by barcode.

        Args:
            barcode: Product barcode/ID

        Returns:
            Product dict or None if not found
        """
        # Try to fetch by barcode
        result = self.search_products(barcode, limit=1)
        if result.get("products"):
            return result["products"][0]
        return None


if __name__ == "__main__":
    # Demo
    api = RamiLevyAPI()

    print("🔍 TESTING RAMI LEVY API\n")

    # Single search
    print("1. Searching for 'milk'...")
    result = api.search_products("milk", limit=5)
    print(f"   {result['message']}")
    for prod in result.get("products", [])[:3]:
        print(f"   - {prod['name']} - ₪{prod['price']}")

    # Multiple search
    print("\n2. Searching for multiple products...")
    results = api.search_multiple(["milk", "bread", "yogurt"])
    print(f"   Total products found: {results['total_products']}")
    for query, res in results['by_query'].items():
        print(f"   {query}: {len(res.get('products', []))} products")
