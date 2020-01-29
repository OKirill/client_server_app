"""

Клиентская часть приложения

"""
import sys
import json
import socket
import time
import argparse
import logging
import logs.config_client_log
from errors import ReqFieldMissingError
from backup.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEF_IP, DEF_PORT
from backup.utils import rec_message, transmit_message
from decos import log


# init client log
LOGGER = logging.getLogger('client')

@log
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
    LOGGER.debug(f'Создано {PRESENCE} сообщения для ююзера {account_name}')
    return output


@log
def ans_handling(message):
    """
    Процессинг ответа от сервера
    :param message:
    :return:
    """
    LOGGER.debug(f'Расшифровка ответа от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


@log
def parser_handling():
    """
    Пробегаем по аргументам терминала
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEF_IP, nargs='?')
    parser.add_argument('port', default=DEF_PORT, nargs='?')
    return parser


def main():
    """
    выгружаем необходимые параметры
    :return:
    """
    parser = parser_handling()
    namespace = parser.parse_args(sys.argv[1:])
    server_adress = namespace.addr
    server_port = namespace.port

    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Запуск клиента с неправильным портом: {server_port}.'
            f' Используйте адреса в диапазоне 1024-65535.'
        )
        sys.exit(1)

    LOGGER.info(
            f'Клиен работает с параметрами:'
            f'адрес сервера: {server_adress}, порт: {server_port}'
                       )
    # try:
    #     server_adress = sys.argv[1]
    #     server_port = input(sys.argv[2])
    #     if server_port < 1024 or server_port > 65535:
    #         raise ValueError
    # except IndexError:
    #     server_adress = DEF_IP
    #     server_port = DEF_PORT
    # except ValueError:
    #     print('Укажите чилос в диапазоне 1024 - 65535')
    #     sys.exit(1)
    try:
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward.connect((server_adress, server_port))
        msg_to_server = show_presence()
        transmit_message(forward, msg_to_server)
        answer = ans_handling(rec_message(forward))
        LOGGER.info(f'Получен ответ от сервера {answer}')
        print(answer)
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать полученную Json строку.')
    except ReqFieldMissingError as miss_error:
        LOGGER.error(
            f'В полученных данных отсутствует необходимое поле'
            f'{miss_error.missing_field}'
        )
    except ConnectionRefusedError:
        LOGGER.critical(
            f'Не удалось соедениться с сервером {server_adress}:{server_port}, '
            f'удаленный компьютер отверг запрос на подключение.'
        )

        # forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # forward.connect((server_adress, server_port))
    # msg_to_server = show_presence()
    # transmit_message(forward, msg_to_server)
    # try:
    #     answer = ans_handling(rec_message(forward))
    #     print(answer)
    # except (ValueError, json.JSONDecodeError):
    #     print('Декодирование сообщения провалилось')


if __name__ == '__main__':
    main()
