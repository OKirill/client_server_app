"""

Клиентская часть приложения

"""
import sys
import json
import socket
import time
import dis
import argparse
import logging
import threading
import logs.config_client_log
from errors import ReqFieldMissingError, ServerError, IncorrectDataReceivedError
from backup.variables import *
from backup.utils import *
from decos import log
from metaclasses import ClientMaker

# init client log
logger = logging.getLogger('client')


class ClientSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_message(self):
        """
        Функция принимает данные о том кому отправить сообщение и отсылает данные на сервер
        """
        to_user = input('Введите имя собеседника: ')
        message = input('Напишите ваше сообщение: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            transmit_message(self.sock, message_dict)
            logger.info(f'Отправлено сообщение для пользователя {to_user}')
        except:
            logger.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    transmit_message(self.sock, self.create_exit_message())
                except:
                    pass
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


class ClientReader(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Основной цикл приёмника сообщений, принимает сообщения, выводит в консоль. Завершается при потере соединения.
    def run(self):
        while True:
            try:
                message = rec_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    logger.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataReceivedError:
                logger.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break


@log
def show_presence(account_name):
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
    logger.debug(f'Создано {PRESENCE} сообщения для ююзера {account_name}')
    return output


@log
def ans_handling(message):
    """
    Процессинг ответа от сервера
    :param message:
    :return:
    """
    logger.debug(f'Расшифровка ответа от сервера: {message}')
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
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, client_name


# @log
# def transmission_from_server(sock, my_username):
#     """
#     Функция обработки сообщений переданных на сервер
#     """
#     while True:
#         try:
#             message = rec_message(sock)
#             if ACTION in message and message[ACTION] == MESSAGE and \
#                     SENDER in message and DESTINATION in message \
#                     and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
#                 print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
#                       f'\n{message[MESSAGE_TEXT]}')
#                 logger.info(f'Получено сообщение от пользователя {message[SENDER]}:'
#                             f'\n{message[MESSAGE_TEXT]}')
#             else:
#                 logger.error(f'Получено некорректное сообщение с сервера: {message}')
#         except IncorrectDataReceivedError:
#             logger.error(f'Не удалось декодировать полученное сообщение.')
#         except (OSError, ConnectionError, ConnectionAbortedError,
#                 ConnectionResetError, json.JSONDecodeError):
#             logger.critical(f'Потеряно соединение с сервером.')
#             break
#
#
# @log
# @log
# def user_interactive(sock, username):
#     """
#     Функция запрашивает команды и занимается отправкой сообщений
#     """
#     print_help()
#     while True:
#         command = input('Введите команду: ')
#         if command == 'message':
#             create_message(sock, username)
#         elif command == 'help':
#             print_help()
#         elif command == 'exit':
#             transmit_message(sock, create_exit_message(username))
#             print('Завершение соединения.')
#             logger.info('Завершение работы по команде пользователя.')
#             # Задержка сообщения
#             time.sleep(0.5)
#             break
#         else:
#             print('Команда задана неверно, попробойте снова. help - вывести поддерживаемые команды.')


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
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, режим работы: {client_name}')

    try:
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward.connect((server_address, server_port))
        transmit_message(forward, show_presence(client_name))
        answer = ans_handling(rec_message(forward))
        logger.info(f'Получен ответ от сервера {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        logger.error(f'Сервер выявил ошибку при подключении: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as miss_error:
        logger.error(
            f'В полученных данных отсутствует необходимое поле'
            f'{miss_error.missing_field}'
        )
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f'Не удалось соедениться с сервером {server_address}:{server_port}, '
            f'удаленный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # запускаем процесс приема сообщений если все настроено верно
        module_reciver = ClientReader(client_name, forward)
        module_reciver.daemon = True
        module_reciver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        module_sender = ClientSender(client_name, forward)
        module_sender.daemon = True
        module_sender.start()
        logger.debug('Запущены процессы')

        # основной цикл которой отрабатывает пока не потеряно соединение
        # или пользователь не вышел через exit
        while True:
            time.sleep(1)
            if module_reciver.is_alive() and module_sender.is_alive():
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
