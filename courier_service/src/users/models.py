from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from src.database import Base
from src.delivery.mixins import AddressMixin, UserDataMixin


class User(Base, AddressMixin, UserDataMixin):
    """Таблица SQLAlchemy «Пользователи/покупатели»."""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)

    orders = relationship('Order', back_populates='user', lazy='selectin', order_by='Order.id.desc()')
