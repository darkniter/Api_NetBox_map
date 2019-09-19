import processor.config as config
import pynetbox
import processor.sites as sites
import processor.regions as regions
import processor.map_devices as map_devices
from processor.utilities.slugify import slugify

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)
parent_region_test = 'Magic_Placement'


def device_name_init(map_dev, xl_map, region):

    result = []
    region = slugify(region)

    for init in map_dev:

        dev = map_dev[init]

        ip_address = dev.get('Address')

        site_arr = xl_map[0].get(ip_address)

        if not site_arr:
            continue

        site_name = site_arr[0] + '-' + site_arr[1].split('.')[0]

        site_info = net_box.dcim.sites.get(name=site_name)
        region_info = net_box.dcim.regions.get(slug=region)

        if not region_info:
            region = regions.add_regions(region, parent_region_test).slug

        if site_info:
            site = site_info
            site_id = site.id
        else:
            site = sites.add_site(site_name, region)
            site_id = site.id

        names_regions = []
        region_tmp = region

        while region_tmp:

            name_this_region = net_box.dcim.regions.get(slug=region_tmp)
            names_regions.append(name_this_region.slug)
            region_tmp = name_this_region.parent
            if region_tmp:
                region_tmp = region_tmp.slug

        names_regions = names_regions[-1]

        name_prefix_tmp = dev.get('Name').split('.')
        name_prefix_tmp.remove(name_prefix_tmp[0])
        name_prefix = '.'.join(name_prefix_tmp)

        name = '-'.join((names_regions, site.slug))
        if name_prefix:
            name = name + '.' + name_prefix

        name_type = dev.get('Hint').split('\n')[0].split(' ')[0]

        type_dev = net_box.dcim.device_types.get(model=name_type)
        if type_dev:
            type_id = type_dev.id
            json_dev = {"name": name,
                        "device_type": type_id,
                        "device_role": 2,
                        "site": site_id,
                        "tags": ["test-0919", ],
                        }

            result.append([json_dev, {"primary_ip": ip_address,
                                      "addresses": dev.get('Addresses'),
                                      }])
        else:
            print('Не установлен Тип в config для данного устройства:', name_type, name, ip_address)

    create_devices = add_devices(result)

    return create_devices


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


if __name__ == "__main__":
    loading_map = map_devices.map_load()
    xl_map = map_devices.excel_map()
    device_name_init(loading_map, xl_map, 'Test_add_reg')
