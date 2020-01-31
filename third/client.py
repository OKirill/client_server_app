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
from errors import ReqFieldMissingError, ServerError
from backup.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEF_IP, DEF_PORT, MESSAGE, MESSAGE_TEXT, SENDER
from backup.utils import rec_message, transmit_message
from decos import log

# init client log
LOGGER = logging.getLogger('client')


@log
def transmission_from_server(message):
    """
    Функция обработки сообщений переданных на сервер
    """
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Поступило сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        LOGGER.info(f'Поступило сообщение от пользователя '
                    f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        LOGGER.error(
            f'Сервер не смог обработать и отправить некорректное сообщение: {message}')


@log
def create_message(sock, account_name='Guest'):
    """Функция принимает сообщение и возращает его обратно и
    так же обрабатывает команды по запросу
    """
    message = input(
        'Введите сообщение которое хотите послать или \'~\' для завершения работы: ')
    if message == '~':
        sock.close()
        LOGGER.info('Пользователь завершил работу.')
        print('Благодарим за то что выбрали наш мессенджер!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


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
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
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
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
                        f'допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    """
    выгружаем необходимые параметры
    :return:
    """
    server_address, server_port, client_mode = parser_handling()

    LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, режим работы: {client_mode}')

    # if not 1023 < server_port < 65536:
    #     LOGGER.critical(
    #         f'Запуск клиента с неправильным портом: {server_port}.'
    #         f' Используйте адреса в диапазоне 1024-65535.'
    #     )
    #     sys.exit(1)
    #
    # LOGGER.info(
    #     f'Клиент работает с параметрами:'
    #     f'адрес сервера: {server_address}, порт: {server_port}'
    # )
    # try:
    #     server_address = sys.argv[1]
    #     server_port = input(sys.argv[2])
    #     if server_port < 1024 or server_port > 65535:
    #         raise ValueError
    # except IndexError:
    #     server_address = DEF_IP
    #     server_port = DEF_PORT
    # except ValueError:
    #     print('Укажите чилос в диапазоне 1024 - 65535')
    #     sys.exit(1)
    try:
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward.connect((server_address, server_port))
        transmit_message(forward, show_presence())
        answer = ans_handling(rec_message(forward))
        LOGGER.info(f'Получен ответ от сервера {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f'Сервер выявил ошибку при подключении: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as miss_error:
        LOGGER.error(
            f'В полученных данных отсутствует необходимое поле'
            f'{miss_error.missing_field}'
        )
        sys.exit(1)
    except ConnectionRefusedError:
        LOGGER.critical(
            f'Не удалось соедениться с сервером {server_address}:{server_port}, '
            f'удаленный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # Основной цикл программы если все настроено как надо
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            # режим работы - отправка сообщений
            if client_mode == 'send':
                try:
                    transmit_message(forward, create_message(forward))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOGGER.error(
                        f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

            # Режим работы приём:
            if client_mode == 'listen':
                try:
                    transmission_from_server(rec_message(forward))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOGGER.error(
                        f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

    # forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # forward.connect((server_address, server_port))
    # msg_to_server = show_presence()
    # transmit_message(forward, msg_to_server)
    # try:
    #     answer = ans_handling(rec_message(forward))
    #     print(answer)
    # except (ValueError, json.JSONDecodeError):
    #     print('Декодирование сообщения провалилось')


if __name__ == '__main__':
    main()
