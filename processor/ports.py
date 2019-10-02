from processor.utilities.split_pattern import search_pattern
import processor.config as config
import pynetbox

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def init_ports(new_dev):

    for init in new_dev:
        id_dev = init.id
        if config.DEVICE_TYPES[init.manufacturer.name].get(init.model):
            result_ports_list = config.DEVICE_TYPES[init.manufacturer.name].get(init.model)
            if result_ports_list.get('interfaces'):
                interfaces_list = ports_list(result_ports_list.get('interfaces'))
            else:
                print('Не задана карта портов для :', init.model)
                continue

            add_dev_temp(id_dev, interfaces_list)

            if result_ports_list.get('consoles'):
                console_ports(id_dev, result_ports_list.get('consoles'))

    return None


def ports_list(initiation_list):

    result = []

    for ports_group in initiation_list:

        init_group = search_pattern(ports_group['name'])

        for record in init_group:
            result.append({
                           "name": record,
                           "type": ports_group.get('type_port'),
                           "mgmt_only": ports_group.get('mgmt')
                           })

    return result


def console_ports(id_dev, ports_names):
    for console_ports in ports_names:
        init_console_ports_name = search_pattern(console_ports)
        for port in init_console_ports_name:
            net_box.dcim.console_port_templates.create({
                                                        "device_type": id_dev,
                                                        "name": port,
                                                        })


def add_dev_temp(device_type_id, names):

    for name in names:
        if name.get("mgmt_only"):
            result = net_box.dcim.interface_templates.create({
                                                                "device_type": device_type_id,
                                                                "name": name["name"],
                                                                "type": name["type"],
                                                                "mgmt_only": name["mgmt_only"]
                                                                })
        else:
            result = net_box.dcim.interface_templates.create({
                                                                "device_type": device_type_id,
                                                                "name": name["name"],
                                                                "type": name["type"],
                                                                })
    return result
