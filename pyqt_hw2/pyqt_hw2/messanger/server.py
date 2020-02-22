"""
Серверная часть программы
"""
import socket
import sys
import json
import logging
import select
import time
import argparse
import logs.config_server_log
from errors import IncorrectDataReceivedError
from backup.variables import *
from backup.utils import *
from decos import log
from descrptrs import Port
from metaclasses import ServerMaker

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


class Server(metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port):
        self.addr = listen_address
        self.port = listen_port

        self.clients = []

        self.messages = []

        self.names = dict()

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

    def main_loop(self):

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
                transmit_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Выбер.'
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
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            transmit_message(client, response)
            return


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

    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
