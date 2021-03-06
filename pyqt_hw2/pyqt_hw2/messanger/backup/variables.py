"""Постоянные для проекта"""
import logging


DEF_PORT = 23456

DEF_IP = '127.0.0.1'

MAX_CONNECTIONS = 5

MAX_BYTES_LENGTH = 1024

ENCODING = 'utf-8'

LOGGING_LEVEL = logging.DEBUG
# ОСНОВНЫЕ КЛЮЧИ JIM ПРОТОКОЛА:

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'
# Дополнительные ключи для протокола

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
DEF_IP_ADRRES = 'def_ip_adrres'
EXIT = 'exit'

RESPONSE_200 = {RESPONSE: 200}

RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}


