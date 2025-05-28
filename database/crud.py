from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from .models import User, Order, UserRole, MenuCategory, MenuItem
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


# User CRUD Operations
def get_or_create_user(db: Session, telegram_id: int, full_name: str, phone: str = None) -> User:
    """Создает или возвращает существующего пользователя"""
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                full_name=full_name,
                phone=phone,
                role=UserRole.CUSTOMER
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Error in get_or_create_user: {e}")
        raise


def update_user_role(db: Session, user_id: int, new_role: UserRole) -> Optional[User]:
    """Обновляет роль пользователя"""
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            user.role = new_role
            db.commit()
            db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Error in update_user_role: {e}")
        return None


def search_users(db: Session, search_query: str) -> List[User]:
    """Поиск пользователей по ID, имени или телефону"""
    try:
        return db.query(User).filter(
            or_(
                User.telegram_id.cast(String).ilike(f"%{search_query}%"),
                User.full_name.ilike(f"%{search_query}%"),
                User.phone.ilike(f"%{search_query}%")
            )
        ).limit(50).all()
    except Exception as e:
        logger.error(f"Error in search_users: {e}")
        return []


# Order CRUD Operations
def create_order(db: Session, user_id: int, items: List[dict]) -> Order:
    """Создает новый заказ"""
    try:
        order = Order(
            user_id=user_id,
            items=items,
            status="created"
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        logger.error(f"Error in create_order: {e}")
        raise


def get_orders_stats(db: Session, days: int = 7) -> dict:
    """Возвращает статистику заказов за последние N дней"""
    try:
        date_from = datetime.utcnow() - timedelta(days=days)

        stats = {
            "total_orders": db.query(Order).filter(Order.created_at >= date_from).count(),
            "completed_orders": db.query(Order).filter(
                and_(
                    Order.created_at >= date_from,
                    Order.status == "completed"
                )
            ).count(),
            "total_revenue": sum(
                sum(item['price'] * item['quantity'] for item in order.items)
                for order in db.query(Order).filter(
                    and_(
                        Order.created_at >= date_from,
                        Order.status == "completed"
                    )
                ).all()
            )
        }
        return stats
    except Exception as e:
        logger.error(f"Error in get_orders_stats: {e}")
        return {}


# Admin Menu Management
def get_menu_categories(db: Session, active_only: bool = True) -> List[MenuCategory]:
    """Возвращает список категорий меню"""
    try:
        query = db.query(MenuCategory)
        if active_only:
            query = query.filter(MenuCategory.is_active == 1)
        return query.all()
    except Exception as e:
        logger.error(f"Error in get_menu_categories: {e}")
        return []


def update_menu_item(db: Session, item_id: int, **kwargs) -> Optional[MenuItem]:
    """Обновляет данные позиции меню"""
    try:
        item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if item:
            for key, value in kwargs.items():
                setattr(item, key, value)
            db.commit()
            db.refresh(item)
        return item
    except Exception as e:
        db.rollback()
        logger.error(f"Error in update_menu_item: {e}")
        return None