"""2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в
последовательность кодов (не используя методы encode и decode)
 и определить тип, содержимое и длину соответствующих переменных."""

WORDS = [b'class', b'function', b'method']

for word in WORDS:
    print(f'тип переменной: {type(word)}\n')
    print(f'содержание переменной - {word}\n')
    print(f'длинна строки: {len(word)}\n')
