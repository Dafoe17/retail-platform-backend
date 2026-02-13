"""Unit tests for User entity"""
import pytest
from core.models import UserModel, UserProfileModel


class TestUserEntity:
    """Tests for User entity"""

    def test_user_creation(self):
        """Test creating user"""
        user = UserModel(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            role="customer",
            is_active=True,
            is_verified=False
        )

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.role == "customer"
        assert user.is_active is True
        assert user.is_verified is False

    def test_user_roles(self):
        """Test user roles"""
        customer = UserModel(
            id=1,
            email="customer@example.com",
            password_hash="hash",
            role="customer"
        )

        admin = UserModel(
            id=2,
            email="admin@example.com",
            password_hash="hash",
            role="admin"
        )

        assert customer.role == "customer"
        assert admin.role == "admin"

    def test_user_profile_relation(self):
        """Test user-profile relation"""
        from core.models import UserProfileModel

        user = UserModel(
            id=1,
            email="test@example.com",
            password_hash="hash"
        )

        profile = UserProfileModel(
            user_id=1,
            first_name="Test",
            last_name="User",
            phone="+79001234567"
        )

        assert profile.user_id == user.id
        assert profile.first_name == "Test"
        assert profile.last_name == "User"
