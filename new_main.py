"""
Никнейм бота - https://t.me/yandexgroceryshop_bot
"""
import logging
import markups_for_bot as mb  # все необходимые клавиатуры
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler
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
markup_stack = [mb.reply_markup]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def new_start(update, context):
    """Запуск приложения-магазина."""
    await update.message.reply_text("Добро пожаловать в наш магазин! Что вы хотите сделать?",
                                    reply_markup=mb.reply_markup)


async def first_answer(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f'Вы выбрали опцию {query.data}')


async def shop(update, context):
    """Реакция на выбор кнопки магазина."""
    markup_stack.append(mb.reply_markup)
    query = update.callback_query
    await query.answer()
    await update.message.reply_text("Магазин", reply_markup=mb.shop_markup)


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
    res = worker.add_product(int(update.effective_user.id),
                             mb.prod_names[int(data[1])][int(data[3]) - 1])
    if res:
        await update.message.reply_text('Товар добавлен в корзину.')
    else:
        await update.message.reply_text('Такого товара нет.')


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
    markup_stack.append(new_profile_markup)
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

    application.add_handler(CommandHandler("start", new_start))
    application.add_handler(CallbackQueryHandler(first_answer))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", new_start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(one, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(two, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
            ],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TWO) + "$"),
            ],
        },
        fallbacks=[CommandHandler("start", new_start)],
    )

    # поехали
    application.run_polling()


if __name__ == '__main__':
    main()
