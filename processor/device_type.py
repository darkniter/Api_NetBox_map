import config
import pynetbox

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def added_device_types(map_dev):

    new_dev = []
    for row in map_dev:
        dev_name = map_dev[row].get('Hint').split('\n')[0].split(' ')[0]
        net = net_box.dcim.device_types.get(model=dev_name)
        if net is None:
            new_dev.append(add_dev_type(2, dev_name))
    return new_dev


def add_dev_type(vendor, name):

    create_list = {"manufacturer": vendor,
                   "model": name,
                   "slug": name.lower(),
                   }

    info = net_box.dcim.device_types.create(create_list)

    return info
