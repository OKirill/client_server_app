"""
Серверная часть программы
"""
import socket
import sys
import json
import logging
import select
import time
import threading
import argparse
import logs.config_server_log
from errors import IncorrectDataReceivedError
from backup.variables import *
from backup.utils import *
from decos import log
from descrptrs import Port
from metaclasses import ServerMaker
from server_database import ServerStorage

logger = logging.getLogger('server')


@log
def parser_handling():
    """
    Пробегаем по аргументам терминала
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEF_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


class Server(threading.Thread, metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.addr = listen_address
        self.port = listen_port

        self.database = database
        self.clients = []

        self.messages = []

        self.names = dict()

        super().__init__()

    def init_socket(self):
        logger.info(
            f'Запущен сервер, с портом: {self.port} , адрес с которого принимаются подключения: {self.addr}. Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward.bind((self.addr, self.port))
        forward.settimeout(0.5)

        # Начинаем слушать сокет.
        self.sock = forward
        self.sock.listen()

    def run(self):
        self.init_socket()

        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.handling_mess_from_client(rec_message(client_with_message), client_with_message)
                    except:
                        logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    logger.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        """
        Отправка сообщения конкретному пользователю
        :param message:
        :param names:
        :param listen_socks:
        :return:
        """
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            transmit_message(self.names[message[DESTINATION]], message)
            logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                        f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    def handling_mess_from_client(self, message, client):
        """
        Обработка сообщения от клиента в виде словаря,
        проверка и отправка ответа.
        :param message:
        :param messages_list:
        :param client:
        :param clients:
        :param names:
        :return:
        """
        logger.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение presence получаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and \
                TIME in message and USER in message:
            # Регистрация пользователя если он ещё не зареган
            #  иначе  завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                transmit_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Выберите другое имя - это уже занято.'
                transmit_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Добавляем в очередь на ответ
        elif ACTION in message and message[ACTION] == MESSAGE and \
                DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            transmit_message(client, response)
            return


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')

# @log
# def handling_mess_from_client(self, message, client):
#     """
#     Обработка сообщения от клиента в виде словаря,
#     проверка и отправка ответа.
#     :param message:
#     :param messages_list:
#     :param client:
#     :param clients:
#     :param names:
#     :return:
#     """
#     logger.debug(f'Разбор сообщения от клиента : {message}')
#     # Если это сообщение presence получаем и отвечаем
#     if ACTION in message and message[ACTION] == PRESENCE and \
#             TIME in message and USER in message:
#         # Регистрация пользователя если он ещё не зареган
#         #  иначе  завершаем соединение.
#         if message[USER][ACCOUNT_NAME] not in self.names.keys():
#             self.names[message[USER][ACCOUNT_NAME]] = client
#             transmit_message(client, RESPONSE_200)
#         else:
#             response = RESPONSE_400
#             response[ERROR] = 'Выбер.'
#             transmit_message(client, response)
#             self.clients.remove(client)
#             client.close()
#         return
#     # Добавляем в очередь на ответ
#     elif ACTION in message and message[ACTION] == MESSAGE and \
#             DESTINATION in message and TIME in message \
#             and SENDER in message and MESSAGE_TEXT in message:
#         self.messages.append(message)
#         return
#     # Если клиент выходит
#     elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
#         self.clients.remove(self.names[ACCOUNT_NAME])
#         self.names[ACCOUNT_NAME].close()
#         del self.names[ACCOUNT_NAME]
#         return
#     else:
#         response = RESPONSE_400
#         response[ERROR] = 'Запрос некорректен.'
#         transmit_message(client, response)
#         return
#
#
# @log
# def process_message(message, names, listen_socks):
#     """
#     Отправка сообщения конкретному пользователю
#     :param message:
#     :param names:
#     :param listen_socks:
#     :return:
#     """
#     if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
#         transmit_message(names[message[DESTINATION]], message)
#         logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
#                     f'от пользователя {message[SENDER]}.')
#     elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
#         raise ConnectionError
#     else:
#         logger.error(
#             f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
#             f'отправка сообщения невозможна.')


def main():
    listen_address, listen_port = parser_handling()

    database = ServerStorage()

    # Создание экземпляра класса - сервера и его запуск:
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Печатаем справку:
    print_help()

    # Основной цикл сервера:
    while True:
        command = input('Введите комманду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(database.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loghist':
            name = input(
                'Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    main()
