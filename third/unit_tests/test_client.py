import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from backup.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import show_presence, ans_handling


class ClassForTesting(unittest.TestCase):


    """Class for testing """

    def test_def_show_presence(self):
        """test for good request"""
        test = show_presence()
        test[TIME]= 1.1 # u need to setup time manually
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_for_200_answer(self):
        """test for maintaing 200 response"""
        self.assertEqual(ans_handling({RESPONSE:200}), '200 : OK')

    def test_for_400_answer(self):
        """test for maintaining 400 response"""
        self.assertEqual(ans_handling({RESPONSE: 400, ERROR: 'False Request'}), '400 : False Request')

    def test_for_no_response(self):
        """Test without response """
        self.assertRaises(ValueError, ans_handling, {ERROR: 'False Request'})

if __name__ == '__main__':
    unittest.main()
