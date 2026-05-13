import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env")

DATA_DIR = "data"
WORDS_PATH = f"{DATA_DIR}/words.json"
ABOUT_ERA_PATH = f"{DATA_DIR}/about_era.md"

# Квиз
QUIZ_OPTIONS_COUNT = 4  # сколько вариантов ответа показывать
