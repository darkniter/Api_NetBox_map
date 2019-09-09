import json
import os


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




if __name__ == "__main__":
    ip_site = '10.140.0.'

    fname = 'ignored/filtred_map.json'

    if (os.path.isfile(fname)):
        os.remove(fname)

    json_file = open(fname, 'a+')
    json_file.write(json.dumps(filter(ip_site)))
    json_file.close()
