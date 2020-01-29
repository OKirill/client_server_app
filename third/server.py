"""
Серверная часть программы
"""
import socket
import sys
import json
import logging
import argparse
import logs.config_server_log
from errors import IncorrectDataReceivedError
from backup.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEF_PORT, DEF_IP_ADRRES
from backup.utils import rec_message, transmit_message
from decos import log


LOGGER = logging.getLogger('server')


@log
def handling_mess_from_client(message):
    """
    Обработка сообщения от клиента в виде словаря,
    проверка и отправка ответа.
    :param message:
    :return:
    """
    LOGGER.debug(f'Обработка сообщения клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'False Request'
    }


@log
def parser_handling():
    """
    Пробегаем по аргументам терминала
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEF_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    return parser


def main():
    """
    Загрузка параметров из командной строки
    в случае отсутствия - используются
    параметры по умолчанию
    :return:
    """
    parser = parser_handling()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # try:
    #     if '-p' in sys.argv:
    #         listner_to_the_port = int(sys.argv[sys.argv.index('-p') + 1])
    #     else:
    #         listner_to_the_port = DEF_PORT
    #     if listner_to_the_port < 1024 or listner_to_the_port > 65535:
    #         raise ValueError
    # except IndexError:
    #     print("Нужно указать номер порта после параметра -\'p\'.")
    #     sys.exit(1)
    # except ValueError:
    #     print(
    #         'Пожалуста введите подобающий номер порта(в диапазоне от 1024 до 65535.'
    #     )
    #     sys.exit(1)
    #
    # try:
    #     if '-a' in sys.argv:
    #         listner_to_the_adress = sys.argv[sys.argv.index('-a') + 1]
    #     else:
    #         listner_to_the_adress = ''
    #
    # except IndexError:
    #     print('Укажите адресс который будет прослушивать сервер после параметра -\'a\'.')
    #     sys.exit(1)

    if not 1023 < listen_port < 65536:
        LOGGER.critical(
            f'Запуск сервера с неправильным портом: {listen_port}.'
            f' Используйте адреса в диапазоне 1024-65535.'
        )
        sys.exit(1)

    LOGGER.info(
        f'Сервер запущен с портом для подключения: {listen_port}'
        f'адрес сервера: {listen_address}')

    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward.bind((listen_address, listen_port))

    forward.listen(MAX_CONNECTIONS)

    while True:
        client, client_adress = forward.accept()
        try:
            message_from_client = rec_message(client)
            LOGGER.debug(f'Получено сообщение {message_from_client}')
            response = handling_mess_from_client(message_from_client)
            LOGGER.info(f'Создан ответ для клиента {response}')
            transmit_message(client, response)
            LOGGER.debug(f'Сеанс с клиентом {client_adress} завершен.')
            client.close()
        except json.JSONDecodeError:
            LOGGER.error(
                f'Не удалось обработать Json  полученый от '
                f'клиента {client_adress}. Сеанс завершен.'
            )
            client.close()
        except IncorrectDataReceivedError:
            LOGGER.error(f'От клиента {client_adress} приняты некорректные данные. '
                                f'Соединение закрывается.')
            client.close()


if __name__ == '__main__':
    main()
