import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def dump_order_to_json(item, quantity, price, buyer, date):
    filename = os.path.join(BASE_DIR, 'orders.json')

    if os.path.exists(filename):
        data = {}

        with open(filename, encoding="utf-8") as file:
            data = json.loads(file.read())

        data['orders'].append({'item': item,
                               'quantity': quantity,
                               'price': price,
                               'buyer': buyer,
                               'date': date})

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                data, file, indent=4, separators=(
                    ',', ': '), ensure_ascii=False)

        print(f'Данные внесены в {filename}')

    else:
        print(f'Запрашиваемый файл по пути {filename} не найден')


if __name__ == '__main__':
    dump_order_to_json(
        'Nintendo Switch',
        '1',
        '16400',
        'Олейник',
        '05.01.2020')
    dump_order_to_json('PS4 PRO', '1', '28900', 'Брусова', '04.01.2020')
