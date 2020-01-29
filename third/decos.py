"""Модуль декоратор log"""

import sys
import logging
import logs.config_server_log
import logs.config_client_log


if sys.argv[0].find('client') == -1:
    # Обращение к серверу если не клиент
    LOGGER = logging.getLogger('server')
else:
    # или к клиенту если не сервер
    LOGGER = logging.getLogger('client')


def log(func_to_log):
    """сам декоратор"""
    def log_saver(*args, **kwargs):
        ret = func_to_log(*args, **kwargs)
        LOGGER.debug(f'Отработана функция {func_to_log.__name__} c аргументами:  {args}, {kwargs}. '
                     f'И вызваным модулем {func_to_log.__module__}')
        return ret
    return log_saver
