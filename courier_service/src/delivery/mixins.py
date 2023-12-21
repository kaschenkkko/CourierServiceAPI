from sqlalchemy import CheckConstraint, Column, String
from src.users.security import pwd_context


class AddressMixin:
    """Базовый класс для моделей SQLAlchemy, в которых присутствует адрес.

    Предоставляет общие поля адреса, такие как:
        - city (str): Город.
        - street (str): Улица.
        - house_number (str): Номер дома.
    """

    city = Column(String, server_default='Тюмень', nullable=False)
    street = Column(String, nullable=False)
    house_number = Column(String, nullable=False)


class UserDataMixin:
    """Базовый класс для моделей SQLAlchemy, для покупателей/курьеров.

    Предоставляет общие поля с информацией, такие как:
        - name (str): Имя.
        - surname (str): Фамилия.
        - phone_number (str): Номер телефона.
        - hashed_password (str): Хэш пароля.

    Ограничение:
        - Поле phone_number должно соответствовать регулярному выражению,
          проверяющему формат номера телефона.
    """

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    def verify_password(self, password: str) -> bool:
        """
        Проверяем соответствие введённого пароля и хэшированного пароля пользователя,
        хранящегося в базе данных.
        """

        return pwd_context.verify(password, self.hashed_password)

    __table_args__ = (
        CheckConstraint(
            "phone_number ~ '^((8|\\+7)[\\- ]?)?(\\(?\\d{3}\\)?[\\- ]?)?[\\d\\- ]{7,10}$'",
            name='check_phone_number'
        ),
    )
