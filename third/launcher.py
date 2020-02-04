"""Launcher"""

import subprocess

PROCESSES = []

while True:
    ACTION = input('Choose your action: q - exit, '
                   's - start servers and clients, x - close all windows: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESSES.append(subprocess.Popen('python server.py',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n test1',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n test2',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n test3',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()
