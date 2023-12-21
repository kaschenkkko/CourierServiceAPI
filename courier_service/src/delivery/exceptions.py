from fastapi import HTTPException, status

from .models import Courier


def raise_forbidden_if_not_courier(current_courier: Courier):
    """
    Кастомное исключение для роутеров, которые
    должны обрабатывать только запросы от курьеров.
    """

    if not isinstance(current_courier, Courier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Только курьеры имеют доступ к этому ресурсу',
        )
