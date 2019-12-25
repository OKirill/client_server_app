"""6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
 «сетевое программирование», «сокет», «декоратор». Проверить кодировку файла по умолчанию.
  Принудительно открыть файл в формате Unicode и вывести его содержимое."""

import locale

ENC = locale.getpreferredencoding()
print(ENC)

FILL_TEST_FILE = ['сетевое программирование', 'сокет', 'декоратор']

with open('test_file.txt', 'w', encoding='utf-8') as f:
    for word in FILL_TEST_FILE:
        f.write(word + '\n')
        print(word)
