"""SQLAlchemy Models"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, BigInteger, CheckConstraint
from sqlalchemy.orm import relationship
from typing import Optional
from sqlalchemy.sql import func

from .database import Base


# Users Module
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="customer")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    profile = relationship("UserProfileModel", back_populates="user", uselist=False)
    refresh_tokens = relationship("RefreshTokenModel", back_populates="user")


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(500))
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("UserModel", back_populates="profile")


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    token_id = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(String(255))

    user = relationship("UserModel", back_populates="refresh_tokens")


# Products Module
class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("CategoryModel", remote_side=[id], foreign_keys=[parent_id])
    children = relationship("CategoryModel", back_populates="parent", overlaps="parent")
    products = relationship("ProductModel", back_populates="category")


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    price = Column(BigInteger, nullable=False)  # in kopecks
    stock = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    images = Column(Text, default="[]")  # JSON as text
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("CategoryModel", back_populates="products")


# Cart Module
class CartModel(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(BigInteger, nullable=False)  # in kopecks
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    cart = relationship("CartModel", back_populates="items")
    product = relationship("ProductModel")


# Orders Module
class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    subtotal = Column(BigInteger, nullable=False)
    shipping_cost = Column(BigInteger, nullable=False, default=0)
    discount = Column(BigInteger, nullable=False, default=0)
    tax = Column(BigInteger, nullable=False, default=0)
    total = Column(BigInteger, nullable=False)

    # Shipping address
    recipient_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    country = Column(String(100))
    city = Column(String(100), nullable=False)
    street = Column(String(255), nullable=False)
    building = Column(String(20), nullable=False)
    apartment = Column(String(20))
    postal_code = Column(String(20), nullable=False)

    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistoryModel", back_populates="order", cascade="all, delete-orphan")


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String(255), nullable=False)
    product_slug = Column(String(255))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(BigInteger, nullable=False)  # in kopecks
    subtotal = Column(BigInteger, nullable=False)

    order = relationship("OrderModel", back_populates="items")


class OrderStatusHistoryModel(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)
    comment = Column(Text)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("OrderModel", back_populates="status_history")
