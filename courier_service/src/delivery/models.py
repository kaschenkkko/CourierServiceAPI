from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, String,
                        Time, text)
from sqlalchemy.orm import relationship
from src.configs import TIMEZONE
from src.database import Base

from .mixins import AddressMixin, UserDataMixin


class Restaurant(Base, AddressMixin):
    """Таблица SQLAlchemy «Рестораны»."""

    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    opening_time = Column(Time, nullable=False, comment='Время открытия ресторана')
    closing_time = Column(Time, nullable=False, comment='Время закрытия ресторана')
    duration_delivery = Column(
        Integer, nullable=False,
        comment='Примерное время доставки заказа/в минутах'
    )

    orders = relationship('Order', back_populates='restaurant',
                          lazy='selectin', order_by='Order.id.desc()')


class Courier(Base, UserDataMixin):
    """Таблица SQLAlchemy «Курьеры»."""

    __tablename__ = 'couriers'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(
        Enum('Без заказа', 'Выполняет заказ', name='courier_status'), index=True,
        server_default='Без заказа', comment='Статус работы курьера', nullable=False
    )

    orders = relationship('Order', back_populates='courier',
                          lazy='selectin',  order_by='Order.id.desc()')


class Order(Base):
    """Таблица SQLAlchemy «Заказы»."""

    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(
        Enum('Поиск курьера', 'В пути', 'Доставлен', name='delivery_status'),
        server_default='Поиск курьера', comment='Статус доставки', nullable=False, index=True
    )
    start_time = Column(
        DateTime, comment='Время создания заказа', nullable=False,
        server_default=text(f"date_trunc('second', (now() at time zone '{TIMEZONE}'))")
    )
    end_time = Column(DateTime(timezone=True), comment='Время завершения доставки')
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), comment='ID ресторана', nullable=False)
    courier_id = Column(Integer, ForeignKey('couriers.id'), comment='ID курьера')
    user_id = Column(Integer, ForeignKey('users.id'), comment='ID пользователя', nullable=False)

    restaurant = relationship('Restaurant', back_populates='orders', lazy='selectin')
    courier = relationship('Courier', back_populates='orders', lazy='selectin')
    user = relationship('User', back_populates='orders', lazy='selectin')
