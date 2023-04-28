"""
Никнейм бота - https://t.me/yandexgroceryshop_bot
"""
import logging
import markups_for_bot as mb
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup
from config import BOT_TOKEN
from db_worker import Worker

# подключаем базу данных
worker = Worker('db/pre_release_shop.db')

reply_keyboard = [['/Shop', '/Profile', '/Support']]
shop_keyboard = [['/prod_types', '/get_check'], ['/pay', '/go_back']]
profile_keyboard = [['/purchase_history', '/activate_coupon'], ['/go_back']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup_shop = ReplyKeyboardMarkup(shop_keyboard, one_time_keyboard=False)
markup_profile = ReplyKeyboardMarkup(profile_keyboard, one_time_keyboard=False)

# будет использоваться для возвращения на прошлую клавиатуру
markup_stack = [markup]
prod_i = 0
type_title = ''
type_i = 0

# данные, чтобы не переделывать их каждый раз
tps = '\n'.join(list(map(lambda x: f'{x + 1} - {mb.types[x]}', range(len(mb.types)))))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def start(update, context):
    markup_stack.append(markup)
    await update.message.reply_text(
        """Добро пожаловать в наш магазин! Что вы хотите сделать?
/Shop - открыть магазин
/Profile - открыть профиль
/Support - справочная информация""",
        reply_markup=markup
    )


async def shop(update, context):
    await update.message.reply_text(
        "Магазин",
        reply_markup=markup_shop
    )


async def get_types(update, context):
    markup_stack.append(markup_shop)
    await update.message.reply_text(f'Выберите тип товара: {tps}',
                                    reply_markup=mb.types_markups[type_i])


async def prev_type(update, context):
    global type_i
    type_i = (type_i - 1) % len(mb.types_markups)
    await update.message.reply_text('', reply_markup=mb.types_markups[type_i])


async def next_type(update, context):
    global type_i
    type_i = (type_i + 1) % len(mb.types_markups)
    await update.message.reply_text('', reply_markup=mb.types_markups[type_i])


async def next_product(update, context):
    global type_i, prod_i
    prod_i = (prod_i + 1) % len(mb.prod_markups[type_title])
    await update.message.reply_text('', reply_markup=mb.prod_markups[type_title][prod_i])


async def prev_product(update, context):
    global type_i, prod_i
    prod_i = (prod_i - 1) % len(mb.prod_markups[type_title])
    await update.message.reply_text('', reply_markup=mb.prod_markups[type_title][prod_i])


async def products(update, context):
    global type_title, prod_i, type_i
    markup_stack.append(mb.types_markups[type_i])
    tp_i = int(update.message.text.lstrip('/type_'))
    type_title = mb.types[int(update.message.text.lstrip('/type_')) - 1]
    need = mb.prod_markups[str(type_title)][prod_i]
    prods = '\n'.join(list(map(lambda x: f'{x + 1} - {mb.prod_names[tp_i][x]}',
                               range(len(mb.prod_names[tp_i])))))
    await update.message.reply_text(
        f"Товары типа {type_title}:\n{prods}", reply_markup=need
    )


async def go_back(update, context):
    """Вернуться на предыдущую клавиатуру."""
    global prod_i, type_i
    if markup_stack[-1] in mb.types_markups:
        prod_i = 0
    else:
        type_i = 0
    await update.message.reply_text('Возвращение назад', reply_markup=markup_stack.pop(-1))


async def add_product(update, context):
    global type_title
    data = update.message.text.split('_')
    worker.add_product(int(update.effective_user.id), mb.prod_names[int(data[1])][int(data[3]) - 1])
    await update.message.reply_text('Товар добавлен в корзину.')


async def add_coupon(update, context):
    coup_id = update.message.text.lstrip('/coup_')
    worker.add_coupon(update.effective_user.id, coup_id)
    await update.message.reply_text(f'Купон {coup_id} добавлен')


async def pay(update, context):
    """Купить - напечатать информацию о корзине и закрыть покупку."""
    user_id = int(update.effective_user.id)
    await update.message.reply_text(worker.get_purchase(user_id))
    worker.close_purchase(user_id)


async def get_check(update, context):
    """Получить всю информацию о корзине на данный момент."""
    await update.message.reply_text(worker.get_purchase(int(update.effective_user.id)))


async def purchase_history(update, context):
    hist = '\n'.join(worker.purchase_history(int(update.effective_user.id)))
    await update.message.reply_text('История покупок:\n' + hist)


async def activate_coupon(update, context):
    global markup_stack
    markup_stack.append(markup_profile)
    await update.message.reply_text(
        'Выберите купон:\n'
        '\n'.join(mb.coupons),
        reply_markup=mb.coup_markup
    )


async def profile(update, context):
    """Вернуть информацию о пользователе (его id) и дополнительные возможности."""
    await update.message.reply_text(
        f"Профиль пользователя {update.effective_user.id}",
        reply_markup=markup_profile
    )


async def support(update, context):
    """Вернуть справочную информацию."""
    await update.message.reply_text(
        """
        ➖ Помощь ➖
По всем вопросам пишите сюда:
@igstsr @theyoungcynic"""
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    # стартовая клавиатура
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("Shop", shop))
    application.add_handler(CommandHandler("Profile", profile))
    application.add_handler(CommandHandler("Support", support))
    # универсальная кнопка
    application.add_handler(CommandHandler("go_back", start))
    # клавиатура профиля
    application.add_handler(CommandHandler("activate_coupon", activate_coupon))
    application.add_handler(CommandHandler("purchase_history", purchase_history))
    # клавиатура магазина
    application.add_handler(CommandHandler("prod_types", get_types))
    application.add_handler(CommandHandler('pay', pay))

    for comm in mb.types_comm:
        application.add_handler(CommandHandler(comm, products))

    for comm in mb.prod_comm:
        application.add_handler(CommandHandler(comm, add_product))

    for coup in range(len(mb.coupons)):
        application.add_handler(CommandHandler(f'coup_{coup}', add_coupon))

    # поехали
    application.run_polling()


if __name__ == '__main__':
    main()
