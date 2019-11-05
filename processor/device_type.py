import processor.config as config
import pynetbox
from processor.utilities.slugify import slugify

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def add_device_types(option='Switch', map_dev=None,):
    new_dev = []
    namespace_dev = []
    if option == 'Switch':
        for row in map_dev:
            namespace_dev.append(map_dev[row].get('description').split('\n')[0].split(' ')[0])
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

    map_dev = set(map_dev)

    for dev_name in map_dev:
        if option != 'dev':
            dev_name = 'T1-' + dev_name
        net = net_box.dcim.device_types.get(slug=slugify(dev_name))

        for vendor in config.DEVICE_TYPES:

            if dev_name in config.DEVICE_TYPES[vendor]:
                try:
                    manufacturer = net_box.dcim.manufacturers.get(name=vendor).id
                except BaseException:
                    print('не найден вендор в системе NetBox ', vendor)
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
                   "tags": ["test-0919", ],
                   "is_full_depth": 0,
                   }

    info = net_box.dcim.device_types.create(create_list)

    return info
