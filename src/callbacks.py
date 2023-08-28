from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from src.egrul import pdf_extraction, short_info
from src.main_logger import main_logger
from src.models import Company, Request, session, User
from src.utils import get_static_text
from src.exceptions import DevEGRULException

EXTRACTION = range(1)


def start(update: Update, context: CallbackContext):
    text = get_static_text('start.txt')

    chat = update.effective_chat

    user = update.effective_user.id

    new_user = User(telegram_id=user)
    session.add(new_user)
    session.commit()

    context.bot.send_message(chat_id=chat.id, text=text)


def about(update: Update, context: CallbackContext):
    text = get_static_text('about_author.txt')

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def help(update: Update, context: CallbackContext):
    text = get_static_text('help.txt')

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def support(update: Update, context: CallbackContext):
    text = get_static_text('support.txt')

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def commands(update: Update, context: CallbackContext):
    text = get_static_text('commands.txt')

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def new_extraction(update: Update, context: CallbackContext):
    text = 'Пожалуйста, пришлите ИНН или ОГРН или отмените командой /cancel'
    update.message.reply_text(text)
    return EXTRACTION


def send_extraction(update: Update, context: CallbackContext):
    chat = update.effective_chat
    query = update.message.text

    if not query.isnumeric():
        text = 'Я умею работать только с ИНН или ОГРН'
        main_logger.error(f'Введена нечисловая строка: {query}')
        context.bot.send_message(chat_id=chat.id, text=text)

    extraction = pdf_extraction(query)

    context.bot.send_document(
        chat_id=chat.id,
        document=extraction,
    )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    chat = update.effective_chat
    text = 'Вы всегда можете запросить выписку по команде /get_extraction'
    context.bot.send_message(chat_id=chat.id, text=text)
    return ConversationHandler.END


def send_message(update: Update, context: CallbackContext):
    chat = update.effective_chat
    query = update.message.text

    if not query.isnumeric():
        text = 'Я умею работать только с ИНН или ОГРН'
        main_logger.error(f'Введена нечисловая строка: {query}')
        context.bot.send_message(chat_id=chat.id, text=text)
        return

    text = short_info(query)

    context.bot.send_message(chat_id=chat.id, text=text)


def send_error_message(update: Update, context: CallbackContext):
    chat = update.effective_chat
    # main_logger.exception(update.message.text, context.error)
    text = context.error

    context.bot.send_message(chat_id=chat.id, text=text)
