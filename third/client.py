"""

Клиентская часть приложения

"""
import sys
import json
import socket
import time
import argparse
import logging
import threading
import logs.config_client_log
from errors import ReqFieldMissingError, ServerError, IncorrectDataReceivedError
from backup.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEF_IP, DEF_PORT, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT
from backup.utils import rec_message, transmit_message
from decos import log

# init client log
LOGGER = logging.getLogger('client')


@log
def create_exit_message(account_name):
    """
    Словарь с сообщением о выходе
    :param account_name:
    :return:
    """
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def transmission_from_server(sock, my_username):
    """
    Функция обработки сообщений переданных на сервер
    """
    while True:
        try:
            message = rec_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                            f'\n{message[MESSAGE_TEXT]}')
            else:
                LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataReceivedError:
            LOGGER.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            LOGGER.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_message(sock, account_name='Guest'):
    """
    Функция принимает данные о том кому отправить сообщение и отсылает данные на сервер
    """
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        transmit_message(sock, message_dict)
        LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


def print_help():
    """
    Функция справка
    """
    print('Список команд:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def user_interactive(sock, username):
    """
    Функция запрашивает команды и занимается отправкой сообщений
    """
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            transmit_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            LOGGER.info('Завершение работы по команде пользователя.')
            # Задержка сообщения
            time.sleep(0.5)
            break
        else:
            print('Команда задана неверно, попробойте снова. help - вывести поддерживаемые команды.')


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
    parser.add_argument('port', default=DEF_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    """
    выгружаем необходимые параметры
    :return:
    """
    print('Мессенджер использующий консоль или терминал. Клиентский модуль.')
    server_address, server_port, client_name = parser_handling()

    # Запрашиваем имя пользователя если не было задано изначально
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, режим работы: {client_name}')

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
        transmit_message(forward, show_presence(client_name))
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
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(
            f'Не удалось соедениться с сервером {server_address}:{server_port}, '
            f'удаленный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # запускаем процесс приема сообщений если все настроено верно
        receiver = threading.Thread(target=transmission_from_server, args=(forward, client_name))
        receiver.daemon = True
        receiver.start()

        # запуск процесса отправки сообщений.
        user_interface = threading.Thread(target=user_interactive, args=(forward, client_name))
        user_interface.daemon = True
        user_interface.start()
        LOGGER.debug('Запущены процессы')

        # основной цикл которой отрабатывает пока не потеряно соединение
        # или пользователь не вышел через exit
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break

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
