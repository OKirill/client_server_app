"""Преобразовать слова «разработка», «администрирование», «protocol», «standard»
 из строкового представления в байтовое и выполнить
  обратное преобразование (используя методы encode и decode)."""

LWORDS = ['protocol', 'standart']

for w in LWORDS:
    a = w.encode('utf-16')
    print(f'{w} ------encoding----> {a} ')
    print(f'type = {type(a)}')
    print(f'{a} ------decoding----> {w}')
    b = a.decode('utf-16')
    print(f'{type(b)}')

WORDS = ['разработка', 'администрирование']

for w in WORDS:
    a = w.encode('utf-8')
    print(f'{w} ------encoding----> {a} ')
    print(f'type = {type(a)}')
    print(f'{a} ------decoding----> {w}')
    b = a.decode('utf-8')
    print(f'{type(b)}')
