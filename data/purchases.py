import sqlalchemy
from .db_session import SqlAlchemyBase


class Purchase(SqlAlchemyBase):
    __tablename__ = 'purchases'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.String)
    products = sqlalchemy.Column(sqlalchemy.String)
    cost = sqlalchemy.Column(sqlalchemy.Float)  # без скидки
    coupons = sqlalchemy.Column(sqlalchemy.String)
    total = sqlalchemy.Column(sqlalchemy.Float)  # со скидкой
    closed = sqlalchemy.Column(sqlalchemy.DateTime)

    def __repr__(self):
        """Удобочитаемое представление."""
        return f'<Purchase {self.id} at {self.closed}> cost: {self.cost} with discount: {self.total}'

    def get_products(self):
        """Получить айдишники продуктов в виде списка целых чисел."""
        if not self.products:
            return
        return list(map(int, str(self.products).split(', ')))

    def get_coupons(self):
        """Получить айдишники купонов в виде списка целых чисел."""
        if not self.coupons:
            return
        return list(map(int, str(self.coupons).split(', ')))
