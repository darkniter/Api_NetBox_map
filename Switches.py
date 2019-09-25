import json
import os

vendors = {'D_link': ['DES', 'DGS'], 'Eltex': ['MES'], 'Zyxel': ['IES'], 'Other_vendor': [], 'None_vendor': [], }
# vendors.update({'Cisco': ['WS-']})


def main():
    map_group = {}

    map_dev = open('ignored/result_map.json', 'r')
    map_dev_all = json.load(map_dev)
    map_group = filter_by_group_type(map_dev_all, '34')
    
    sorted_group, result_lenght = result(map_group)

    return sorted_group, result_lenght


def result(map_group):
    result_lenght = len(map_group)

    sorted_group = sort_group(map_group)

    for lists in vendors:
        if not(lists in ['Other_vendor', 'None_vendor']):
            sorted_group.update(untwin(sorted_group.pop(lists), lists))
        else:
            sorted_group.update(unlist(sorted_group.pop(lists), lists))
    return sorted_group, result_lenght


def filter_by_group_type(map_all, group):

    map_group = {}

    for dev_name, dev in map_all.items():
        if (not dev_name == 'Apperance') and dev.get('Group') == group:
            map_group.update({dev_name: dev})

    return map_group


def unlist(model_list, name_vendor):
    result = {}
    count = 0
    for address in model_list:
        count += 1
        result.update({str(count): address})
    return {name_vendor: result}


def untwin(model_list, name_vendor):
    result = {}
    lenght = len(model_list)

    for model in model_list:
        if model.upper() not in result:
            result.update({model.upper(): 1})
        else:
            result[model.upper()] += 1

    result.update({'total_count': lenght})

    return {name_vendor: result}


def sort_group(map_group):
    map_group_result = {}
    for vendor in vendors:
        map_group_result.update({vendor: []})

    for dev_name, dev in map_group.items():
        element_34 = dev
        if element_34.get('Hint'):
            element_34['Hint'] = element_34['Hint'].split('\n')[0]
            map_group_result = hint_in_vendors(element_34, map_group_result)
        else:
            map_group_result['None_vendor'].append(element_34)

    return map_group_result


def hint_in_vendors(element, map_group):

    flag = False

    if isinstance(element['Name'], list):
        element['Name'] = '-'.join(element['Name'])

    for vendor in vendors:
        if element['Hint'][0:3:1] in vendors[vendor]:
            element['Hint'] = element['Hint'].split(' ')[0]
            map_group[vendor].append(element['Hint'])
            flag = True

    if flag is False:
        map_group['Other_vendor'].append(element)

    return map_group


def test_count(map_dev, count):
    flag = None
    result_count = 0
    for vend in vendors:
        if map_dev[vend].get('total_count'):
            result_count += map_dev[vend]['total_count']
        else:
            result_count += len(map_dev[vend])

    if count == result_count:
        flag = True
    else:
        flag = False

    return flag, result_count, count


def to_json(object_python, fname):
    json_file = open(fname, 'w+', encoding='utf-8')
    json_file.write(json.dumps(object_python))
    json_file.close()


if __name__ == "__main__":
    group, start_lenght_group = main()

    print(test_count(group, start_lenght_group))

    if (os.path.isfile('ignored/error_vendors.json')):
        os.remove('ignored/error_vendors.json')

    to_json((group['Other_vendor'], group['None_vendor']), 'C:/Project/Api_NetBox_map/ignored/error_vendors.json')
    to_json(group, 'ignored/models.json')
    print(group['Other_vendor'], '\n')
