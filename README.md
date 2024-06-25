<div id="header" align="center">
  <h1>Courier Service API</h1>
  <img src="https://img.shields.io/badge/Python-3.10.11-F8F8FF?style=for-the-badge&logo=python&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/FastAPI-0.105.0-F8F8FF?style=for-the-badge&logo=FastAPI&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/PostgreSQL-555555?style=for-the-badge&logo=postgresql&logoColor=F5F5DC">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0.23-F8F8FF?style=for-the-badge&logo=SQLAlchemy&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/Docker-555555?style=for-the-badge&logo=docker&logoColor=2496ED">
</div>

# Документация API
Courier Service - [API redoc](https://kaschenkkko.github.io/CourierServiceAPI/)

# Техническое задание проекта:

Необходимо разработать прототип API сервиса курьерской доставки.

### Что должен включать в себя сервис:

- API методы:
  - Метод расчета стоимости доставки
  - Метод создания заказа
  - Метод получения информации о заказе
  - Метод получение списка заказов
- Сервис должен уметь взаимодействовать с клиентом при помощи REST API или JSON RPC запросов
- В сервисе должен быть реализован RateLimit с ограничением 10 RPM

### Дополнительная информация:

- Логику логистики реализовывать не обязательно. На усмотрение разработчика можно использовать mock ответов.  Цель разработать API сервис, а не полноценный сервис курьерской доставки.
-	Сервис разрабатывается для “Внутригородской доставки”
- Приветствуется покрытие кода тестами
- Приветствуется наличие документации с описанием работы API сервиса
- Приветствуется использования систем хранения данных Redis, PostgreSQL, mongoDB

### Контекст задачи:

В процессе работы с API будут участвовать 3 основных лица:

- Покупатель. Для него важно рассчитать стоимость доставки от адреса отправки до адреса получения (при этом адрес отправки у нас занесен в систему продавцом), для этого он использует метод "Расчет стоимостей доставки". После расчета стоимости, покупатель принимает решение об оформлении заказа с доставкой. Когда пользователь оформляет заказ, вызывается метод "Создать заказ". После чего, покупатель ожидает доставки своего товара.
- Продавец. Должен иметь возможность видеть весь список заказов, оформленных покупателями. Для этого доступен метод "Получить список заказов". Также для продавца важно иметь возможность посмотреть детальную информацию по заказу, чтобы передать заказ курьеру для доставки. Для этого доступен метод “Получить информацию о заказе”.
- Курьер с мобильным приложением. Должен иметь возможность просматривать информацию о заказе: какой товар, куда и когда нужно доставить. Для этого мобильное приложение будет вызывать метод "Получить информацию о заказе".

# Запуск проекта:

- Клонируйте репозиторий.
- Перейдите в папку **infra** и создайте в ней файл **.env** с переменными окружения:
  ```
  DB_HOST=db
  DB_PORT=5432
  DB_NAME=postgres
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=postgres

  TIMEZONE='Asia/Yekaterinburg'
  SECRET_KEY=secretsecret
  TZ='Asia/Yekaterinburg'

  PGADMIN_DEFAULT_EMAIL=user@gmail.ru
  PGADMIN_DEFAULT_PASSWORD=user_password

  DB_HOST_TEST=db_test
  ``` 
- Из папки **infra** запустите docker-compose:
  ```
  ~$ docker-compose up -d --build
  ```
- В контейнере **backend** выполните миграции:
  ```
  ~$ docker-compose exec backend alembic upgrade head
  ```
- Для запуска тестов выполните команду:
  ```
  ~$ docker-compose exec backend pytest -v tests/
  ```

Документация к API будет доступна по url-адресу [127.0.0.1/redoc](http://127.0.0.1/redoc)

Админка будет доступна по url-адресу [127.0.0.1/admin](http://127.0.0.1/admin)
