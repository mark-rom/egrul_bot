import logging
import os
import sys

from dotenv import load_dotenv
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from egrul import egrul_extraction, egrul_info

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
EXTRACTION = range(1)


def send_message(update, context):
    chat = update.effective_chat
    query = update.message.text

    if not query.isnumeric():
        text = 'Я умею работать только с ИНН или ОГРН'
        log.error(f'Введена нечисловая строка: {query}')
        context.bot.send_message(chat_id=chat.id, text=text)
        return

    text = egrul_info.parse_egrul(query)

    context.bot.send_message(chat_id=chat.id, text=text)


def new_extraction(update, context):
    text = 'Пожалуйста, пришлите ИНН или ОГРН или отмените командой /cancel'
    update.message.reply_text(text)
    return EXTRACTION


def send_extraction(update, context):
    chat = update.effective_chat
    query = update.message.text

    if not query.isnumeric():
        text = 'Я умею работать только с ИНН или ОГРН'
        log.error(f'Введена нечисловая строка: {query}')
        context.bot.send_message(chat_id=chat.id, text=text)

    # else:
    extraction = egrul_extraction.get_extraction(query)

    context.bot.send_document(
        chat_id=chat.id,
        document=extraction,
    )
    return ConversationHandler.END


def send_error_message(update, context):
    chat = update.effective_chat
    log.exception(update.message.text, context.error)
    text = 'В работе бота произошла ошибка, попробуйте повторить запрос позже.'

    context.bot.send_message(chat_id=chat.id, text=text)


def get_static(path):

    file = open(path)
    text = file.read()
    file.close()

    return text


def start(update, context):
    file_path = os.path.join(STATIC, 'start.txt')
    text = get_static(file_path)

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def about(update, context):
    file_path = os.path.join(STATIC, 'about_author.txt')
    text = get_static(file_path)

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def help(update, context):
    file_path = os.path.join(STATIC, 'help.txt')
    text = get_static(file_path)

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def support(update, context):
    file_path = os.path.join(STATIC, 'support.txt')
    text = get_static(file_path)

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def cancel(update, context):
    chat = update.effective_chat
    text = 'Вы всегда можете запросить выписку по команде /get_extraction'
    context.bot.send_message(chat_id=chat.id, text=text)
    return ConversationHandler.END


def commands(update, context):
    file_path = os.path.join(STATIC, 'commands.txt')
    text = get_static(file_path)

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
cancel_handler = CommandHandler('cancel', cancel)
cancel_handler = CommandHandler('commands', commands)

parse_egrul_handler = MessageHandler(
    Filters.text & (~ Filters.command),
    send_message
)
extraction_handler = MessageHandler(
    Filters.text & (~ Filters.command),
    send_extraction
)

get_extraction_conv = ConversationHandler(
    entry_points=[CommandHandler('get_extraction', new_extraction)],
    states={EXTRACTION: [extraction_handler]},
    fallbacks=[cancel_handler]
)


def main():
    if not check_tokens():
        return

    updater = Updater(token=BOT_TOKEN)

    updater.start_polling()
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(support_handler)
    updater.dispatcher.add_handler(about_handler)

    updater.dispatcher.add_handler(get_extraction_conv)
    updater.dispatcher.add_handler(parse_egrul_handler)

    updater.dispatcher.add_error_handler(send_error_message)

    updater.idle()


if __name__ == '__main__':
    main()
