import logging
import os
from logging.handlers import RotatingFileHandler

from settings import LOGS_DIR

main_logger = logging.getLogger(__file__)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, 'egrul_bot.log'), backupCount=1,
    encoding='utf-8', maxBytes=1000000
)
handler.setFormatter(formatter)
main_logger.setLevel(logging.INFO)
main_logger.addHandler(handler)
