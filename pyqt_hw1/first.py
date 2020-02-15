'''
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
'''

import os
import subprocess
from ipaddress import ip_address

hostsList = ['185.60.112.157', '8.8.8.8', 'battle.net']
result = {'Доступные узлы':"", 'Недоступные узлы':""}

DNL = open(os.devnull, 'w')


def ip_check(value):
    """
        Проверка на валидность
    """
    try:
        ipv4 = ip_address(value)
    except ValueError:
        raise Exception("Некорректный ip адрес")
    return ipv4


def host_ping(hostsList, getList=False):
    """
       Проверяем доступен ли хост

    """
    print('Начинаю проверку доступности узлов...')
    for host in hostsList:  
        try:
            ipv4 = ip_check(host)
        except Exception as e:
            print(f"{host} - {e}, воспринимаю как доменное имя")
            ipv4 = host
        response = subprocess.Popen(["ping",  str(ipv4)], stdout=DNL)
        if response == 0:
            result['Доступные узлы'] += f"{str(ipv4)}\n"
            resString = f'{str(ipv4)} - Узел доступен'
        else:
            result['Недоступные узлы'] += f"{ipv4}\n"
            resString = f'{str(ipv4)} - Узел недоступен'
        if not getList:
            print(resString)
    if getList:
        return result


if __name__ == '__main__':
    host_ping(hostsList)
    print(result)

