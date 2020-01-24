"""Errors handling"""


class IncorrectDataReceivedError(Exception):
    """
        Incorrect data from socket
    """
    def __str__(self):
        return "Received incorrect message from PC"


class NoDictInputError(Exception):
    """
    exception argument not a dict
    """
    def __str__(self):
        return "Functions argument need to be dict."


class ReqFieldMissingError(Exception):
    """
    Missed - missing required argument in dict
    """
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'In received dict is missing a requierd argument {self.missing_field}'