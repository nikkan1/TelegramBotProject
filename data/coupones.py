import sqlalchemy
from .db_session import SqlAlchemyBase


class Coupone(SqlAlchemyBase):
    __tablename__ = 'coupones'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    types = sqlalchemy.Column(sqlalchemy.String)
    discount = sqlalchemy.Column(sqlalchemy.Integer)

    def get_types(self):
        return list(map(int, str(self.types).split(', ')))
