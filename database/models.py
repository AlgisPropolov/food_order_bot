from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    """Роли пользователей"""
    CUSTOMER = "customer"
    MANAGER = "manager"
    ADMIN = "admin"
    COURIER = "courier"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    orders = relationship("Order", back_populates="user")

    def is_admin(self):
        return self.role == UserRole.ADMIN

    def has_management_access(self):
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    items = Column(JSON, nullable=False)
    status = Column(String(20), default="created")
    iiko_order_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    courier = relationship("User", foreign_keys=[courier_id])


class MenuCategory(Base):
    """Категории меню для админ-панели"""
    __tablename__ = "menu_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    iiko_id = Column(String(50), nullable=False, unique=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class MenuItem(Base):
    """Позиции меню для админ-панели"""
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(300))
    price = Column(Integer, nullable=False)
    iiko_id = Column(String(50), nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey("menu_categories.id"))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    category = relationship("MenuCategory")