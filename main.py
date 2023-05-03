"""
Никнейм бота - https://t.me/yandexgroceryshop_bot
"""
import logging
import markups_for_bot as mb  # все необходимые клавиатуры
from copy import deepcopy
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, DB_FILE
from db_worker import Worker

# подключаем базу данных
worker = Worker(db_file=DB_FILE)

# необходимые для дальнейшей работы глобальные переменные и константы
TYPES = worker.get_types()
PRODUCTS = worker.get_products()
COUPONS = worker.get_coupons()
product = ''


# будет использоваться для возвращения на прошлую клавиатуру
markup_stack = [mb.reply_markup]
to_add = None

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def new_start(update, context):
    """Запуск приложения-магазина."""
    await update.message.reply_text("Добро пожаловать в наш магазин! Что вы хотите сделать?",
                                    reply_markup=mb.reply_markup)


async def manager_callback(update, context):
    """Управлять всеми событиями клавиатур."""
    query = update.callback_query
    await query.answer()
    if query.data == 'shop':  # попасть в магазин
        await shop(query)
    if query.data == 'types':  # получить категории товаров
        await get_all_types(query)
    if query.data == 'profile':  # профиль
        await profile(query)
    if query.data == 'back':  # кнопка "вернуться"
        await go_back(query)
    if query.data in TYPES:  # если выбран тип, то вернуть продукты по нему
        await types_manage(query)
    if query.data == 'add_product':  # добавить продукт в корзину
        await add_product(update, query)
    if query.data == 'purchase_history':  # получить историю покупок
        await purchase_history(update)
    if query.data.isdigit():  # если отправлен номер купона
        await add_coupon(update, query)
    if query.data == 'coupons':  # чтобы получить список купонов
        await activate_coupon(query)
    if query.data == 'support':  # поддержка
        await support(update)
    if query.data == 'check':  # получить чек
        await get_check(update)
    if query.data == 'pay':  # оплатить покупку
        await pay(update)
    if query.data in PRODUCTS:  # дать возможность купить продукт
        await product_manage(query)


async def get_all_types(query):
    """Получить все категории продуктов."""
    markup_stack.append(mb.shop_markup)
    await query.edit_message_text('Категории продуктов:', reply_markup=mb.types_markup)


async def types_manage(query):
    """Отправить клавиатуру со списком продуктов определенной категории."""
    global to_add
    markup_stack.append(mb.shop_markup)
    to_add = deepcopy(mb.prod_markup[query.data])
    to_print = f'Продукты категории "{query.data}":'
    await query.edit_message_text(to_print, reply_markup=mb.prod_markup[query.data])


async def product_manage(query):
    """Вернуть клавиатуру, где дается выбор, покупать товар или нет."""
    global to_add, product
    markup_stack.append(to_add)
    product = query.data
    await query.edit_message_text(f'{query.data}', reply_markup=mb.small_markup)


async def add_product(update, query):
    """Добавить продукт в корзину пользователя."""
    global product
    user = update.effective_message.chat.username
    worker.add_product(user, product)
    await query.edit_message_text(f'{product}\nДобавлен в корзину!', reply_markup=mb.small_markup)


async def shop(query):
    """Реакция на выбор кнопки магазина."""
    markup_stack.append(mb.reply_markup)
    await query.edit_message_text("Магазин", reply_markup=mb.shop_markup)


async def profile(query):
    """Профиль пользователя."""
    markup_stack.append(mb.reply_markup)
    await query.edit_message_text('Ваш профиль:', reply_markup=mb.profile_markup)


async def go_back(query):
    """Вернуться на предыдущую клавиатуру."""
    await query.edit_message_text('Возвращение назад', reply_markup=markup_stack.pop())


async def add_coupon(update, query):
    """Добавить к покупке купон."""
    worker.add_coupon(update.effective_message.chat.username, query.data)
    await update.effective_message.reply_text(f'Купон {query.data} добавлен')
    await update.effective_message.reply_text(f'Выберите купон:', reply_markup=mb.coup_markup)


async def pay(update):
    """Купить - напечатать информацию о корзине и закрыть покупку."""
    user_id = update.effective_message.chat.username
    await update.effective_message.reply_text(worker.get_purchase(user_id))
    worker.close_purchase(user_id)
    await update.effective_message.reply_text('Покупка оплачена.')
    await update.effective_message.reply_text('Магазин', reply_markup=mb.reply_markup)


async def get_check(update):
    """Получить всю информацию о корзине на данный момент."""
    await update.effective_message.reply_text(worker.get_purchase(
        update.effective_message.chat.username))
    await update.effective_message.reply_text('''Магазин''', reply_markup=mb.shop_markup)


async def purchase_history(update):
    """Получить историю покупок пользователя."""
    hist = '\n'.join(worker.purchase_history(update.effective_message.chat.username))
    await update.effective_message.reply_text('История покупок:\n' + hist)
    await update.effective_message.reply_text('Ваш профиль:', reply_markup=mb.profile_markup)


async def activate_coupon(query):
    """Выбрать купон из списка."""
    markup_stack.append(mb.profile_markup)
    await query.edit_message_text('Выберите купон:', reply_markup=mb.coup_markup)


async def support(update):
    """Вернуть справочную информацию."""
    await update.effective_message.reply_text(
        """
        ➖ Помощь ➖
По всем вопросам пишите сюда:
@igstsr @theyoungcynic"""
    )
    await update.effective_message.reply_text('Что вы хотите сделать?', reply_markup=mb.reply_markup)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", new_start))
    application.add_handler(CallbackQueryHandler(manager_callback))

    # поехали
    application.run_polling()


if __name__ == '__main__':
    main()
