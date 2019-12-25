"""Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе"""

WORDS = [b'attribute', b'класс', b'функция', b'type']

try:
    for w in WORDS:
        print(f'{w} - можно записпать в байтовом виде')
except SyntaxError:
    print(f'{w} - невозможно записать в байтовом виде')

"""Не было времени покапаться с исключениями но в общем кириллицу нельзя записать в байтовом виде
                SyntaxError: bytes can only contain ASCII literal characters.
"""
