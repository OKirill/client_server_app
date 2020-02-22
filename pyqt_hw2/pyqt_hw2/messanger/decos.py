"""Модуль декоратор log"""

import sys
import logging
import logs.config_server_log
import logs.config_client_log


if sys.argv[0].find('client') == -1:
    # Обращение к серверу если не клиент
    logger = logging.getLogger('server')
else:
    # или к клиенту если не сервер
    logger = logging.getLogger('client')


def log(func_to_log):
    """сам декоратор"""
    def log_saver(*args, **kwargs):

        logger.debug(
            f'Отработана функция {func_to_log.__name__} c аргументами:  {args}, {kwargs}. '
            f'И вызваным модулем {func_to_log.__module__}')
        ret = func_to_log(*args, **kwargs)
        return ret
    return log_saver
