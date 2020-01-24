"""Server tests"""
import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from server import handling_mess_from_client
from backup.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE


class TestServerClass(unittest.TestCase):
    """Class with tests for server part"""

    err_dict = {
        RESPONSE: 400,
        ERROR: "False Request"
    }
    good_dict = {RESPONSE: 200}

    def test_if_nothing(self):
        """error if there is no action"""
        self.assertEqual(handling_mess_from_client(
            {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_unknown_action(self):
        """error if unknown action"""
        self.assertEqual(handling_mess_from_client(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_missing_time(self):
        """error if request has no time argument"""
        self.assertEqual(handling_mess_from_client(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_user(self):
        """No user error"""
        self.assertEqual(handling_mess_from_client(
            {ACTION: PRESENCE, TIME: '1.1'}), self.err_dict)

    def test_not_matching_user(self):
        self.assertEqual(handling_mess_from_client(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest1'}}), self.err_dict)

    def test_good_request(self):
        """good request"""
        self.assertEqual(handling_mess_from_client(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.good_dict)


if __name__ == '__main__':
    unittest.main()
