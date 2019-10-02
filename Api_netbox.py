from processor import ports, device, device_type, map_devices, ip_adresses, VLAN
import processor.config as config
import pynetbox
from processor.utilities.transliteration import transliterate as revers

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def main(region=None):
    # loaded maindevices
    vlans_map = map_devices.VLAN_map(region)
    VLAN.region_add_from_vlan(vlans_map)

    VLAN.main_add_VLANs(vlans_map)
    if region:
        for street in vlans_map[revers(region)]:
            filter_ip = street[3].split('-')[-1].split('.')

            filter_ip = ".".join([filter_ip[0], filter_ip[1], filter_ip[2], ''])

            map_devices.map_filtration_init(filter_ip)
        # loaded items from map
            filtred_map = map_devices.map_load(config.MAP_LOCATION)
            xl_map = map_devices.excel_map(config.VLAN_PATH_XL)

            # setup missing types
            new_types = device_type.add_device_types('prod', filtred_map)

            print("added:", new_types)

            if len(new_types) > 0:
                # get type list for ports
                ports.init_ports(new_types)

            # add new devices from map

            info_ip = device.device_name_init(filtred_map, xl_map, street)

            if len(info_ip) > 0:
                ip_adresses.setup_ip(info_ip)

    return None


def load_conf_dev_type():
    new_types = device_type.add_device_types('dev')

    print("added:", new_types)

    if len(new_types) > 0:
        # get type list for ports
        ports.init_ports(new_types)


if __name__ == "__main__":
    main('Кабаново')
    # main()
    # load_conf_dev_type()
