import socket
import sys
import json
from backup.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEF_IP, \
    DEF_IP_ADRRES
from backup.utils import rec_message, transmit_message


def handling_mess_from_client(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        DEF_IP_ADRRES: 400,
        ERROR: 'Not a complete Request'
    }


def main():
    try:
        if '-p' in sys.argv:
            listner_to_the_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listner_to_the_port = DEF_IP
        if listner_to_the_port < 1024 or listner_to_the_port > 65535:
            raise ValueError
    except IndexError:
        print("Нужно указать номер порта после параметра -\'p\'.")
        sys.exit(1)
    except ValueError:
        print(
            'Пожалуста введите подобающий номер порта(в диапазоне от 1024 до 65535.'
        )
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listner_to_the_adress = sys.argv[sys.argv.index('-a') + 1]
        else:
            listner_to_the_adress = ''

    except IndexError:
        print('Укажите адресс который будет прослушивать сервер после параметра -\'a\'.')
        sys.exit(1)

    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward.bind((listner_to_the_adress, listner_to_the_port))

    forward.listen(MAX_CONNECTIONS)

    while True:
        client, client_adress = forward.accept()
        try:
            message_from_client = rec_message(client)
            print(message_from_client)
            response = handling_mess_from_client(message_from_client)
            transmit_message(client, response)
            client.close()
        except(ValueError, json.JSONDecodeError):
            print('Получено недопустимое сообщение от клиента')
            client.close()


if __name__ == '__main__':
    main()


