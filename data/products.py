import sqlalchemy
from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('types.id'))
    title = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
