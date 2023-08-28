from telegram.ext import Updater

from settings import BOT_TOKEN
from src import handlers
from src.callbacks import send_error_message
from src.main_logger import main_logger


def check_tokens():
    if not BOT_TOKEN:
        main_logger.critical(
            'Переменная окружения TG_TOKEN не задана. Бот выключен'
        )
        return False

    return True


def main():
    if not check_tokens():
        return

    updater = Updater(token=BOT_TOKEN)

    updater.start_polling()
    updater.dispatcher.add_handler(handlers.start_handler)
    updater.dispatcher.add_handler(handlers.help_handler)
    updater.dispatcher.add_handler(handlers.support_handler)
    updater.dispatcher.add_handler(handlers.about_handler)

    updater.dispatcher.add_handler(handlers.get_extraction_conv)
    updater.dispatcher.add_handler(handlers.parse_egrul_handler)

    updater.dispatcher.add_error_handler(send_error_message)

    updater.idle()


if __name__ == '__main__':
    main()
