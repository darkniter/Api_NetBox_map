from processor import ports, device, device_type, map_devices, ip_adresses, VLAN
import processor.config as config
import pynetbox
net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def main(region=None):
    # loaded maindevices
    vlans_map = map_devices.VLAN_map(region)
    VLAN.region_add_from_vlan(vlans_map)

    VLAN.main_add_VLANs(vlans_map)

    filter_ip = vlans_map['Kurovskoe'][1][3].split('-')[-1].split('.')

    filter_ip = ".".join([filter_ip[0], filter_ip[1], filter_ip[2], ''])

    map_devices.map_filtration_init(filter_ip)
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
    info_ip = device.device_name_init(filtred_map, xl_map, vlans_map['Kurovskoe'][1][1])

    if len(info_ip) > 0:
        # setup ip adresses for new added devices
        info_added_device = ip_adresses.setup_ip(info_ip)

        return info_added_device

    return None


if __name__ == "__main__":
    # print(main())
    print(main('Куровское'))

    # delete_obj.delete_object(**{'name': 'sites', 'list': {'Kabanovo'}})
    # delete_object(**{'name': 'device_types', 'list': {'D-Link DES-3028'}})

    # print(finder.find_site_child('Kabanovo'))
    # print(find_type_child('DES-3028'))

    # regions.add_regions("Magic_Placement", "Lenina 97")
