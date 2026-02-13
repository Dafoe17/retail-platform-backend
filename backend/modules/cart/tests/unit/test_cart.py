"""Unit tests for Cart entity"""
import pytest
from decimal import Decimal
from core.models import CartModel, CartItemModel


class TestCartEntity:
    """Tests for Cart entity"""

    def test_cart_creation(self):
        """Test creating cart"""
        cart = CartModel(id=1, user_id=1)

        assert cart.id == 1
        assert cart.user_id == 1

    def test_cart_without_user(self):
        """Test cart without user (anonymous)"""
        cart = CartModel(id=1, user_id=None)

        assert cart.id == 1
        assert cart.user_id is None

    def test_cart_item_creation(self):
        """Test creating cart item"""
        item = CartItemModel(
            id=1,
            cart_id=1,
            product_id=10,
            quantity=2,
            unit_price=19990  # 199.90 in kopecks
        )

        assert item.id == 1
        assert item.cart_id == 1
        assert item.product_id == 10
        assert item.quantity == 2
        assert item.unit_price == 19990

    def test_cart_item_subtotal_calculation(self):
        """Test cart item subtotal calculation"""
        # quantity * unit_price
        # 3 * 19990 = 59970 (599.70)
        item = CartItemModel(
            id=1,
            cart_id=1,
            product_id=10,
            quantity=3,
            unit_price=19990
        )

        expected_subtotal = 3 * 19990  # 59970
        assert item.quantity * item.unit_price == expected_subtotal

    def test_cart_total_calculation(self):
        """Test cart total calculation"""
        # Item 1: 2 * 100.00 = 200.00
        # Item 2: 1 * 50.00 = 50.00
        # Total: 250.00 = 25000 kopecks

        item1 = CartItemModel(
            id=1,
            cart_id=1,
            product_id=1,
            quantity=2,
            unit_price=10000  # 100.00
        )

        item2 = CartItemModel(
            id=2,
            cart_id=1,
            product_id=2,
            quantity=1,
            unit_price=5000  # 50.00
        )

        total = (item1.quantity * item1.unit_price +
                item2.quantity * item2.unit_price)

        expected_total = 25000  # 250.00
        assert total == expected_total

    def test_cart_items_count(self):
        """Test cart items count"""
        items = [
            CartItemModel(
                id=i,
                cart_id=1,
                product_id=i,
                quantity=i,
                unit_price=1000
            )
            for i in range(1, 4)  # quantity: 1, 2, 3
        ]

        total_items_count = sum(item.quantity for item in items)
        assert total_items_count == 6  # 1 + 2 + 3
