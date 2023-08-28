import os

from settings import STATIC_DIR


def get_static_text(filename: str):

    with open(os.path.join(STATIC_DIR, filename)) as file:
        text = file.read()

    return text
