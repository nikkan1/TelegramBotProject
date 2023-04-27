"""
Реализует класс-менеджер, обращающийся с БД.
"""
import json  # нужен для изначальной загрузки данных в БД при инициализации

import datetime
from data.types import Types
from data.products import Product
from data.purchases import Purchase
from data.coupones import Coupone
from data.db_session import create_session, global_init


class Worker:
    """
    Отвечает за взаимодействие с БД.
    """
    def __init__(self, db_file: str):
        self.purchases = {}
        global_init(db_file)
        self.session = create_session()

    def temp_load(self):
        """Единоразовая подгрузка базы данных из файла при ее инициализации. Может еще пригодиться"""
        with open('data.json', encoding='utf-8') as jsfile:
            data = json.load(jsfile)

        for tp in data['types']:
            typp = Types(title=tp)
            self.session.add(typp)
            self.session.commit()
            for p in data['types'][tp]:
                prod = Product(title=p[0], price=p[1], type=typp.id)
                self.session.add(prod)

        for coup in data['coupons']:
            coupon = Coupone()
            coupon.types = coup[0]
            coupon.discount = coup[1]
            self.session.add(coupon)

        self.session.commit()

    def get_types(self):
        """Получаем названия типов продуктов из таблицы."""
        return list(map(lambda x: x.title, self.session.query(Types).all()))

    def get_products(self, tp='<no-type>'):
        """Получить список названий продуктов переданного типа."""
        if tp == '<no-type>':
            return list(map(lambda x: x.title, self.session.query(Product).all()))
        type_id = self.get_type_by_title(tp)
        return list(map(lambda x: x.title,
                        self.session.query(Product).filter(Product.type == type_id)))

    def get_type_by_title(self, title: str):
        """Получить объект Types по его названию."""
        return self.session.query(Types).filter(Types.title == title).first()

    def get_product_by_title(self, title: str):
        """Получить объект Product по его названию."""
        return self.session.query(Product).filter(Product.title == title).first()

    def purchase_history(self, user_id=0):
        """
        Загрузить историю покупок и вернуть в удобочитаемом виде.
        Необязательный параметр user_id - если мы хотим получить историю только одного пользователя.
        """
        if not user_id:
            return list(map(str, self.session.query(Purchase).filter(Purchase.closed.isnot(None))))
        return list(map(str, self.session.query(Purchase).filter(Purchase.closed.isnot(None),
                                                                 Purchase.user_id == user_id)))

    def open_purchase(self, user_id: int):
        """Открыть корзину, начать историю покупок. Все активные покупки хранятся в атрибуте
        класса, а тут происходит их инициализация или загрузка незакрытых из БД."""
        if self.purchases.get(user_id):
            return self.purchases[user_id]
        found = self.session.query(Purchase).filter(Purchase.user_id == user_id,
                                                    Purchase.closed.is_(None)).first()
        if not found:
            purchase = Purchase()
            purchase.user_id = user_id
            self.session.add(purchase)
        else:
            purchase = found
        self.purchases[user_id] = purchase
        self.session.commit()
        return purchase

    def add_product(self, user_id: int, product: str):
        """Добавить продукт в корзину. Сначала получить корзину методом open_purchase, чтобы не
        возникло накладок (если корзина не закрыта и в БД или не существует вовсе)."""
        purchase = self.open_purchase(user_id)
        prod = self.get_product_by_title(product)
        if not prod:
            return
        print(f'added {product} with price {prod.price}')
        prod_id = str(prod.id)
        if not purchase.products:
            purchase.products = prod_id
        else:
            purchase.products += ', ' + prod_id
        self.session.commit()

    def delete_product(self, user_id: int, product: str):
        """Удалить продукт из корзины. Также в первую очередь запускает open_purchase.
        :return True если предмет успешно удален иначе False (корзина пуста или его там нет)"""
        purchase = self.open_purchase(user_id)
        prods = purchase.get_products()
        need = self.get_product_by_title(product)
        if not prods or need.id not in prods:
            return False
        print(f'removed {product} with price {need.price}')
        prods.remove(need.id)
        purchase.products = ', '.join(list(map(str, prods)))
        self.session.commit()
        return True

    def add_coupon(self, user_id: int, coupon_id: str):
        """Добавляем купон. Предполагается, что купоны пользователь вводит по их id, тогда запоминаем
        его в активной покупке."""
        purchase = self.open_purchase(user_id)
        if not purchase.coupons:
            purchase.coupons = coupon_id
        else:
            purchase.coupons += ', ' + coupon_id
        self.session.commit()

    def count_cost(self, user_id: int):
        """Высчитать цену с учетом скидок по купонам. Выставление счета (вернуть число)."""
        purchase = self.open_purchase(user_id)
        # получить список продуктов и посчитать их цену без купонов
        prod_ids = purchase.get_products()
        if not prod_ids:
            purchase.cost = purchase.total = 0
            self.session.commit()
            return 0
        products = self.session.query(Product).filter(Product.id.in_(prod_ids))
        purchase.cost = sum(map(lambda x: x.price, products))
        # если есть купоны, иначе цена будет посчитана неверно
        if purchase.coupons:
            # найти типы со скидкой по купонам и посчитать цену со скидкой. скидки не суммируются
            coup_ids = purchase.get_coupons()
            coupons = self.session.query(Coupone).filter(Coupone.id.in_(coup_ids))
            type_ids = set()
            discounts = {}
            for coup in coupons:
                discounts[coup] = coup.get_types()
                type_ids = type_ids | set(coup.get_types())
            # применить скидку
            summ = 0
            for prod in products:
                if prod.type in type_ids:
                    discount = max(filter(lambda x: prod.type in discounts[x], discounts),
                                   key=lambda x: x.discount).discount
                    price = round(prod.price * (100 - discount) / 100)
                    print(f'к товару {prod.title} применена скидка {discount}:\n'
                          f'{prod.price} ----------- {price}')
                    summ += price
                else:
                    summ += prod.price
            purchase.total = summ
        else:
            purchase.total = purchase.cost
        self.session.commit()
        return purchase.total

    def close_purchase(self, user_id: int):
        """Закрыть покупку - оплата прошла, закрываем корзину и записываем в БД в качестве истории
        покупок."""
        purchase = self.open_purchase(user_id)
        purchase.closed = datetime.datetime.now()
        self.session.commit()
        print(purchase, '-' * 10, 'just closed')
        del self.purchases[user_id]
