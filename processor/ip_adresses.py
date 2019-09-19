import processor.config as config
import pynetbox

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def setup_ip(create_devices):

    info = {}

    for device in create_devices:

        id_dev = device.id
        id_System = net_box.dcim.interfaces.get(q="System", device_id=id_dev).id
        ip_info = net_box.ipam.ip_addresses.create({"address": device.primary_ip,
                                                    "interface": id_System,
                                                    "tags": ["test-0919", ],
                                                    })
        if device.addresses is not None:
            for deprecation_dev in device.addresses:
                net_box.ipam.ip_addresses.create({"address": deprecation_dev,
                                                  "interface": id_System,
                                                  "status": 3,
                                                  "tags": ["test-0919", ],
                                                  })
        ip_info.update({'addresses': device.addresses})
        info.update({id_dev: ip_info})

    info_dev = set_primary(info)

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
