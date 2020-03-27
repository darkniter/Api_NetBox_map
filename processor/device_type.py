import processor.config as config
import pynetbox
from processor.utilities.slugify import slugify
import re

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN, threading=True)


def add_device_types(option='Switch', map_dev=None,):
    new_dev = []
    namespace_dev = []
    if option == 'Switch':
        for row in map_dev:
            description_map = map_dev[row].get('description')
            description_map = re.sub(r'^\[.*\]', '', description_map)
            namespace_dev.append(description_map.split('\n')[0].split(' ')[0])

        map_dev = namespace_dev

    if option == 'Modem':
        for row in map_dev:
            namespace_dev.append(map_dev[row].get('model'))
        map_dev = namespace_dev

    if option == 'dev':
        for vendor in config.DEVICE_TYPES:
            for dev_type in config.DEVICE_TYPES[vendor]:
                namespace_dev.append(dev_type)
        map_dev = namespace_dev

    map_dev_name = set(map_dev)

    for dev_name in map_dev_name:
        if option != 'dev':
            dev_name = dev_name
        net = net_box.dcim.device_types.get(slug=slugify(dev_name))

        for vendor in config.DEVICE_TYPES:

            if dev_name in config.DEVICE_TYPES[vendor]:
                try:
                    manufacturer = net_box.dcim.manufacturers.get(slug=slugify(vendor)).id
                except BaseException:
                    print('не найден вендор в системе NetBox:', vendor)
                    return new_dev

                configured_ports = config.DEVICE_TYPES[vendor].get(dev_name.upper())
                if configured_ports:
                    break
            else:
                manufacturer = None
                configured_ports = None

        if net is None and configured_ports:
            new_dev.append(formatted_device_type(manufacturer, dev_name))
        elif not configured_ports:
            print('нет конфигурации портов:', dev_name)

    return new_dev


def formatted_device_type(vendor, name):

    create_list = {"manufacturer": vendor,
                   "model": name,
                   "slug": slugify(name),
                   "tags": config.TAGS,
                   "is_full_depth": 0,
                   }

    info = net_box.dcim.device_types.create(create_list)

    return info
