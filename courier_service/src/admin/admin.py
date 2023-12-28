import pytz
from sqladmin import Admin, ModelView
from src.configs import TIMEZONE
from src.delivery.models import Courier, Order, Restaurant
from src.users.models import User


def setup_admin(app, engine):
    admin = Admin(app, engine, title='Админ Панель')

    class UserAdmin(ModelView, model=User):
        """Отображение пользователей/покупателей."""

        name = 'Покупатель'
        name_plural = 'Покупатели'

        column_searchable_list = [
            User.phone_number
        ]
        column_list = [
            User.id,
            User.name,
            User.surname,
            User.phone_number,
            User.city,
            User.street,
            User.house_number,
        ]

    class RestaurantAdmin(ModelView, model=Restaurant):
        """Отображение ресторанов."""

        name = 'Ресторан'
        name_plural = 'Рестораны'

        column_labels = {
            Restaurant.opening_time: 'Время открытия ресторана',
            Restaurant.closing_time: 'Время закрытия ресторана',
            Restaurant.duration_delivery: 'Примерное время доставки заказа/в минутах',
        }
        column_searchable_list = [
            Restaurant.name
        ]
        column_list = [
            Restaurant.id,
            Restaurant.name,
            Restaurant.opening_time,
            Restaurant.closing_time,
            Restaurant.duration_delivery,
            Restaurant.city,
            Restaurant.street,
            Restaurant.house_number,
        ]

    class CourierAdmin(ModelView, model=Courier):
        """Отображение курьеров."""

        name = 'Курьер'
        name_plural = 'Курьеры'

        column_searchable_list = [
            Courier.phone_number
        ]
        column_labels = {
            Courier.status: 'Статус работы курьера',
        }
        column_list = [
            Courier.id,
            Courier.name,
            Courier.surname,
            Courier.phone_number,
            Courier.status,
        ]

    class OrderAdmin(ModelView, model=Order):
        """Отображение заказов."""

        name = 'Заказ'
        name_plural = 'Заказы'

        def end_time_taking_timezone(self, value):
            """Получаем время завершения доставки с учётом часового пояса."""

            return self.end_time.astimezone(pytz.timezone(TIMEZONE)) if value else ''

        column_labels = {
            Order.status: 'Статус доставки',
            Order.start_time: 'Время создания заказа',
            Order.end_time: 'Время завершения доставки.'
        }
        column_formatters = {
            'end_time': end_time_taking_timezone
        }
        column_list = [
            Order.id,
            Order.status,
            Order.start_time,
            Order.end_time,
            Order.restaurant_id,
            Order.courier_id,
            Order.user_id,
        ]

    admin.add_view(UserAdmin)
    admin.add_view(RestaurantAdmin)
    admin.add_view(CourierAdmin)
    admin.add_view(OrderAdmin)
