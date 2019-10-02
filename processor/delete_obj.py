import config
import pynetbox
import finder
from utilities.slugify import slugify
from utilities.transliteration import transliterate as revers
net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def delete_object(**kwarg):

    def_name = kwarg.get('name')

    objects_list = kwarg.get('list')

    def delete_sites(sites_list, func_mod=None):

        if func_mod == 'child':
            sites_names = []
            for site_name in sites_list:
                sites_names.append(site_name)
            sites_list = sites_names

        for site in sites_list:
            try:
                site = slugify(site)
                site_info = net_box.dcim.sites.get(slug=site)
            except pynetbox.core.query.RequestError as e:
                print(e.error)

            if site_info:
                site_id = site_info.id

                device_list = finder.find_child_devices(site, 'site')

                delete_devices(device_list)

                print("Site:", site, "site_id:", site_id, "delete:", site_info.delete())

    def delete_device_types(type_list):
        for dev_type in type_list:
            try:
                dev_type = slugify(dev_type)
                if not(dev_type == '') and net_box.dcim.device_types.get(slug=dev_type):

                    dev_type_info = net_box.dcim.device_types.get(slug=dev_type)
                    dev_type_id = dev_type_info.id

                    device_list = finder.find_child_devices(dev_type, 'dev_type')

                    delete_devices(device_list)
                    print("Type:", dev_type, "type_id:", dev_type_id, "delete:", dev_type_info.delete())
            except pynetbox.core.query.RequestError as e:
                print(e.error)

    def delete_devices(device_list):
        for device_unit in device_list:
            print("Device:", device_unit.display_name, "device_id:", device_unit.id, "delete:", device_unit.delete())

    def delete_regions(regions_list, func_mod=None):

        if func_mod == 'child':
            regions_names = []
            for region_name in regions_list:
                regions_names.append(region_name.name)
            regions_list = regions_names

        for region in regions_list:
            if net_box.dcim.regions.get(slug=region):
                region_info = net_box.dcim.regions.get(slug=region)
            else:
                region_info = net_box.dcim.regions.get(name=region)
                if not region_info:
                    region_info = net_box.dcim.regions.get(name=revers(region))

            if region_info:
                child_regions = finder.find_child_regions(region_info.id)

                if len(child_regions) > 0:
                    delete_regions(child_regions, 'child')

                child_sites = finder.find_child_sites(region_info.id)

                if len(child_sites) > 0:
                    delete_sites(child_sites, 'child')

                print("Region:", region_info.name, "region-id:", region_info.id, "delete:", region_info.delete())

    if def_name and objects_list:
        if def_name == 'sites':
            return delete_sites(objects_list)

        elif def_name == 'device_types':
            return delete_device_types(objects_list)

        elif def_name == 'devices':
            return delete_devices(objects_list)

        elif def_name == 'regions':
            return delete_regions(objects_list)

        else:
            print('The function is called incorrectly')
    else:
        print('The function is called without the required arguments')


if __name__ == "__main__":
    pass
    # list_dev = []
    # for vendor in config.DEVICE_TYPES:
    #     for model in config.DEVICE_TYPES[vendor]:
    #         list_dev.append(model)
    # list_regions = ['kb',]
    # delete_object(**{'name': 'regions', 'list': list_regions})
    # if os.path.isfile(config.VLAN_PATH_XL):
    #     os.remove(config.VLAN_PATH_XL)
