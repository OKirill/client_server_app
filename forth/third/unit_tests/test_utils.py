from backup.utils import rec_message, transmit_message
from backup.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
import sys
import os
import unittest
import json

sys.path.append(os.path.join(os.getcwd(), '..'))


class CommonTest:
    """Test class for testing recieving and sending """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.recieved_message = None

    def send(self, message_to_sent):
        """Test func for sending"""

        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.recieved_message = message_to_sent

    def recv(self, max_len):
        """Recieving data from socket"""
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class Tests(unittest.TestCase):
    """Test for act. testing"""
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 111111.111111,
        USER: {
            ACCOUNT_NAME: 'test_test'
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: 'False Request'
    }

    def test_send_message(self):
        """
            Test for sending mess
        """

        test_socket = CommonTest(self.test_dict_send)
        transmit_message(test_socket, self.test_dict_send)

        self.assertEqual(
            test_socket.encoded_message,
            test_socket.recieved_message)

        self.assertRaises(TypeError, transmit_message, test_socket, 1111)

    def test_get_message(self):
        """
        Test for rec mess
        """
        test_sock_ok = CommonTest(self.test_dict_recv_ok)
        test_sock_err = CommonTest(self.test_dict_recv_err)
        self.assertEqual(rec_message(test_sock_ok), self.test_dict_recv_ok)
        self.assertEqual(rec_message(test_sock_err), self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()
