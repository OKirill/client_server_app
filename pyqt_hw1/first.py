'''
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
'''

import os
import subprocess
from ipaddress import ip_address

hostsList = ['185.60.112.157', '8.8.8.8', 'battle.net']  # список проверяемых хостов
result = {'Доступные узлы':"", 'Недоступные узлы':""}  # словарь с результатами (для задания 3)

DNL = open(os.devnull, 'w')  # заглушка, чтобы поток не выводился на экран


def ip_check(value):
    """
        Проверка является ли введеное значение IP-адресом
        :param value: присланное значение
        :return: ipv4: полученный ip адрес из переданного значения
            Exception: ошибка при невозможности получения ip адреса из значения
    """
    try:
        ipv4 = ip_address(value)
    except ValueError:
        raise Exception("Некорректный ip адрес")
    return ipv4


def host_ping(hostsList, getList=False):
    """
       Проверка доступности хостов
       :param hostsList: список хостов
               getList: признак нужно ли одать результат в виде словаря (для задания №3)
       :return: словарь результатов проверки, если требуется
    """
    print('Начинаю проверку доступности узлов...')
    for host in hostsList:  # цикл для каждого значения в переданном списке
        try:
            ipv4 = ip_check(host)  # проверяем является ли значение ip-адресом
        except Exception as e:
            print(f"{host} - {e}, воспринимаю как доменное имя")
            ipv4 = host                     # если не являемся, то не приводим его к ip-адресу, думае, что доменное имя
        response = subprocess.Popen(["ping",  str(ipv4)], stdout=DNL)  # получаем результат вызова ping хост
        if response == 0:
            result['Доступные узлы'] += f"{str(ipv4)}\n"
            resString = f'{str(ipv4)} - Узел доступен'
        else:
            result['Недоступные узлы'] += f"{ipv4}\n"
            resString = f'{str(ipv4)} - Узел недоступен'
        if not getList:         # если результаты не надо добавлять в словарь, значит отображать их в консоли
            print(resString)
    if getList:                # если требуется вернуть словарь (для задачи 3), то возвращаем
        return result


if __name__ == '__main__':
    host_ping(hostsList)
    print(result)

