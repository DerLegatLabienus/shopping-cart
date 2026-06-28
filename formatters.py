"""
Rami Levy Shopping List - Output Formatters
Converts search results into different formats: Markdown, JSON, CSV, HTML Table
"""

import json
import csv
from io import StringIO
from datetime import datetime
from typing import List, Dict


class OutputFormatter:
    def __init__(self, currency: str = "₪"):
        self.currency = currency

    def calculate_total(self, products: List[Dict]) -> float:
        """Calculate total price from products (using minimum price per product)"""
        total = 0
        for product in products:
            if product.get('sizes'):
                min_price = min(size['price'] for size in product['sizes'])
                total += min_price
        return round(total, 2)

    def format_markdown(self, products: List[Dict], title: str = "Vegetarian Shopping List",
                       include_urls: bool = False) -> str:
        """Format results as Markdown shopping list"""
        if not products:
            return f"# {title}\n\n*No products found*"

        md = f"# {title} - Rami Levy\n\n"
        md += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"

        # Group by category
        categories = {}
        for product in products:
            cat = product['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(product)

        # Format by category
        for category in sorted(categories.keys()):
            items = categories[category]
            md += f"## {category.title()} ({len(items)} items)\n\n"

            for product in items:
                name = product['name']
                brand = product.get('brand', '')
                attributes = ', '.join(product.get('attributes', []))
                size = product['sizes'][0] if product.get('sizes') else {}

                price = size.get('price', 'N/A')
                size_str = size.get('size', 'N/A')
                unit_price = size.get('price_per_unit', '')

                # Format line
                attr_str = f" *[{attributes}]*" if attributes else ""
                unit_str = f" ({unit_price})" if unit_price else ""
                brand_str = f" - {brand}" if brand else ""

                md += f"- **{name}**{brand_str} ({size_str}): {self.currency}{price}{unit_str}{attr_str}\n"

            md += "\n"

        # Add summary
        total = self.calculate_total(products)
        md += "---\n\n"
        md += f"**Total Items:** {len(products)}\n\n"
        md += f"**Estimated Total:** {self.currency}{total}\n\n"
        md += f"**Note:** Prices are based on minimum size available for each product.\n"

        return md

    def format_json(self, products: List[Dict], title: str = "Vegetarian Shopping List") -> str:
        """Format results as JSON"""
        if not products:
            result = {
                'list_name': title,
                'timestamp': datetime.now().isoformat(),
                'items': [],
                'total_items': 0,
                'estimated_total': 0
            }
            return json.dumps(result, ensure_ascii=False, indent=2)

        # Group by category
        categories = {}
        for product in products:
            cat = product['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(product)

        # Build items list
        items = []
        for product in products:
            size = product['sizes'][0] if product.get('sizes') else {}
            items.append({
                'id': product['id'],
                'name': product['name'],
                'category': product['category'],
                'brand': product.get('brand', ''),
                'size': size.get('size', ''),
                'price': size.get('price', 0),
                'price_per_unit': size.get('price_per_unit', ''),
                'attributes': product.get('attributes', []),
                'organic': product.get('organic', False)
            })

        result = {
            'metadata': {
                'list_name': title,
                'timestamp': datetime.now().isoformat(),
                'total_items': len(products),
                'total_categories': len(categories),
                'estimated_total': self.calculate_total(products),
                'currency': self.currency
            },
            'items': items,
            'categories': {cat: len(prods) for cat, prods in categories.items()}
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    def format_csv(self, products: List[Dict]) -> str:
        """Format results as CSV"""
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Product Name',
            'Brand',
            'Category',
            'Size',
            'Price',
            'Price Per Unit',
            'Attributes',
            'Organic',
            'ID'
        ])

        # Write rows
        for product in products:
            size = product['sizes'][0] if product.get('sizes') else {}
            writer.writerow([
                product['name'],
                product.get('brand', ''),
                product['category'],
                size.get('size', ''),
                size.get('price', ''),
                size.get('price_per_unit', ''),
                '; '.join(product.get('attributes', [])),
                'Yes' if product.get('organic', False) else 'No',
                product['id']
            ])

        return output.getvalue()

    def format_html_table(self, products: List[Dict], title: str = "Vegetarian Shopping List") -> str:
        """Format results as HTML table"""
        if not products:
            return f"<h1>{title}</h1><p>No products found</p>"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th {{ background-color: #4CAF50; color: white; padding: 12px; text-align: left; border: 1px solid #ddd; }}
        td {{ padding: 10px; border: 1px solid #ddd; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .organic {{ background-color: #d4edda; }}
        .price {{ color: #d9534f; font-weight: bold; }}
        .summary {{ margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #4CAF50; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <table>
        <thead>
            <tr>
                <th>Product</th>
                <th>Brand</th>
                <th>Category</th>
                <th>Size</th>
                <th>Price</th>
                <th>Unit Price</th>
                <th>Type</th>
            </tr>
        </thead>
        <tbody>
"""

        for product in products:
            size = product['sizes'][0] if product.get('sizes') else {}
            organic_class = ' class="organic"' if product.get('organic') else ''
            attrs = ', '.join(product.get('attributes', []))
            attrs_html = f"<br/><small>{attrs}</small>" if attrs else ""

            html += f"""            <tr{organic_class}>
                <td><strong>{product['name']}</strong>{attrs_html}</td>
                <td>{product.get('brand', '')}</td>
                <td>{product['category']}</td>
                <td>{size.get('size', '')}</td>
                <td class="price">{self.currency}{size.get('price', 'N/A')}</td>
                <td>{size.get('price_per_unit', '')}</td>
                <td>{'🌱 Organic' if product.get('organic') else 'Regular'}</td>
            </tr>
"""

        total = self.calculate_total(products)
        html += f"""        </tbody>
    </table>

    <div class="summary">
        <h3>Summary</h3>
        <p><strong>Total Items:</strong> {len(products)}</p>
        <p><strong>Estimated Total:</strong> <span class="price">{self.currency}{total}</span></p>
        <p><small>Note: Prices are based on minimum size available for each product.</small></p>
    </div>
</body>
</html>
"""
        return html

    def format_plain_text(self, products: List[Dict], title: str = "Vegetarian Shopping List") -> str:
        """Format results as plain text shopping list"""
        if not products:
            return f"{title}\n\nNo products found."

        text = f"{title.upper()}\n"
        text += f"{'=' * len(title)}\n\n"
        text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Group by category
        categories = {}
        for product in products:
            cat = product['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(product)

        for category in sorted(categories.keys()):
            items = categories[category]
            text += f"\n{category.upper()} ({len(items)} items)\n"
            text += f"-" * (len(category) + len(str(len(items))) + 11) + "\n"

            for product in items:
                name = product['name']
                brand = product.get('brand', '')
                size = product['sizes'][0] if product.get('sizes') else {}
                price = size.get('price', 'N/A')
                size_str = size.get('size', '')
                unit_price = size.get('price_per_unit', '')

                brand_str = f" ({brand})" if brand else ""
                unit_str = f" - {unit_price}" if unit_price else ""

                text += f"  ☐ {name}{brand_str} [{size_str}] ... {self.currency}{price}{unit_str}\n"

            text += "\n"

        total = self.calculate_total(products)
        text += f"\n{'=' * 40}\n"
        text += f"TOTAL ITEMS: {len(products)}\n"
        text += f"ESTIMATED TOTAL: {self.currency}{total}\n"
        text += f"{'=' * 40}\n"

        return text

    def format_as(self, products: List[Dict], format_type: str = "markdown",
                 title: str = "Vegetarian Shopping List") -> str:
        """
        Universal formatter - converts to requested format
        format_type: 'markdown', 'json', 'csv', 'html', 'text'
        """
        format_type = format_type.lower()

        if format_type == 'markdown' or format_type == 'md':
            return self.format_markdown(products, title)
        elif format_type == 'json':
            return self.format_json(products, title)
        elif format_type == 'csv':
            return self.format_csv(products)
        elif format_type == 'html':
            return self.format_html_table(products, title)
        elif format_type == 'text' or format_type == 'plain':
            return self.format_plain_text(products, title)
        else:
            # Default to markdown
            return self.format_markdown(products, title)


if __name__ == "__main__":
    # Test formatters with sample data
    sample_products = [
        {
            "id": "prod_001",
            "name": "Red Lentils",
            "category": "legumes",
            "brand": "Rami Levy",
            "sizes": [{"size": "500g", "price": 7.00, "price_per_unit": "1.40 per 100g"}],
            "attributes": ["vegetarian", "vegan"],
            "organic": False
        },
        {
            "id": "prod_063",
            "name": "Organic Tomatoes",
            "category": "organic",
            "brand": "Rami Levy Organic",
            "sizes": [{"size": "per kg", "price": 8.50, "price_per_unit": "8.50 per kg"}],
            "attributes": ["vegetarian", "vegan"],
            "organic": True
        }
    ]

    formatter = OutputFormatter()

    print("=== MARKDOWN FORMAT ===")
    print(formatter.format_markdown(sample_products))

    print("\n=== JSON FORMAT ===")
    print(formatter.format_json(sample_products))

    print("\n=== CSV FORMAT ===")
    print(formatter.format_csv(sample_products))

    print("\n=== PLAIN TEXT FORMAT ===")
    print(formatter.format_plain_text(sample_products))
