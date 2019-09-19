from processor.utilities.split_pattern import search_pattern
import processor.config as config
import pynetbox

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def init_ports(new_dev):

    for init in new_dev:
        id_dev = init.id
        if config.DEVICE_TYPES.get(init.model):
            result_ports_list = ports_list(config.DEVICE_TYPES.get(init.model))
        else:
            print('Не задана карта портов для :', init.model)
            continue

        add_dev_temp(id_dev, result_ports_list)

    return None


def ports_list(initiation_list):

    result = []

    for ports_group in initiation_list:

        init_group = search_pattern(ports_group['name'])

        for record in init_group:
            result.append({"name": record,
                           "type": ports_group.get('type_port'),
                           "mgmt_only": ports_group.get('mgmt')})

    return result


def add_dev_temp(device_type_id, names):

    for name in names:

        result = net_box.dcim.interface_templates.create({"device_type": device_type_id,
                                                          "name": name["name"],
                                                          "type": name["type"],
                                                          "mgmt_only": name["mgmt_only"]})

    return result
