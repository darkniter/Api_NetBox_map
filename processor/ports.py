from processor.utilities.split_pattern import search_pattern
import processor.config as config
import pynetbox

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def init_ports(new_dev):

    for init in new_dev:
        id_dev = init.id
        if config.DEVICE_TYPES.get(init.model):
            result_ports_list = ports_list(config.DEVICE_TYPES.get(init.model)[0])
        else:
            print('Не задана карта портов для :', init.model)
            continue

        add_dev_temp(id_dev, result_ports_list)

        if config.DEVICE_TYPES.get(init.model) and len(config.DEVICE_TYPES.get(init.model)) == 2:
            console_ports(id_dev, config.DEVICE_TYPES.get(init.model)[1])

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
    init_console_ports_name = search_pattern(ports_names)
    for port in init_console_ports_name:
        net_box.dcim.console_port_templates.create({
                                            "device_type": id_dev,
                                            "name": port,
                                            })
    return


def add_dev_temp(device_type_id, names):

    for name in names:

        result = net_box.dcim.interface_templates.create({"device_type": device_type_id,
                                                          "name": name["name"],
                                                          "type": name["type"],
                                                          "mgmt_only": name["mgmt_only"]})

    return result
