from processor import ports, device, device_type, map_devices, ip_adresses


def main():
    # init filtred map
    # map_devices.map_filtration_init()

    # loaded items from map
    filtred_map = map_devices.map_load()
    # setup missing types
    new_types = device_type.add_device_types(filtred_map)

    print("added:", new_types)

    if len(new_types) > 0:
        # get type list for ports
        ports.init_ports(new_types)

    # add new devices from map
    info_ip = device.device_name_init(filtred_map, 'test')

    if len(info_ip) > 0:
        # setup ip adresses for new added devices
        info_added_device = ip_adresses.setup_ip(info_ip)

        return info_added_device

    return None


if __name__ == "__main__":
    print(main())


def delete_object(*arg):

    def site():
        pass

    def device():
        pass

    def device_type(name):
        pass

    return arg()
