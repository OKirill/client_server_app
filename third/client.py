"""

Клиентская часть приложения

"""
import sys
import json
import socket
import time
from backup.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEF_IP, DEF_PORT
from backup.utils import rec_message, transmit_message


def show_presence(account_name='Guest'):
    """
    Функция для генерации запроса о статусе на присутствие клиента
    :param account_name:
    :return:
    """
    output = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return output


def ans_handling(message):
    """
    Процессинг ответа от сервера
    :param message:
    :return:
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    """
    выгружаем необходимые параметры
    :return:
    """
    try:
        server_adress = sys.argv[1]
        server_port = input(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_adress = DEF_IP
        server_port = DEF_PORT
    except ValueError:
        print('Укажите чилос в диапазоне 1024 - 65535')
        sys.exit(1)

    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward.connect((server_adress, server_port))
    msg_to_server = show_presence()
    transmit_message(forward, msg_to_server)
    try:
        answer = ans_handling(rec_message(forward))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Декодирование сообщения провалилось')


if __name__ == '__main__':
    main()
