import os
from datetime import datetime
import argparse

import dotenv

from api import Api, IncorrectTokenException


FILE_NAME = "spam.txt"

dotenv.load_dotenv()
token = os.getenv("TOKEN")

# выводим баннер
print("Telegram: @cyberego", end="\n\n")

# настраиваем argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    "-n", "--max-number", type=int, default=0, help="Максимальное количество сообщений"
)
parser.add_argument(
    "-d",
    "--delay",
    type=int,
    default=0,
    help="Задержка в секундах после отправки каждых 100 сообщений",
)
args = parser.parse_args()

# получаем текст сообщения из файла
try:
    with open(FILE_NAME) as f:
        text = f.read().strip()
except FileNotFoundError:
    print(f"Ошибка: файл {FILE_NAME} не создан")
    exit(1)

# засекаем время
d1 = datetime.now()

# рассылаем сообщение
ok = Api(token)
chats = []

try:
    print("Получение списка чатов...")
    chats = ok.get_chats(max_count=args.max_number)
except IncorrectTokenException:
    print("Ошибка: некорректный токен")
    exit(1)

chat_ids = [chat["conversation"]["peer"]["id"] for chat in chats]

# рассылка
print("Рассылка...")
ok.mailing(chat_ids, text, delay=args.delay)

# засекаем время
d2 = datetime.now()
dd = (d2 - d1).total_seconds()

# выводим результат
print("\nГотово!")
print("Всего отправлено сообщений:", len(chats))
print("Затраченное время:", dd, "сек.")
