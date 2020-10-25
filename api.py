import random
from time import sleep

import requests
from typing import List


_BASE_URL = "https://api.vk.com/method/"
_HTTP_HEADERS = {"Content-Type": "application/json;charset=utf-8"}
_API_VERSION = 5.124


class IncorrectTokenException(Exception):
    pass


class Api:
    def __init__(self, token: str):
        self._token = token

    def _query(self, endpoint: str, params: dict = None, data: dict = None, method: str = "GET") -> dict:
        url = "{}{}".format(_BASE_URL, endpoint)
        if not params:
            params = {}
        params["access_token"] = self._token
        params["v"] = _API_VERSION

        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, data=data, params=params)
        else:
            raise ValueError("Incorrect method passed")

        json_ = response.json()

        if "error" in json_:
            if json_["error"]["error_code"] == 5:
                raise IncorrectTokenException
            else:
                raise RuntimeError(json_["error"]["error_msg"])
        return json_

    def get_chats(self, max_count: int = 0) -> list:
        chats = []
        offset = 0

        while 1:
            # высчитываем count исходя из max_count
            if max_count and max_count - len(chats) < 200:
                count = max_count - len(chats)

                if count == 0:
                    break
            else:
                count = 200

            # получение списка чатов
            response = self._query(
                "messages.getConversations", {"count": count, "offset": offset}
            )
            chats_portion = response["response"]["items"]
            chats.extend(chats_portion)

            # выходим из цикла, если это последняя партия чатов
            if len(chats_portion) < 200:
                break

            offset += 200

        return chats

    def mailing(self, user_ids: List[int], text: str, delay: int = 0) -> None:
        offset = 0

        while True:
            # формируем список получателей до 100 шт.
            peer_ids = ",".join(
                [str(user_id) for user_id in user_ids[offset : offset + 100]]
            )

            # формируем уникальный ID сообщения
            random_id = random.randint(1_000_000_000, 9_999_999_999)

            # отправляем сообщение вышеуказанным получателям
            self._query(
                "messages.send",
                data={"peer_ids": peer_ids, "message": text, "random_id": random_id},
                method="POST"
            )

            offset += 100

            if offset >= len(user_ids):
                break

            sleep(delay)
