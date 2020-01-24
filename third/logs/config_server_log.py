"""Config servers log"""

import sys
import os
import logging
import logging.handlers
from backup.variables import LOGGING_LEVEL
sys.path.append('../')

# Creating formatter:
SERVER_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Prep filename for logging
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

# crating streams outputs of logs
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
LOG_FILE.setFormatter(SERVER_FORMATTER)

# creating logger
LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

# maintance
if __name__ == '__main__':
    LOGGER.critical('Critical error')
    LOGGER.error('Error')
    LOGGER.debug('Debugging info')
    LOGGER.info('Info message')
