'''
Написать функцию table_ip_range(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате
(использовать модуль tabulate). Таблица должна состоять из двух колонок
'''

from second import ip_number_ping
from tabulate import tabulate


def table_ip_range():
    """
           Запрос диапазона ip адресов,проверка и вывод

           """
    resDict = ip_number_ping(True)
    print()
    print(tabulate([resDict], headers='keys', tablefmt="pipe", stralign="center"))


if __name__ == "__main__":
    table_ip_range()
