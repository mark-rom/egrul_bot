import logging
import os
import sys
from asyncio.log import logger

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from egrul import parse_egrul

load_dotenv()

log = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
log.setLevel(logging.INFO)
log.addHandler(handler)


BOT_TOKEN = os.getenv('BOT_TOKEN')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(BASE_DIR, 'static/')


def send_message(update, context):
    chat = update.effective_chat
    query = update.message.text

    if not query.isnumeric():
        text = 'Я умею работать только с ИНН или ОГРН'
        logger.error(f'Введена нечисловая строка: {query}')
        context.bot.send_message(chat_id=chat.id, text=text)
        return

    text = parse_egrul(query)

    context.bot.send_message(chat_id=chat.id, text=text)


def send_error_message(update, context):
    chat = update.effective.chat
    text = '''Произошла ошибка. Проверьте, что вводите верный ИНН/ОГРН.
    Если ИНН/ОГРН введен правильно, сообщите @mark-rom об ошибке.'''
    logger.error(update.message.text)

    context.bot.send_message(chat_id=chat.id, text=text)


def start(update, context):
    file_path = os.path.join(STATIC, 'start.txt')
    start_file = open(file_path)
    text = start_file.read()
    start_file.close()

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def about(update, context):
    file_path = os.path.join(STATIC, 'about_author.txt')
    start_file = open(file_path)
    text = start_file.read()
    start_file.close()

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def help(update, context):
    file_path = os.path.join(STATIC, 'help.txt')
    start_file = open(file_path)
    text = start_file.read()
    start_file.close()

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def support(update, context):
    file_path = os.path.join(STATIC, 'support.txt')
    start_file = open(file_path)
    text = start_file.read()
    start_file.close()

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def check_tokens():
    if not BOT_TOKEN:
        log.critical(
            'Переменная окружения TG_TOKEN не задана. Бот выключен'
        )
        return False

    return True


start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help)
support_handler = CommandHandler('support', support)
about_handler = CommandHandler('about', about)
parse_egrul_handler = MessageHandler(Filters.text, send_message)
error_message_handler = MessageHandler(Filters.text, send_error_message)


def main():
    if not check_tokens():
        return

    updater = Updater(token=BOT_TOKEN)

    while True:
        try:
            updater.start_polling()
            updater.dispatcher.add_handler(start_handler)
            updater.dispatcher.add_handler(help_handler)
            updater.dispatcher.add_handler(support_handler)
            updater.dispatcher.add_handler(about_handler)

            updater.dispatcher.add_handler(parse_egrul_handler)
        except Exception as e:
            logger.exception(e)
            updater.dispatcher.add_handler(error_message_handler)
        finally:
            updater.idle()


if __name__ == '__main__':
    main()
