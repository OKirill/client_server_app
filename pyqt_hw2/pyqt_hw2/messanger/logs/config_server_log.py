"""Config servers log"""

import sys
import os
import logging
import logging.handlers
from backup.variables import LOGGING_LEVEL
sys.path.append('../')

# Creating formatter:
server_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Prep filename for logging
path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'server.log')

# crating streams outputs of logs
steam = logging.StreamHandler(sys.stderr)
steam.setFormatter(server_formatter)
steam.setLevel(logging.INFO)
log_file = logging.handlers.TimedRotatingFileHandler(path, encoding='utf8', interval=1, when='D')
log_file.setFormatter(server_formatter)

# creating logger
logger = logging.getLogger('server')
logger.addHandler(steam)
logger.addHandler(log_file)
logger.setLevel(LOGGING_LEVEL)

# maintance
if __name__ == '__main__':
    logger.critical('Test critical event')
    logger.error('Test error ivent')
    logger.debug('Test debug ivent')
    logger.info('Test info ivent')
