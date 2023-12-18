from sqlalchemy import CheckConstraint, Column, String


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

    Предоставляет общие поля с информацией:
        - name (str): Имя.
        - surname (str): Фамилия.
        - phone_number (str): Номер телефона.
    """

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint(
            "phone_number ~ '^((8|\\+7)[\\- ]?)?(\\(?\\d{3}\\)?[\\- ]?)?[\\d\\- ]{7,10}$'",
            name='check_phone_number'
        ),
    )
