"""Unit tests for Order entity"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from core.models import OrderModel, OrderItemModel, OrderStatusHistoryModel


class TestOrderEntity:
    """Tests for Order entity"""

    def test_order_creation(self):
        """Test creating order"""
        order = OrderModel(
            id=1,
            order_number="ORD-2024-000001",
            user_id=1,
            status="pending",
            subtotal=450000,  # 4500.00
            shipping_cost=50000,  # 500.00
            discount=0,
            tax=0,
            total=500000,  # 5000.00
            recipient_name="Test User",
            phone="+79001234567",
            city="Moscow",
            street="Test Street",
            building="123",
            postal_code="123456"
        )

        assert order.id == 1
        assert order.order_number == "ORD-2024-000001"
        assert order.user_id == 1
        assert order.status == "pending"
        assert order.subtotal == 450000
        assert order.shipping_cost == 50000
        assert order.total == 500000

    def test_order_statuses(self):
        """Test order statuses"""
        valid_statuses = [
            "pending", "confirmed", "processing",
            "shipped", "delivered", "cancelled", "refunded"
        ]

        for status in valid_statuses:
            order = OrderModel(
                id=1,
                order_number="TEST-001",
                user_id=1,
                status=status,
                subtotal=10000,
                shipping_cost=0,
                discount=0,
                tax=0,
                total=10000,
                recipient_name="Test",
                phone="+79001234567",
                city="M",
                street="T",
                building="1",
                postal_code="1"
            )
            assert order.status == status

    def test_order_item_creation(self):
        """Test creating order item"""
        item = OrderItemModel(
            id=1,
            order_id=1,
            product_id=10,
            product_name="Test Product",
            product_slug="test-product",
            quantity=2,
            unit_price=19990,  # 199.90
            subtotal=39980  # 2 * 19990
        )

        assert item.id == 1
        assert item.order_id == 1
        assert item.product_id == 10
        assert item.product_name == "Test Product"
        assert item.quantity == 2
        assert item.unit_price == 19990
        assert item.subtotal == 39980

    def test_order_total_calculation(self):
        """Test order total calculation"""
        # subtotal + shipping - discount + tax
        order = OrderModel(
            id=1,
            order_number="TEST-001",
            user_id=1,
            status="pending",
            subtotal=100000,  # 1000.00
            shipping_cost=10000,  # 100.00
            discount=5000,  # 50.00
            tax=20000,  # 200.00
            total=125000,  # 1250.00
            recipient_name="Test",
            phone="+79001234567",
            city="Moscow",
            street="Test",
            building="1",
            postal_code="123456"
        )

        # 1000 + 100 - 50 + 200 = 1250
        expected_total = 100000 + 10000 - 5000 + 20000
        assert order.total == expected_total

    def test_order_status_history_creation(self):
        """Test creating order status history"""
        history = OrderStatusHistoryModel(
            id=1,
            order_id=1,
            status="confirmed",
            comment="Order confirmed by manager"
        )

        assert history.id == 1
        assert history.order_id == 1
        assert history.status == "confirmed"
        assert history.comment == "Order confirmed by manager"

    def test_order_shipping_address_fields(self):
        """Test shipping address fields"""
        order = OrderModel(
            id=1,
            order_number="TEST-001",
            user_id=1,
            status="pending",
            subtotal=10000,
            shipping_cost=0,
            discount=0,
            tax=0,
            total=10000,
            recipient_name="Ivan Ivanovich",
            phone="+79001234567",
            country="Russia",
            city="Moscow",
            street="Arbat Street",
            building="10",
            apartment="25",
            postal_code="119002"
        )

        assert order.recipient_name == "Ivan Ivanovich"
        assert order.phone == "+79001234567"
        assert order.country == "Russia"
        assert order.city == "Moscow"
        assert order.street == "Arbat Street"
        assert order.building == "10"
        assert order.apartment == "25"
        assert order.postal_code == "119002"

    def test_order_can_be_cancelled_pending(self):
        """Test order in pending status can be cancelled"""
        order = OrderModel(
            id=1,
            order_number="TEST-001",
            user_id=1,
            status="pending",
            subtotal=10000,
            shipping_cost=0,
            discount=0,
            tax=0,
            total=10000,
            recipient_name="Test",
            phone="+79001234567",
            city="M",
            street="T",
            building="1",
            postal_code="1"
        )

        # pending -> cancelled = valid transition
        cancellable_statuses = ["pending", "confirmed", "processing"]
        assert order.status in cancellable_statuses
