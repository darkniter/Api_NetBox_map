import config
import pynetbox
import finder
from utilities.slugify import slugify
net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def delete_object(**kwarg):

    def_name = kwarg.get('name')

    objects_list = kwarg.get('list')

    def delete_sites(site_list):
        for site in site_list:
            try:
                site = slugify(site)
                site_info = net_box.dcim.sites.get(slug=site)
            except pynetbox.core.query.RequestError as e:
                print(e.error)

            if site_info:
                site_id = site_info.id

                device_list = finder.find_site_child(site)

                delete_devices(device_list)

                print("Site:", site, "site_id:", site_id, "delete:", site_info.delete())

    def delete_device_types(type_list):
        for dev_type in type_list:
            try:
                dev_type = slugify(dev_type)
                if not(dev_type == '') and net_box.dcim.device_types.get(slug=dev_type):

                    dev_type_info = net_box.dcim.device_types.get(slug=dev_type)
                    dev_type_id = dev_type_info.id

                    device_list = finder.find_type_child(dev_type)

                    delete_devices(device_list)
                    print("Type:", dev_type, "type_id:", dev_type_id, "delete:", dev_type_info.delete())
            except pynetbox.core.query.RequestError as e:
                print(e.error)

    def delete_devices(device_list):
        for device_unit in device_list:
            print("Device:", device_unit.display_name, "device_id:", device_unit.id, "delete:", device_unit.delete())

    if def_name and objects_list:
        if def_name == 'sites':
            return delete_sites(objects_list)

        elif def_name == 'device_types':
            return delete_device_types(objects_list)

        elif def_name == 'devices':
            return delete_devices(objects_list)

        else:
            print('The function is called incorrectly')
    else:
        print('The function is called without the required arguments')


if __name__ == "__main__":
    list_dev = []
    for vendor in config.DEVICE_TYPES:
        for model in config.DEVICE_TYPES[vendor]:
            list_dev.append(model)
    delete_object(**{'name': 'device_types', 'list': list_dev})

    # if os.path.isfile(config.VLAN_PATH_XL):
    #     os.remove(config.VLAN_PATH_XL)
