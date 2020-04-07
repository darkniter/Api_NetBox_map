from processor import ports, device, device_type, map_devices, ip_adresses, VLAN, ReMoved, regions
import processor.config as config
import pynetbox
from processor.utilities.transliteration import transliterate
from processor.utilities.Tester import comparsion
from functools import lru_cache
import json
from os import remove
from os import path
from profilehooks import timecall, profile


net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN, threading=True)


def Switches(region, vlans_map, xl_map):
    ip_list = None

    for street in vlans_map[transliterate(region[0])]:
        if street[8] == '/23':
            filter_ip = street[3].split('-')[-1].split('.')

            filter_ip = ".".join([filter_ip[0], filter_ip[1], filter_ip[2]])

        elif street[8] == '/22':
            filter_ip = street[3].split('-')[-1].split('.')

            filter_ip = ".".join(filter_ip[0:2:1])

        map_devices.map_filtration_init(filter_ip)
    # loaded items from map
        filtred_map = map_devices.map_load(config.MAP_LOCATION)

    # setup missing types
        new_types = device_type.add_device_types('Switch', filtred_map)

        if len(new_types) > 0:
            print("Switch added:", new_types)
            # get type list for ports
            ports.init_ports(new_types)

        # add new devices from map
        info_ip = device.device_name_SWITCH(filtred_map, xl_map, street)
        if len(info_ip) > 0:
            print("Switches()", info_ip)
            ip_list = ip_adresses.setup_ip(info_ip)

    return ip_list


def Vlan_init(region=None):

    vlans_map = map_devices.VLAN_map(region)
    VLAN.region_add_from_vlan(vlans_map)
    VLAN.main_add_VLANs(vlans_map)

    return vlans_map


def Modems():
    vlans_list = []
    ip_list = []
    filtred_map = map_devices.from_json(config.MODEMMAP)

    new_types = device_type.add_device_types('Modem', filtred_map)

    if len(new_types) > 0:
        print("Modem added:", new_types)
        # get type list for ports
        ports.init_ports(new_types)

    # vlans_list = Vlan_init()

    info_ip = device.device_name_MODEM(filtred_map, vlans_list)
    print('added_dev:', info_ip)

    if len(info_ip) > 0:
        print("Modems()", info_ip)
        ip_list = ip_adresses.setup_ip(info_ip)

    return ip_list


def load_conf_dev_type():
    new_types = device_type.add_device_types('dev')

    if len(new_types) > 0:
        print("devs added:", new_types)
        # get type list for ports
        ports.init_ports(new_types)


def loader_maps(options_vlan='file', options_xl='file'):
    # loaded maindevices

    if options_vlan == 'load':
        if path.isfile(config.PATHVLANS_INIT):
            remove(config.PATHVLANS_INIT)
        vlans_map = Vlan_init()
        with open(config.PATHVLANS_INIT, 'w', encoding='utf-8-sig') as vlans_map_init:
            json.dump(vlans_map, vlans_map_init, indent=4, sort_keys=True)

    else:
        with open(config.PATHVLANS_INIT, 'r', encoding='utf-8-sig') as vlans_map_init:
            vlans_map = json.load(vlans_map_init)

    if options_xl == 'load':
        if path.isfile(config.XL_INIT):
            remove(config.XL_INIT)

        xl_map = map_devices.excel_map(config.PATH_XL, config.CSV_PATH)
        broken = map_devices.excel_map(config.PATH_BROKEN, config.CSV_PATH_BROKEN)
        comparsion(xl_map, broken)
        xl_map.update(broken)

        with open(config.XL_INIT, 'w', encoding='utf-8-sig') as xl_map_init:
            json.dump(xl_map, xl_map_init, indent=4, sort_keys=True)
    else:
        with open(config.XL_INIT, 'r', encoding='utf-8-sig') as xl_map_init:
            xl_map = json.load(xl_map_init)
    return vlans_map, xl_map


def rename_removed():
    removed_dev = {}
    vlans_map, xl_map = loader_maps()

    regions = [
                'Орехово-Зуево',
                'Кабаново',
                'Куровское',
                'Демихово',
                'Ликино-Дулёво',
               ]
    for region in regions:
        for street in vlans_map[transliterate(region)]:
            if street[8] == '/23':
                filter_ip = street[3].split('-')[-1].split('.')

                filter_ip = ".".join([filter_ip[0], filter_ip[1], filter_ip[2]])

            elif street[8] == '/22':
                filter_ip = street[3].split('-')[-1].split('.')

                filter_ip = ".".join(filter_ip[0:2:1])

            map_devices.map_filtration_init(filter_ip)
        # loaded items from map
            filtred_map = map_devices.map_load(config.MAP_LOCATION)
            removed_dev.update({region: ReMoved.main(region, vlans_map, xl_map, filtred_map, net_box)})
    print()
    return removed_dev


@profile
def pre_conf():
    ip_list = []

    region_list = [
                ('Кабаново', 'kb'),
                ('Демихово', 'dm'),
                ('Куровское', 'ku'),
                ('Ликино-Дулёво', 'ld'),
                ('Орехово-Зуево', 'oz'),
               ]

    for region, slug in region_list:
        regions.add_regions(transliterate(region), slug=slug)

    # vlans_map, xl_map = loader_maps('file', 'file')
    vlans_map, xl_map = loader_maps('load', 'load')

    for load in region_list:
        ip_list.append(Switches(load, vlans_map, xl_map))

    return ip_list


if __name__ == "__main__":
    load_conf_dev_type()
    print(pre_conf())
    # print(Modems())

    # print(rename_removed())
    # d#  old_name = ['TestName', 'Description', 'REMOVEDTest 44.7']
    # dev = net_box.dcim.devices.get(name=old_name[2])
    # # if dev.custom_fields['P_REMOVED'] == 1:
    # #     dev.update({"name": "REMOVED " + old_name[0]})
