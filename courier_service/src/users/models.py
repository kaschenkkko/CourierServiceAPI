from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base
from src.delivery.mixins import AddressMixin, UserDataMixin
from src.delivery.models import Order

from .security import pwd_context


class User(Base, AddressMixin, UserDataMixin):
    """Таблица SQLAlchemy «Пользователи/покупатели»."""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)

    orders = relationship('Order', back_populates='user', lazy='selectin', order_by='Order.id.desc()')

    def verify_password(self, password: str) -> bool:
        """
        Проверяем соответствие введённого пароля и хэшированного пароля пользователя,
        хранящегося в базе данных.
        """

        return pwd_context.verify(password, self.hashed_password)
