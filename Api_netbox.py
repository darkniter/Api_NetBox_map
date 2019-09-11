import pynetbox
import config
import json
from split_pattern import search_pattern

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def map_load():

    with open(config.MAP_LOCATION, 'r') as map_device:
        loading_map = json.load(map_device)

    return loading_map


def added_device_types(map):

    new_dev = []
    for row in map:
        dev_name = map[row].get('Hint').split('\n')[0]
        net = net_box.dcim.device_types.get(model=dev_name)
        if net is None:
            new_dev.append(add_dev_type(2, dev_name))
    return new_dev


def init_ports(new_dev):

    for init in new_dev:
        id_dev = init.id
        result_ports_list = ports_list([{"name": "[01-24]", "type_port": 800, "menagemant": False},
                                        {"name": "t[25-28]", "type_port": 1100, "menagemant": False},
                                        {"name": "test", "type_port": 1200, "menagemant": False},
                                        {"name": "System", "type_port": 0, "menagemant": True}
                                        ])
        add_dev_temp(id_dev, result_ports_list)

    return None


def ports_list(initiation_list):

    result = []

    for ports_group in initiation_list:

        init_group = search_pattern(ports_group['name'])

        for record in init_group:
            result.append({"name": record,
                           "type_port": ports_group['type_port'],
                           "menagemant": ports_group['menagemant']})

    return result


def add_dev_temp(device_type_id, names):

    for name in names:

        result = net_box.dcim.interface_templates.create({"device_type": device_type_id,
                                                          "name": name['name'],
                                                          "type_port": name['type_port'],
                                                          "menagemant": name['menagemant']})

    return result


def add_dev_type(vendor, name):

    create_list = {"manufacturer": vendor,
                   "model": name,
                   "slug": name.lower(),
                   }

    info = net_box.dcim.device_types.create(create_list)

    return info


def device_name_init(map, site_name):

    result = []

    for init in map:

        dev = map[init]

        name = dev.get('Name')

        name_type = dev.get('Hint').split('\n')[0]

        type_id = net_box.dcim.device_types.get(model=name_type).id

        site = net_box.dcim.sites.get(name=site_name).id

        json_dev = {"name": name,
                    "device_type": type_id,
                    "device_role": 2,
                    "site": site,
                    }

        result.append([json_dev, {"primary_ip": dev.get('Address'),
                                  "addressess": dev.get('Addressess'),
                                  }])

    return result


def add_devices(json_names):

    create_devices = []

    for name in json_names:
        try:
            dev_id = net_box.dcim.devices.get(name=name[0]['name'])
            if not dev_id:
                created_dev = net_box.dcim.devices.create(name[0])
                created_dev.update(name[1])
                create_devices.append(created_dev)

        except pynetbox.core.query.RequestError as e:

            print(e.error)

    return create_devices


def setup_ip(create_devices):

    info = {}

    for device in create_devices:

        id_dev = device.id
        id_System = net_box.dcim.interfaces.get(q="System", device_id=id_dev).id
        ip_info = net_box.ipam.ip_addresses.create({"address": device.primary_ip,
                                                    "interface": id_System
                                                    })
        ip_info.update({'addressess': device.addressess})
        info.update({id_dev: ip_info})

    return info


def set_primary(info):

    info_dev = []

    for dev_id, ip_info in info.items():

        dev_data = net_box.dcim.devices.get(dev_id)

        dev_data.update({'primary_ip4': ip_info.id})
        # if not addressess in None:
        #     dev_data.update({})

        info_dev.append(net_box.dcim.devices.get(dev_id))

    return info_dev


def main():

    filtred_map = map_load()    # loaded item from map

    new_types = added_device_types(filtred_map)    # setup missing types

    if len(new_types) > 0:
        init_ports(new_types)

    namespace_map = device_name_init(filtred_map, 'Kabanovo')   # will return dictionary with basic info about devices

    info_ip = add_devices(namespace_map)   # add new devices from map
    if len(info_ip) > 0:
        primary_info = setup_ip(info_ip)
        info_added_device = set_primary(primary_info)
        return info_added_device

    return None


if __name__ == "__main__":
    print(main())
