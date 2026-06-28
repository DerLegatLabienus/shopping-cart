"""
Rami Levy Website Integration
Handles adding items to cart and verifying on the live website
"""

from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime


class RamiLevyWebIntegration:
    """
    Integrates with Rami Levy website to:
    - Navigate to products
    - Add items to cart
    - Verify items in cart
    - Track cart state
    """

    def __init__(self):
        """Initialize web integration"""
        self.base_url = "https://www.rami-levy.co.il/he"
        self.cart_state = {}  # Track what we've added to website
        self.verified_items = {}  # Track verified items on website
        self.session_log = []  # Log of all actions
        self.browser_reference = None  # Reference to current browser tab

    def search_product_on_website(self, product_name: str, category: str = None) -> Dict:
        """
        Search for product on Rami Levy website

        Args:
            product_name: Name of product to search
            category: Optional category filter

        Returns:
            {
                'success': bool,
                'message': str,
                'found_products': [],
                'actions_needed': []
            }
        """
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': 'search_product',
            'product_name': product_name,
            'category': category,
            'status': 'pending'
        }

        return {
            'success': True,
            'message': f"Ready to search for '{product_name}' on Rami Levy website",
            'actions_needed': [
                f"1. Navigate to search box",
                f"2. Type '{product_name}'",
                f"3. Press Enter to search",
                f"4. Identify product in results",
                f"5. Click to view details"
            ],
            'action_log': [action]
        }

    def add_product_to_website_cart(
        self,
        product_id: str,
        product_name: str,
        quantity: float = 1,
        price: float = 0
    ) -> Dict:
        """
        Add product to website cart and track it

        Args:
            product_id: Product ID from database
            product_name: Product name
            quantity: Quantity to add
            price: Price per unit

        Returns:
            {
                'success': bool,
                'message': str,
                'item_added': {...},
                'verification_needed': bool,
                'actions_to_perform': []
            }
        """

        item = {
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
            'price_per_unit': price,
            'subtotal': price * quantity,
            'status': 'added_to_tracking',
            'added_timestamp': datetime.now().isoformat(),
            'website_verified': False
        }

        self.cart_state[product_id] = item

        action = {
            'timestamp': datetime.now().isoformat(),
            'action': 'add_to_cart',
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
            'status': 'needs_verification'
        }
        self.session_log.append(action)

        return {
            'success': True,
            'message': f"✅ Added to tracking: {product_name}",
            'item_added': item,
            'verification_needed': True,
            'actions_to_perform': [
                f"1. Look for 'Add to Cart' or '+' button on product",
                f"2. Click to add {quantity} to cart",
                f"3. Confirm quantity is {quantity}",
                f"4. Check cart shows ₪{item['subtotal']:.2f}",
                f"5. Report: Item added or still need help?"
            ]
        }

    def verify_item_in_website_cart(
        self,
        product_id: str,
        product_name: str,
        expected_price: float
    ) -> Dict:
        """
        Verify that item is actually in website cart

        Args:
            product_id: Product ID
            product_name: Product name
            expected_price: Expected cart total or item price

        Returns:
            {
                'verified': bool,
                'product_id': str,
                'message': str,
                'status': 'verified' | 'not_found' | 'needs_checking'
            }
        """

        if product_id not in self.cart_state:
            return {
                'verified': False,
                'product_id': product_id,
                'message': f"❌ {product_name} not in our tracking system",
                'status': 'not_tracked',
                'actions_needed': [
                    f"This product was never added to tracking.",
                    f"Add it first using add_product_to_website_cart()"
                ]
            }

        # Check if already verified
        if product_id in self.verified_items:
            return {
                'verified': True,
                'product_id': product_id,
                'product_name': product_name,
                'message': f"✅ {product_name} verified in cart",
                'status': 'verified',
                'item': self.verified_items[product_id]
            }

        # Need to check on website
        return {
            'verified': False,
            'product_id': product_id,
            'message': f"⚠️ Need to verify {product_name} is in cart",
            'status': 'needs_checking',
            'tracked_item': self.cart_state[product_id],
            'actions_needed': [
                f"1. Look at your shopping cart",
                f"2. Find '{product_name}' in the list",
                f"3. Check if price/quantity match: ₪{self.cart_state[product_id]['subtotal']:.2f}",
                f"4. If found: Report 'Verified'",
                f"5. If NOT found: Report 'Not in cart'"
            ]
        }

    def mark_item_verified(self, product_id: str, verified: bool) -> Dict:
        """
        Mark an item as verified in website cart based on user confirmation

        Args:
            product_id: Product ID
            verified: Whether user confirmed it's in cart

        Returns:
            {
                'success': bool,
                'product_id': str,
                'message': str
            }
        """

        if product_id not in self.cart_state:
            return {
                'success': False,
                'message': f"Product {product_id} not in tracking"
            }

        item = self.cart_state[product_id]

        if verified:
            item['website_verified'] = True
            item['status'] = 'verified_in_cart'
            self.verified_items[product_id] = item

            return {
                'success': True,
                'product_id': product_id,
                'message': f"✅ {item['product_name']} confirmed in cart",
                'item': item
            }
        else:
            item['website_verified'] = False
            item['status'] = 'not_in_cart'

            return {
                'success': True,
                'product_id': product_id,
                'message': f"❌ {item['product_name']} NOT in cart - need to add it",
                'item': item,
                'next_steps': [
                    f"1. Navigate to {item['product_name']}",
                    f"2. Click 'Add to Cart'",
                    f"3. Set quantity to {item['quantity']}",
                    f"4. Confirm added",
                    f"5. Run verify again"
                ]
            }

    def get_cart_status(self) -> Dict:
        """
        Get current status of all tracked items

        Returns:
            {
                'total_tracked': int,
                'verified_count': int,
                'unverified_count': int,
                'not_in_cart': int,
                'tracked_items': [],
                'verified_items': [],
                'needs_verification': [],
                'estimated_total': float
            }
        """

        verified = [item for item in self.cart_state.values() if item['website_verified']]
        unverified = [item for item in self.cart_state.values() if not item['website_verified']]

        estimated_total = sum(item['subtotal'] for item in verified)

        return {
            'total_tracked': len(self.cart_state),
            'verified_count': len(verified),
            'unverified_count': len(unverified),
            'estimated_total': estimated_total,
            'tracked_items': list(self.cart_state.values()),
            'verified_items': verified,
            'needs_verification': unverified,
            'summary': f"{len(verified)} verified, {len(unverified)} pending verification"
        }

    def get_verification_checklist(self) -> str:
        """
        Get markdown checklist of items to verify on website
        """

        status = self.get_cart_status()

        markdown = "# 🛒 Rami Levy Cart Verification Checklist\n\n"
        markdown += f"**Status:** {status['summary']}\n"
        markdown += f"**Estimated Total:** ₪{status['estimated_total']:.2f}\n\n"

        markdown += "## ✅ Verified in Cart\n"
        for item in status['verified_items']:
            markdown += f"- ✅ {item['product_name']} (x{item['quantity']}) - ₪{item['subtotal']:.2f}\n"

        markdown += "\n## ⚠️ Need to Verify\n"
        for item in status['needs_verification']:
            markdown += f"- ☐ {item['product_name']} (x{item['quantity']}) - ₪{item['subtotal']:.2f}\n"
            markdown += f"   *Look for this in your cart and confirm it's there*\n"

        return markdown

    def get_session_log(self) -> List[Dict]:
        """Get log of all actions in this session"""
        return self.session_log

    def reset_cart(self) -> Dict:
        """Reset cart tracking for new session"""
        count = len(self.cart_state)
        self.cart_state = {}
        self.verified_items = {}
        self.session_log = []

        return {
            'success': True,
            'message': f"Reset cart tracking (cleared {count} items)",
            'items_cleared': count
        }

    def generate_manual_workflow(self, products: List[Dict]) -> str:
        """
        Generate step-by-step manual workflow for adding items to website cart
        """

        workflow = "# 🛒 Manual Shopping Workflow - Rami Levy\n\n"
        workflow += f"**Total Items to Add:** {len(products)}\n"
        workflow += f"**Estimated Budget:** ₪{sum(p['price'] * p.get('quantity', 1) for p in products):.2f}\n\n"

        workflow += "## Instructions\n\n"

        for i, product in enumerate(products, 1):
            workflow += f"### Step {i}: Add {product['name']}\n\n"
            workflow += f"1. Search for: **{product['name']}**\n"
            workflow += f"   - Category: {product.get('category', 'N/A')}\n"
            workflow += f"   - Quantity: {product.get('quantity', 1)}\n"
            workflow += f"   - Price: ₪{product['price']:.2f}\n\n"

            workflow += f"2. Click 'Add to Cart'\n"
            workflow += f"3. Confirm quantity is {product.get('quantity', 1)}\n"
            workflow += f"4. ✅ Confirm added to cart\n\n"

        workflow += "## Verification\n\n"
        workflow += "After adding all items:\n"
        workflow += "1. Open shopping cart\n"
        workflow += "2. Verify all items are there\n"
        workflow += "3. Confirm total price is approximately ₪" + f"{sum(p['price'] * p.get('quantity', 1) for p in products):.2f}\n"

        return workflow
