import config
import pynetbox

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def device_name_init(map, site_name):

    result = []

    for init in map:

        dev = map[init]

        name = site_name + '_' + dev.get('Name')

        name_type = dev.get('Hint').split('\n')[0].split(' ')[0]

        type_id = net_box.dcim.device_types.get(model=name_type).id

        site = net_box.dcim.sites.get(name=site_name).id

        json_dev = {"name": name,
                    "device_type": type_id,
                    "device_role": 2,
                    "site": site,
                    }

        result.append([json_dev, {"primary_ip": dev.get('Address'),
                                  "addresses": dev.get('Addresses'),
                                  }])

    return result


def add_devices(json_names):

    create_devices = []

    for name in json_names:
        try:
            dev_id = net_box.dcim.devices.get(name=name[0]['name'])
            if not dev_id:
                created_dev = net_box.dcim.devices.create(name[0])
                created_dev.update(name[1])
                create_devices.append(created_dev)

        except pynetbox.core.query.RequestError as e:

            print(e.error)

    return create_devices
