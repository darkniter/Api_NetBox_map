from split_pattern import search_pattern
import config
import pynetbox

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


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
