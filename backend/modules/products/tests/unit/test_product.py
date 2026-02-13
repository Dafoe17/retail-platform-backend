"""Unit tests for Product entity"""
import pytest
from decimal import Decimal
from core.models import ProductModel, CategoryModel


class TestProductEntity:
    """Tests for Product entity"""

    def test_product_creation(self):
        """Test creating product"""
        product = ProductModel(
            id=1,
            name="Test Product",
            slug="test-product",
            description="Test description",
            price=19990,  # 199.90 in kopecks
            stock=50,
            is_active=True
        )

        assert product.id == 1
        assert product.name == "Test Product"
        assert product.slug == "test-product"
        assert product.price == 19990
        assert product.stock == 50
        assert product.is_active is True

    def test_product_price_in_kopecks(self):
        """Test price in kopecks"""
        # 999.99 rub = 99999 kopecks
        product = ProductModel(
            id=1,
            name="Product",
            slug="product",
            price=99999,
            stock=10
        )

        assert product.price == 99999

    def test_product_category_relation(self):
        """Test product-category relation"""
        category = CategoryModel(
            id=1,
            name="Electronics",
            slug="electronics"
        )

        product = ProductModel(
            id=1,
            name="Phone",
            slug="phone",
            price=50000,
            stock=20,
            category_id=1
        )

        assert product.category_id == category.id

    def test_product_images_json(self):
        """Test images as JSON"""
        import json

        images = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
        product = ProductModel(
            id=1,
            name="Product",
            slug="product",
            price=10000,
            stock=10,
            images=json.dumps(images)
        )

        assert product.images is not None

    def test_product_availability(self):
        """Test product availability"""
        # Product in stock
        product_in_stock = ProductModel(
            id=1,
            name="Product",
            slug="product",
            price=10000,
            stock=10,
            is_active=True
        )

        # Product out of stock
        product_out_of_stock = ProductModel(
            id=2,
            name="Product 2",
            slug="product-2",
            price=10000,
            stock=0,
            is_active=True
        )

        # Inactive product
        product_inactive = ProductModel(
            id=3,
            name="Product 3",
            slug="product-3",
            price=10000,
            stock=10,
            is_active=False
        )

        assert product_in_stock.stock > 0
        assert product_out_of_stock.stock == 0
        assert product_inactive.is_active is False
