"Утилиты для проекта"

import json
from backup.variables import MAX_BYTES_LENGTH, ENCODING


def rec_message(client):
    """Утилита которую мы будем часто использовать для получания и декодирования наших сообщений
    поэтому она будет вынесена в отдельный файл для удобства
    """
    response_after_encod = client.recv(MAX_BYTES_LENGTH)
    if isinstance(response_after_encod, bytes):
        json_resp = response_after_encod.decode(ENCODING)
        response = json.loads(json_resp)
        if isinstance(response, dict):
            return response

        raise ValueError
    raise ValueError


def transmit_message(sock, message):
    """
    Тоже самое что и первая утилита только для отправки

    """
    if not isinstance(message, dict):
        raise TypeError
    js_message = json.dumps(message)
    message_after_encode = js_message.encode(ENCODING)
    sock.send(message_after_encode)
