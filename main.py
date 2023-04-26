"""
Никнейм бота - https://t.me/yandexgroceryshop_bot
"""
import datetime
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup
import random

reply_keyboard = [['/Shop', '/Profile', '/Support']]
shop_keyboard = [['/products', '/buy'],
                 ['/go_back']]
profile_keyboard = [['/purchase_history', '/activate_coupon'], ['/go_back']]
close_keyboard = [['/close']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
markup_shop = ReplyKeyboardMarkup(shop_keyboard, one_time_keyboard=False)
markup_profile = ReplyKeyboardMarkup(profile_keyboard, one_time_keyboard=False)
markup_close = ReplyKeyboardMarkup(close_keyboard, one_time_keyboard=False)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна, а?",
        reply_markup=markup
    )


async def shop(update, context):
    await update.message.reply_text(
        "Магазин",
        reply_markup=markup_shop
    )


async def products(update, context):
    await update.message.reply_text(
        """Список товаров:"""
    )


async def buy(update, context):
    await update.message.reply_text(
        """Сделать будет всплывающее в чате окно с категориями товаров, которое сделает кирилл"""
    )


async def activate_coupon(update, context):
    await update.message.reply_text(
        """Введите купон: (Берется купон из бд и пополняется баланс, это делает ксюша)"""
    )


async def profile(update, context):
    await update.message.reply_text(
        "Здесь будет инфа о пользователе",
        reply_markup=markup_profile
    )


async def support(update, context):
    await update.message.reply_text(
        """
        ➖ Помощь ➖
По всем вопросам пишите сюда:
@igstsr @theyoungcynic"""
    )


async def purchase_history(update, context):
    await update.message.reply_text(
        """История покупок из бд"""
    )


async def deposits_history(update, context):
    await update.message.reply_text(
        """История пополнений из бд"""
    )


def main():
    application = Application.builder().token('6277839457:AAG7BAL2YFhg6bPyGqqzgJYKTFlpvGg0SWM').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("go_back", start))
    application.add_handler(CommandHandler("Shop", shop))
    application.add_handler(CommandHandler("Products", products))
    application.add_handler(CommandHandler("Buy", buy))
    application.add_handler(CommandHandler("activate_coupon", activate_coupon))
    application.add_handler(CommandHandler("Profile", profile))
    application.add_handler(CommandHandler("Support", support))
    application.add_handler(CommandHandler("purchase_history", purchase_history))
    application.add_handler(CommandHandler("deposits_history", deposits_history))
    application.add_handler(CommandHandler("Support", support))

    application.run_polling()


if __name__ == '__main__':
    main()
