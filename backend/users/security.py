from datetime import datetime, timedelta
from typing import Dict

from jose import jwt
from passlib.context import CryptContext

from backend.configs import SECRET_KEY

ALGORITHM = 'HS256'
SECRET_KEY = SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = 240

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    """Создаём хэш пароля."""

    return pwd_context.hash(password)


def create_access_token(data: Dict[str, str]) -> str:
    """Создаём JWT-токен."""

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
