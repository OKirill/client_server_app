import socket
import sys
import json
from backup.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEF_IP, \
    DEF_IP_ADRRES
from backup.utils import rec_message, transmit_message


def handling_mess_from_client(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message and message[USER][
        ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return  {
        DEF_IP_ADRRES: 400,
        ERROR: 'Not a complete Request'
    }


def main():
    try:
        if '-p' in sys.argv:
            listner_to_the_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listner_to_the_port = DEF_IP
        if listner_to_the_port < 1024
