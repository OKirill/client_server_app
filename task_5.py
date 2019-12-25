"""5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com
и преобразовать результаты из байтовового в строковый тип на кириллице"""

import subprocess

PING_SOURCE = [['ping', 'yandex.ru'], ['ping', 'youtube.com']]

for ping_this in PING_SOURCE:
    subproc_ping = subprocess.Popen(ping_this, stdout=subprocess.PIPE)

    times = 0

    for line in subproc_ping.stdout:
        print(line)
        line = line.decode('cp866').encode('utf-8')
        print(line.decode('utf-8'))
        times += 1
    else:
        break
