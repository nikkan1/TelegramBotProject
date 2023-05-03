"""
Создание клавиатур и списков для взаимодействия с ними.
"""
from config import DB_FILE
from db_worker import Worker
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


def new_keyboard_making():
    """Создать клавиатуры для магазина - клавиатура типов товаров, купонов и самих товаров.
    Вернуть готовые списки-клавиатуры."""
    worker = Worker(DB_FILE)
    types = worker.get_types()

    tps_keyboards = list(map(lambda x: [(InlineKeyboardButton(x, callback_data=x))], types))
    tps_keyboards.append([InlineKeyboardButton('Вернуться', callback_data='back')])
    prod_keyboards = {}
    for tp in types:
        prod_keyboards[tp] = []
        for prod in worker.get_products(tp, only_title=False):
            prod_keyboards[tp].append(
                [InlineKeyboardButton(f'{prod.title} -- {prod.price}', callback_data=prod.title)])
        prod_keyboards[tp].append([InlineKeyboardButton('Вернуться', callback_data='back')])
    tps_markup = InlineKeyboardMarkup(tps_keyboards)
    product_markups = {x[0]: InlineKeyboardMarkup(x[1]) for x in prod_keyboards.items()}

    coupons = worker.get_coupons()
    coup_keyboard = list(map(lambda x: [InlineKeyboardButton(coupons[x], callback_data=str(x + 1))],
                             range(len(coupons))))
    coup_keyboard.append([InlineKeyboardButton('Вернуться', callback_data='back')])
    coup_markup = InlineKeyboardMarkup(coup_keyboard)

    return tps_markup, product_markups, coup_markup


# начальная клавиатура с доступом в магазин и профиль и кнопкой поддержки
reply_keyboard = [[
    InlineKeyboardButton('Магазин', callback_data='shop'),
    InlineKeyboardButton('Профиль', callback_data='profile'),
    InlineKeyboardButton('Поддержка', callback_data='support')
]]
# клавиатура магазина - перейти к категориям товаров, получить счет, оплатить, вернуться
shop_keyboard = [[
    InlineKeyboardButton('Категории продуктов', callback_data='types'),
    InlineKeyboardButton('Получить счет', callback_data='check')
], [
    InlineKeyboardButton('Оплатить', callback_data='pay'),
    InlineKeyboardButton('Вернуться', callback_data='back')
]]
# клавиатура профиля - посмотреть историю покупок, активировать купон, вернуться
profile_keyboard = [[InlineKeyboardButton('История покупок', callback_data='purchase_history')],
                    [InlineKeyboardButton('Активировать купон', callback_data='coupons')],
                    [InlineKeyboardButton('Вернуться', callback_data='back')]]
# клавиатура внутри магазина - купить товар или вернуться к выбору
small_keyboard = [[InlineKeyboardButton('В корзину', callback_data='add_product')],
                  [InlineKeyboardButton('Вернуться', callback_data='back')]]

# создание целых клавиатур из кнопок
reply_markup = InlineKeyboardMarkup(reply_keyboard)
shop_markup = InlineKeyboardMarkup(shop_keyboard)
profile_markup = InlineKeyboardMarkup(profile_keyboard)
small_markup = InlineKeyboardMarkup(small_keyboard)

types_markup, prod_markup, coup_markup = new_keyboard_making()
