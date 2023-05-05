import asyncio
import json

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from data.types import Types
from data.products import Product
from data.purchases import Purchase
from data.coupones import Coupone


class Worker:
    """
    Реализует все взаимодействие с БД. Ебаная асинхронщина.
    """
    meta = sa.MetaData()

    def __init__(self, db_file):
        """Инициализация соединения с БД, словаря для хранения текущих покупок."""
        self.purchases = {}
        self.db_file = db_file

    async def global_init(self):
        """Соединение с БД."""
        if not self.db_file or not self.db_file.strip():
            raise Exception("Необходимо указать файл базы данных.")

        conn_str = f'postgresql+asyncpg://{self.db_file.strip()}?check_same_thread=False'
        print(f'INFO: Getting access to the DB file with path {conn_str}')
        self.engine = create_async_engine(conn_str, echo=False)

        self.async_session = async_sessionmaker(self.engine)

        async with self.engine.begin() as conn:
            await conn.run_sync(self.meta.create_all)

        with open('ext_data/data.json', encoding='utf-8') as jsfile:
            data = json.load(jsfile)
        async with self.async_session() as db_sess:
            for tp in data:
                typp = Types(title=tp)
                db_sess.add(typp)
                db_sess.commit()
                for p in data[tp]:
                    prod = Product(title=p[0], price=p[1], type=tp)
                    db_sess.add(prod)
            db_sess.commit()

    async def commit_all(self):
        """Запомнить все изменения в таблице (коммит для всех активных Purchase)"""
        async with self.async_session() as db_sess:
            await db_sess.commit()

    async def get_types(self):
        """Получаем названия типов продуктов из таблицы."""
        async with self.async_session() as db_sess:
            tps = await db_sess.query(Types).all()
        return list(map(lambda x: x.title, tps))

    async def get_type_by_title(self, title):
        """Получить объект Types по его названию."""
        async with self.async_session() as db_sess:
            return await db_sess.query(Types).filter(Types.title == title).first()

    async def get_product_by_title(self, title):
        """Получить объект Product по его названию."""
        async with self.async_session() as db_sess:
            return await db_sess.query(Product).filter(Product.title == title).first()

    async def get_products(self, tp):
        """Получить список названий продуктов переданного типа."""
        async with self.async_session() as db_sess:
            titles = await db_sess.query(Product).filter(Product.type == tp)
        return list(map(lambda x: x.title, titles))

    async def purchase_history(self, user_id=0):
        """
        Загрузить историю покупок и вернуть в удобочитаемом виде.
        Необязательный параметр user_id - если мы хотим получить историю только одного пользователя.
        """
        async with self.async_session() as db_sess:
            if not user_id:
                pch = await db_sess.query(Purchase).all()
        return list(map(str, pch))

    async def open_purchase(self, user_id):
        """Открыть корзину, начать историю покупок. Все активные покупки хранятся в атрибуте
        класса, а тут происходит их инициализация или загрузка незакрытых из БД."""
        async with self.async_session() as db_sess:
            found = await db_sess.query(Purchase).filter(Purchase.user_id == int(user_id),
                                                         not Purchase.closed).first()
            if not found:
                pur = Purchase(user_id=int(user_id))
                db_sess.add(pur)
            else:
                pur = found
        self.purchases[user_id] = pur
        return pur

    async def add_product(self, user_id, product):
        """Добавить продукт в корзину. Если корзины нет, мы ее инициализируем или достаем из БД."""
        if user_id not in self.purchases:
            purchase = await self.open_purchase(user_id)
        else:
            purchase = self.purchases[user_id]
        prod = await self.get_product_by_title(product)
        prods = purchase.get_products()
        if not prods:
            purchase.products = str(prod.id)
        else:
            purchase.products += ', ' + str(prod.id)

    async def delete_product(self, user_id, product):
        """Удалить продукт из корзины. Если корзины нет, ищем в БД."""
        pass

    async def add_coupon(self, user_id, coupon_id):
        """Добавляем купон. Предполагается, что купоны пользователь вводит по их id, тогда запоминаем
        его в активной покупке."""
        pass

    async def count_cost(self, user_id):
        """Высчитать цену с учетом скидок по купонам. Выставление счета (вернуть число)."""
        pass

    async def close_purchase(self, user_id):
        """Закрыть покупку - оплата прошла, закрываем корзину и записываем в БД в качестве истории
        покупок."""
        pass


worker = Worker('db/test_shop.db')
asyncio.run(asyncio.create_task(worker.global_init()))
