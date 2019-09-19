import json
import os
import config
import csv
from utilities.transliteration import transliterate as revers


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


def VLAN_map(filter_region=None):
    csv.register_dialect('csv', delimiter=';', quoting=csv.QUOTE_NONE)
    regions = {}
    with open(config.VLAN_PATH, 'r', encoding='utf-8-sig') as xl:
        result = csv.reader(xl, 'csv')

        for row in result:
            if row[0] == row[1]:
                regions.update({revers(row[0]): []})
            elif len(row) == 14:
                regions[revers(row[13])].append(row)
            else:
                regions.update({'Hint': row})

    if (os.path.isfile(config.VLAN_PATH_JSON)):
        os.remove(config.VLAN_PATH_JSON)

    json_file = open(config.VLAN_PATH_JSON, 'a+', encoding='utf-8-sig')
    json_file.write(json.dumps(regions))
    json_file.close()

    hint = regions.pop('Hint')
    regions = VLAN_map_format(regions, hint, filter_region)

    return regions


def VLAN_map_format(regions, hint, filter_region=None):

    for row in regions:
        if not row == 'Hint':
            for site in regions[row]:
                site[11] = '-'.join([site[9].split('-')[0], 'cctv', site[11]])
                site[1] = revers(site[1])
                site[13] = revers(site[13])
                site[11] = '-'.join([site[11], site.pop(12) + hint[12]])
                site[9] = '-'.join([site[9], site.pop(10) + hint[10]])
                site[7] = '-'.join([site[7], site.pop(8) + hint[8]])
                site[5] = '-'.join([site[5], site.pop(6) + hint[6]])
                site[3] = '-'.join([site[3], site.pop(4) + hint[4]])
    if filter_region:
        regions = {revers(filter_region): regions[revers(filter_region)]}

    return regions


if __name__ == "__main__":
    VLAN_map("Куровское")
