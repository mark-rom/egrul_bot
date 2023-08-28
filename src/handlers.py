from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler)

from src import callbacks

start_handler = CommandHandler('start', callbacks.start)
help_handler = CommandHandler('help', callbacks.help)
support_handler = CommandHandler('support', callbacks.support)
about_handler = CommandHandler('about', callbacks.about)
cancel_handler = CommandHandler('cancel', callbacks.cancel)
cancel_handler = CommandHandler('commands', callbacks.commands)

parse_egrul_handler = MessageHandler(
    Filters.text & (~ Filters.command),
    callbacks.send_message
)
extraction_handler = MessageHandler(
    Filters.text & (~ Filters.command),
    callbacks.send_extraction
)

get_extraction_conv = ConversationHandler(
    # TODO: добавить сброс, если при поиске выписки произошла ошибка
    entry_points=[CommandHandler('get_extraction', callbacks.new_extraction)],
    states={callbacks.EXTRACTION: [extraction_handler]},
    fallbacks=[cancel_handler]
)
