from processor import ports, device, device_type, map_devices, ip_adresses, VLAN, ReMoved
import processor.config as config
import pynetbox
from processor.utilities.transliteration import transliterate
from functools import lru_cache

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def Switches(region, vlans_map, xl_map):
    ip_list = None

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

    # setup missing types
        new_types = device_type.add_device_types('Switch', filtred_map)

        print("added:", new_types)

        if len(new_types) > 0:
            # get type list for ports
            ports.init_ports(new_types)

        # add new devices from map
        info_ip = device.device_name_SWITCH(filtred_map, xl_map, street)
        print(info_ip)
        if len(info_ip) > 0:
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
    print("added:", new_types)

    if len(new_types) > 0:
        # get type list for ports
        ports.init_ports(new_types)

    # vlans_list = Vlan_init()

    info_ip = device.device_name_MODEM(filtred_map, vlans_list)
    print('added_dev:', info_ip)

    if len(info_ip) > 0:
        ip_list = ip_adresses.setup_ip(info_ip)

    return ip_list


def load_conf_dev_type():
    new_types = device_type.add_device_types('dev')

    print("added:", new_types)

    if len(new_types) > 0:
        # get type list for ports
        ports.init_ports(new_types)


@lru_cache(5000)
def loader_maps():
    # loaded maindevices
    xl_map = map_devices.excel_map(config.PATH_XL, config.CSV_PATH)
    xl_map.update(map_devices.excel_map(config.PATH_BROKEN, config.CSV_PATH_BROKEN))

    vlans_map = Vlan_init()

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


def pre_conf():
    ip_list = []

    vlans_map, xl_map = loader_maps()
    regions = [
                'Орехово-Зуево',
                'Кабаново',
                'Куровское',
                'Демихово',
                'Ликино-Дулёво',
               ]

    for load in regions:
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
