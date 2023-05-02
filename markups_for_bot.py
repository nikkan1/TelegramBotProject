"""
Создание клавиатур и списков для взаимодействия с ними.
"""
from db_worker import Worker
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


def new_keyboard_making():
    worker = Worker('db/pre_release_shop.db')
    types = worker.get_types()

    tps_keyboards = list(map(lambda x: [InlineKeyboardButton(x, callback_data=x)],
                             map(lambda x: x.title, types)))
    tps_keyboards.append(InlineKeyboardButton('Вернуться', callback_data='back'))
    prod_keyboards = {}
    for tp in map(lambda x: x.title, types):
        prod_keyboards[tp] = []
        for prod in worker.get_products(tp, only_title=False):
            prod_keyboards[tp].append(
                InlineKeyboardButton(f'{prod.title}\n{prod.price}', callback_data=prod.title))
        prod_keyboards[tp].append(InlineKeyboardButton('Вернуться', callback_data='back'))
    tps_markup = InlineKeyboardMarkup(tps_keyboards)
    product_markups = {x[0]: InlineKeyboardMarkup(x[1]) for x in prod_keyboards.items()}

    coupons = worker.get_coupons()
    coup_keyboard = list(map(lambda x: [InlineKeyboardButton(coupons[x], callback_data=x)],
                             range(len(coupons))))
    coup_keyboard.append(InlineKeyboardButton('Вернуться', callback_data='back'))
    coup_markup = InlineKeyboardMarkup(coup_keyboard)

    return tps_markup, product_markups, coup_markup


reply_keyboard = [[
    InlineKeyboardButton('Магазин', callback_data='shop'),
    InlineKeyboardButton('Профиль', callback_data='profile'),
    InlineKeyboardButton('Поддержка', callback_data='support')
]]
shop_keyboard = [[
    InlineKeyboardButton('Категории продуктов', callback_data='types'),
    InlineKeyboardButton('Получить счет', callback_data='check')
], [
    InlineKeyboardButton('Оплатить', callback_data='pay'),
    InlineKeyboardButton('Вернуться', callback_data='back')
]]
profile_keyboard = [[InlineKeyboardButton('История покупок', callback_data='purchase_history')],
                    [InlineKeyboardButton('Активировать купон', callback_data='coupons')],
                    [InlineKeyboardButton('Вернуться', callback_data='back')]]
reply_markup = InlineKeyboardMarkup(reply_keyboard)
shop_markup = InlineKeyboardMarkup(shop_keyboard)
profile_markup = InlineKeyboardMarkup(profile_keyboard)

types_markup, prod_markup, coup_markup = new_keyboard_making()


def origin_keyboards():
    worker = Worker('db/pre_release_shop.db')
    types = worker.get_types()

    types_comm = []
    prod_comm = []

    prod_names = {}
    prod_keyboards = {}

    types_keyboards = []
    for i in range(0, len(types), 6):
        lst = list(map(lambda x: f'/type_{x + 1}', range(i, i + 6)))
        types_comm.extend(list(map(lambda x: x[1:], lst)))
        types_keyboards.append([lst[i:i + 2], lst[i + 2:i + 4], lst[i + 4:i + 6],
                                ['/prev_t', '/go_back', '/next_t']])
        for k in range(6):
            if i + k == len(types):
                break
            products = worker.get_products(types[i + k])
            print(products)
            prod_names[i + k + 1] = []
            prod_keyboards[types[i + k]] = []
            for j in range(0, len(products), 6):
                prod_names[i + k + 1].extend(products[j:j + 6])
                lst = list(map(lambda x: f'/t_{i + k + 1}_p_{x + 1}', range(j, j + 6)))
                prod_comm.extend(list(map(lambda x: x[1:], lst)))
                prod_keyboards[types[i + k]].append([lst[j:j + 2], lst[j + 2:j + 4], lst[j + 4:j + 6],
                                                     ['/prev_p', '/go_back', '/next_p']])

    coupons = worker.get_coupons()
    coup_keyboard = []
    for i in range(0, len(coupons), 4):
        coup_keyboard.append(list(map(lambda x: '/coup_' + str(x + 1),
                                      range(i, i + len(coupons[i:i + 4])))))
    coup_keyboard.append(['/go_back'])

    prod_markups = {x[0]: list(map(lambda y: ReplyKeyboardMarkup(y, one_time_keyboard=False),
                                   x[1])) for x in prod_keyboards.items()}
    types_markups = list(map(lambda x: ReplyKeyboardMarkup(x, one_time_keyboard=False), types_keyboards))
    coup_markup = ReplyKeyboardMarkup(coup_keyboard, one_time_keyboard=False)
