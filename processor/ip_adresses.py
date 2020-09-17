import processor.config as config
import pynetbox

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN, threading=True)


def setup_ip(create_devices):
    info_dev = []
    for device in create_devices:
        info = {}
        id_dev = device.id
        vendor = device.device_type.manufacturer.name
        if device.device_type.model in config.DEVICE_TYPES.get(vendor):
            id_System = net_box.dcim.interfaces.get(
                q=config.DEVICE_TYPES[vendor][device.device_type.model]['interfaces'][-1].get('name'),
                device_id=id_dev
                ).id

            ip_info = net_box.ipam.ip_addresses.create({
                                                        "address": device.primary_ip,
                                                        "assigned_object_type": "dcim.interface",
                                                        "assigned_object_id": id_System,
                                                        "tags": config.TAGS,
                                                        })
            if device.addresses is not None:
                for deprecation_dev in device.addresses:
                    net_box.ipam.ip_addresses.create({
                                                        "address": deprecation_dev,
                                                        "interface": id_System,
                                                        "status": 3,
                                                        "tags": config.TAGS,
                                                    })
            ip_info.update({'addresses': device.addresses})
            info.update({id_dev: ip_info})

            info_dev.append(set_primary(info))

    return info_dev


def set_primary(info):

    info_dev_with_primapy = []

    for dev_id, ip_info in info.items():

        dev_data = net_box.dcim.devices.get(dev_id)

        dev_data.update({'primary_ip4': ip_info.id})
        # if not addresses in None:
        #     dev_data.update({})

        info_dev_with_primapy.append(net_box.dcim.devices.get(dev_id))

    return info_dev_with_primapy
