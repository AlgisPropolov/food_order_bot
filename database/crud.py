from sqlalchemy import select, update, delete, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .models import User, Order, UserRole, MenuCategory, MenuItem
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# User CRUD Operations
async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Получение пользователя по ID"""
    try:
        result = await session.execute(
            select(User)
            .where(User.telegram_id == user_id)
        )
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error in get_user_by_id: {e}")
        return None


async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        full_name: str,
        phone: str = None
) -> User:
    """Создает или возвращает существующего пользователя"""
    try:
        user = await get_user_by_id(session, telegram_id)
        if not user:
            user = User(
                telegram_id=telegram_id,
                full_name=full_name,
                phone=phone,
                role=UserRole.CUSTOMER
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user
    except Exception as e:
        await session.rollback()
        logger.error(f"Error in get_or_create_user: {e}")
        raise


async def update_user_role(
        session: AsyncSession,
        user_id: int,
        new_role: UserRole
) -> Optional[User]:
    """Обновляет роль пользователя"""
    try:
        user = await get_user_by_id(session, user_id)
        if user:
            user.role = new_role
            await session.commit()
            await session.refresh(user)
        return user
    except Exception as e:
        await session.rollback()
        logger.error(f"Error in update_user_role: {e}")
        return None


async def search_users(
        session: AsyncSession,
        search_query: str,
        limit: int = 50
) -> List[User]:
    """Поиск пользователей по ID, имени или телефону"""
    try:
        result = await session.execute(
            select(User)
            .where(
                or_(
                    User.telegram_id.cast(String).ilike(f"%{search_query}%"),
                    User.full_name.ilike(f"%{search_query}%"),
                    User.phone.ilike(f"%{search_query}%")
                )
            )
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error in search_users: {e}")
        return []


# Order CRUD Operations
async def create_order(
        session: AsyncSession,
        user_id: int,
        items: List[Dict[str, Any]],
        status: str = "created"
) -> Order:
    """Создает новый заказ"""
    try:
        order = Order(
            user_id=user_id,
            items=items,
            status=status
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order
    except Exception as e:
        await session.rollback()
        logger.error(f"Error in create_order: {e}")
        raise


async def get_orders_stats(
        session: AsyncSession,
        days: int = 7
) -> Dict[str, Any]:
    """Возвращает статистику заказов за последние N дней"""
    try:
        date_from = datetime.utcnow() - timedelta(days=days)

        # Получаем общее количество заказов
        total_orders = await session.scalar(
            select(func.count(Order.id))
            .where(Order.created_at >= date_from)
        )

        # Получаем количество завершенных заказов
        completed_orders = await session.scalar(
            select(func.count(Order.id))
            .where(
                and_(
                    Order.created_at >= date_from,
                    Order.status == "completed"
                )
            )
        )

        # Получаем общую выручку
        orders = await session.execute(
            select(Order)
            .where(
                and_(
                    Order.created_at >= date_from,
                    Order.status == "completed"
                )
            )
        )

        total_revenue = sum(
            sum(item['price'] * item['quantity'] for item in order.items)
            for order in orders.scalars()
        )

        return {
            "total_orders": total_orders or 0,
            "completed_orders": completed_orders or 0,
            "total_revenue": total_revenue or 0
        }
    except Exception as e:
        logger.error(f"Error in get_orders_stats: {e}")
        return {
            "total_orders": 0,
            "completed_orders": 0,
            "total_revenue": 0
        }


# Admin Menu Management
async def get_menu_categories(
        session: AsyncSession,
        active_only: bool = True
) -> List[MenuCategory]:
    """Возвращает список категорий меню"""
    try:
        query = select(MenuCategory)
        if active_only:
            query = query.where(MenuCategory.is_active == True)

        result = await session.execute(query)
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error in get_menu_categories: {e}")
        return []


async def update_menu_item(
        session: AsyncSession,
        item_id: int,
        **kwargs
) -> Optional[MenuItem]:
    """Обновляет данные позиции меню"""
    try:
        result = await session.execute(
            select(MenuItem)
            .where(MenuItem.id == item_id)
        )
        item = result.scalars().first()

        if item:
            for key, value in kwargs.items():
                setattr(item, key, value)
            await session.commit()
            await session.refresh(item)
        return item
    except Exception as e:
        await session.rollback()
        logger.error(f"Error in update_menu_item: {e}")
        return None