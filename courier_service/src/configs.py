"""Переменные окружения."""

import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
TIMEZONE = os.environ.get('TIMEZONE')
SECRET_KEY = os.environ.get('SECRET_KEY')

DB_HOST_TEST = os.environ.get('DB_HOST_TEST')
