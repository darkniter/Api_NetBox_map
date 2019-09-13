import config
import pynetbox
from processor.utilities.slugify import slugify

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def add_device_types(map_dev):

    new_dev = []
    for row in map_dev:
        dev_name = map_dev[row].get('Hint').split('\n')[0].split(' ')[0]
        net = net_box.dcim.device_types.get(model=dev_name)

        if net is None:
            new_dev.append(add_device_type(2, dev_name))

    return new_dev


def add_device_type(vendor, name):

    create_list = {"manufacturer": vendor,
                   "model": name,
                   "slug": slugify(name),
                   }

    info = net_box.dcim.device_types.create(create_list)

    return info
