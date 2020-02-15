'''
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
'''

from first import ip_check as ipcheck, host_ping


def ip_number_ping(getList=False):
    """
       Запрос на вход определённое кол-во ip и их проверка
       """
    while True:
        startIp = input('Введите первый ip: ')
        try:
            ipv4Start = ipcheck(startIp)
            lastOct = int(startIp.split('.')[3])
            break
        except Exception as e:
            print(e)
    while True:
        endIp = input('Сколько ip нужно проверить?: ')
        if not endIp.isnumeric():
            print('Введите число: ')
        else:
            if (lastOct+int(endIp)) > 254:
                print(f"Можем менять только последний октет, т.е. максимальное число хостов для проверки: {254-lastOct}")
            else:
                break
    hostList = []
    [hostList.append(str(ipv4Start+x)) for x in range(int(endIp))]
    if not getList:
        host_ping(hostList)
    else:
        return host_ping(hostList, True)


if __name__== "__main__":
    host_range_ping()

