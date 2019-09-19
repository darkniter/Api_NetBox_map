import config
import pynetbox
from utilities.slugify import slugify
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


def find_tag_group(tag):

    tag_object_list = {'prefix': [], 'vlans': [], 'device': []}

    for prefix in net_box.ipam.prefixes.filter(tag=tag):
        tag_object_list['prefix'].append(prefix)
    for vlans in net_box.ipam.vlans.filter(tag=tag):
        tag_object_list['vlans'].append(vlans)
    for device in net_box.dcim.devices.filter(tag=tag):
        tag_object_list['device'].append(device)

    return tag_object_list



