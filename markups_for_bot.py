"""
Создание клавиатур и списков для взаимодействия с ними.
"""
from db_worker import Worker
from telegram import ReplyKeyboardMarkup


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
