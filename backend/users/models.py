from sqlalchemy import Column, Integer, String

from backend.database.options import Base

from .security import pwd_context


class User(Base):
    """Таблица SQLAlchemy «Пользователи»."""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def verify_password(self, password: str) -> bool:
        """
        Проверяем соответствие введённого пароля и хэшированного пароля пользователя,
        хранящегося в базе данных.
        """

        return pwd_context.verify(password, self.hashed_password)
