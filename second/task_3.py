import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(BASE_DIR, 'file.yaml')
data = {
    'consoles': [
        'XBOX ONE S',
        'XBOX ONE X',
        'PS4 Slim',
        'PS4 PRO',
        'NINTENDO SWITCH lite',
        'NINTENDO SWITCH'],
    'total_quantity': 6,
    'price': {
        'XBOX ONE S': '223$',
        'XBOX ONE X': '456$',
        'PS4 Slim': '232$',
        'PS4 PRO': '402$',
        'NINTENDO SWITCH lite': '210$',
        'NINTENDO SWITCH': '245$'}}

with open(filename, 'a') as file:
    yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

with open(filename) as file:
    print(file.read())
