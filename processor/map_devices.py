import json
import os
import config
import csv
from utilities.transliteration import transliteration as revers


def from_json(map):
    json_map = open(map, 'r')
    python_map = json.load(json_map)
    return python_map


def filter(filtration_val):
    filtred = {}

    python_map = from_json('ignored/result_map.json')

    for row in python_map:
        finded = python_map[row].get('Address')
        if finded and finded.startswith(filtration_val):
            filtred.update({row: python_map[row]})
    print('')
    return filtred


def map_filtration_init():
    ip_site = '10.140.0.'

    fname = 'ignored/filtred_map.json'

    if (os.path.isfile(fname)):
        os.remove(fname)

    json_file = open(fname, 'a+')
    json_file.write(json.dumps(filter(ip_site)))
    json_file.close()


def map_load():

    with open(config.MAP_LOCATION, 'r', encoding='utf-8-sig') as map_device:
        loading_map = json.load(map_device)

    return loading_map


def excel_map():
    map_xl = {}
    csv.register_dialect('csv', delimiter=';', quoting=csv.QUOTE_NONE)
    with open(config.CSV_PATH, 'r') as xl:
        result = csv.reader(xl, 'csv')
        for row in result:
            row[0] = revers(row[0])
            if len(row[4]) > 0:
                row[3] = row[4]
            map_xl.update({row[3]: [row[0], row[1]]})
            if len(row[3]) == 0:
                print({row[3]: [row[0], row[1]]})

    return map_xl


if __name__ == "__main__":
    # map_filtration_init()
    excel_map()
