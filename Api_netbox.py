import pynetbox
import config
from processor import ports, device, device_type, map_devices, ip_adresses

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def main():

    map_devices()
    # loaded item from map
    filtred_map = map_devices.map_load()
    # setup missing types
    new_types = device_type.added_device_types(filtred_map, net_box)

    if len(new_types) > 0:
        ports.init_ports(new_types, net_box)
    # will return dictionary with basic info about devices
    namespace_map = device.device_name_init(filtred_map, 'test', net_box)

    info_ip = device.add_devices(namespace_map)   # add new devices from map

    if len(info_ip) > 0:

        primary_info = ip_adresses.setup_ip(info_ip)

        info_added_device = ip_adresses.set_primary(primary_info)

        return info_added_device

    return None


if __name__ == "__main__":
    print(main())
