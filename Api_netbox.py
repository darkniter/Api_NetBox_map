from processor import ports, device, device_type, map_devices, ip_adresses, finder, delete_obj, regions
import config
import pynetbox
net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def main():
    # loaded items from map
    filtred_map = map_devices.map_load()
    xl_map = map_devices.excel_map()

    # setup missing types
    new_types = device_type.add_device_types(filtred_map)

    print("added:", new_types)

    if len(new_types) > 0:
        # get type list for ports
        ports.init_ports(new_types)

    # add new devices from map
    info_ip = device.device_name_init(filtred_map, xl_map, 'Elm_street')

    if len(info_ip) > 0:
        # setup ip adresses for new added devices
        info_added_device = ip_adresses.setup_ip(info_ip)

        return info_added_device

    return None


if __name__ == "__main__":
    print(main())
    # delete_obj.delete_object(**{'name': 'sites', 'list': {'Kabanovo'}})
    # delete_object(**{'name': 'device_types', 'list': {'DES-3028'}})

    # print(finder.find_site_child('Kabanovo'))
    # print(find_type_child('DES-3028'))

    # map_devices.map_filtration_init()
    # map_devices.excel_map()

    # regions.add_regions("Magic_Placement", "Lenina 97")
