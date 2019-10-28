import json
import os
import processor.config as config
import csv
from processor.utilities.transliteration import transliterate


def from_json(map):
    json_map = open(map, 'r', encoding='utf-8-sig')
    python_map = json.load(json_map)
    return python_map


def filter(filtration_val=''):
    filtred = {}

    python_map = from_json(config.DEVICE_FILTRED)

    for row in python_map:
        finded = python_map[row].get('address')
        if finded and finded.startswith(filtration_val):
            filtred.update({row: python_map[row]})
    print('')
    return filtred


def map_filtration_init(filter_ip=None):

    fname = config.MAP_LOCATION

    if (os.path.isfile(fname)):
        os.remove(fname)

    json_file = open(fname, 'a+')
    json_file.write(json.dumps(filter(filter_ip)))
    json_file.close()


def map_load(fname):

    with open(fname, 'r', encoding='utf-8-sig') as map_device:
        loading_map = json.load(map_device)

    return loading_map


def hint_init(hint, val):
    result = {}
    count = -1
    if len(hint) == len(val):
        for element in hint.keys():
            count += 1
            if element.find('RESERVED') == -1:
                result.update({element: val[count]})
        return result


def excel_map(fname):
    if os.path.isfile(fname):
        os.remove(fname)
    map_xl = {}
    csv.register_dialect('csv', delimiter=';', quoting=csv.QUOTE_NONE)
    with open(config.CSV_PATH, 'r') as xl:
        result = csv.reader(xl, 'csv')
        header = []
        for row in result:
            init_name = row[0]
            if init_name == 'P_STREET':
                header = row[7: len(row): 1]
            else:
                hint = {}
                hint = hint_init({}.fromkeys([*header]), row[7:len(row):1])
                row[0] = transliterate(row[0])
                if len(row[4]) > 0:
                    row[3] = row[4]
                map_xl.update({row[3]: [row[0], row[1], init_name, hint]})
                if len(row[3]) == 0:
                    print({row[3]: [row[0], row[1]]})

    json_file = open(fname, 'a+', encoding='utf-8-sig')
    json_file.write(json.dumps(map_xl))
    json_file.close()

    return map_xl


def VLAN_map(filter_region=None):
    csv.register_dialect('csv', delimiter=';', quoting=csv.QUOTE_NONE)
    regions = {}
    with open(config.VLAN_PATH, 'r', encoding='utf-8-sig') as xl:
        result = csv.reader(xl, 'csv')

        for row in result:
            if row[0] != '' and row[1] == '':
                regions.update({transliterate(row[0]): []})
            elif len(row) == 16 and transliterate(row[15]) in regions:
                regions[transliterate(row[15])].append(row)
            else:
                regions.update({'description': row})

    if (os.path.isfile(config.VLAN_PATH_JSON)):
        os.remove(config.VLAN_PATH_JSON)

    json_file = open(config.VLAN_PATH_JSON, 'a+', encoding='utf-8-sig')
    json_file.write(json.dumps(regions))
    json_file.close()

    description = regions.pop('description')
    regions = VLAN_map_format(regions, description, filter_region)

    return regions


def VLAN_map_format(regions, description, filter_region=None):

    for row in regions:
        if not row == 'description':
            for site in regions[row]:
                site[11] = '-'.join([site[9].split('-')[0], 'cctv', site[11]])
                site[1] = transliterate(site[1])
                site[13] = transliterate(site[13])
                site[11] = '-'.join([site[11], site.pop(12) + description[12]])
                site[9] = '-'.join([site[9], site.pop(10) + description[10]])
                site[7] = '-'.join([site[7], site.pop(8) + description[8]])
                site[5] = '-'.join([site[5], site.pop(6) + description[6]])
                site[3] = '-'.join([site[3], site.pop(4) + site[8]])
    if filter_region:
        regions = {transliterate(filter_region): regions[transliterate(filter_region)]}

    return regions


if __name__ == "__main__":
    VLAN_map("Куровское")
