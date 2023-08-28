import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
LOGS_DIR = BASE_DIR / 'logs'


env_path = BASE_DIR / 'infra/.env'
load_dotenv(env_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')
