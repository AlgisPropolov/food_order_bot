from sqlalchemy.orm import Session
from .models import User, Order

def get_or_create_user(db: Session, telegram_id: int, full_name: str):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, full_name=full_name)
        db.add(user)
        db.commit()
    return user

def create_order(db: Session, user_id: int, items: list):
    order = Order(user_id=user_id, items=items)
    db.add(order)
    db.commit()
    return order