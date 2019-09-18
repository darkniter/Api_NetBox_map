import config
import pynetbox
from processor.utilities.slugify import slugify
net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def find_site_child(name):
    try:
        name = slugify(name)
        device_list = net_box.dcim.devices.filter(site=name)
        return device_list
    except pynetbox.core.query.RequestError as e:
        print(e.error)


def find_type_child(name):
    try:
        name = slugify(name)
        device_list = net_box.dcim.devices.filter(model=name)
        return device_list
    except pynetbox.core.query.RequestError as e:
        print(e.error)
