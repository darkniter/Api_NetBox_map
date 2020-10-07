import processor.config as config
import pynetbox
import processor.sites as sites
import re
from processor.utilities.slugify import slugify
from processor.utilities.transliteration import transliterate
from functools import lru_cache

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN, threading=True)
prefixes = {'d.': 'd', 'proezd.': 'pr', 'b-r.': 'br', 'ul.': 'ul', 'sh.': 'sh'}


def device_name_SWITCH(map_dev, xl_map, region):

    device_role = net_box.dcim.device_roles.get(name='Switch').id

    ip_mask = '/' + region[3].split('/')[-1]

    region = region[1].strip()

    result = []

    region = slugify(region)

    for init in map_dev:

        dev = map_dev[init]

        ip_address = dev.get('address')

        if net_box.ipam.ip_addresses.get(address=ip_address):
            continue

        site_arr = xl_map.get(ip_address)

        if (dev.get('description') and site_arr):
            site_arr[3].update({'hint': dev.get('description')})
            desc_tmp = site_arr[3]
            dev['description'] = desc_tmp

        if not site_arr:
            continue

        site_arr[3]['P_RESERVED3'] = str(site_arr[2]) + '_' + str(site_arr[1])

        number_house = transliterate(re.sub('[,/]', '_', site_arr[1].split()[-1].split('.')[0]))
        site_name = (site_arr[0] + ' ' + number_house).strip()
        trans_name = site_arr[2]
        try:
            prefix = re.match(r'^[\w-]+\.', site_name).group(0)
            if prefix in prefixes:
                site_name = re.sub(r'^[\w-]+\.', prefixes[prefix], site_name)
        except BaseException as ex:
            print(ex)

        site_info = net_box.dcim.sites.get(name=site_name.strip())

        if not site_info:
            site_info = net_box.dcim.sites.get(slug=slugify(site_name.strip()))
        region_info = net_box.dcim.regions.get(slug=region)

        if not region_info:
            raise ValueError(f"No region_info for {map_dev[init]}")

        if site_info:
            site = site_info
        else:
            site = sites.add_site(trans_name + ' ' + number_house, site_name, region)
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

        name_prefix_tmp = site_arr[1].split('.')
        name_prefix_tmp.remove(name_prefix_tmp[0])
        name_prefix = transliterate('.'.join(name_prefix_tmp))

        name = '-'.join((names_regions, site.slug))
        if name_prefix:
            name = name + '.' + name_prefix

        if site_arr[3].get('P_REMOVED') == '1':
            removed = net_box.dcim.devices.get(name="REMOVED " + name)
            name = "REMOVED " + name
        else:
            removed = None

        name_type_tmp = dev.get('description')['hint'].split('\n')[0]
        name_type = re.sub(r'^\[font .*\]', '', name_type_tmp).split(' ')[0]
        type_dev = net_box.dcim.device_types.get(model='' + name_type)

        if type_dev:
            if not removed:
                type_id = type_dev.id
                description = dev.get('description')
                if description['P_REMOVED'] == '1':
                    description['P_REMOVED'] = True
                elif description['P_REMOVED'] == '0':
                    description['P_REMOVED'] = False
                if description['P_TRANSIT'] == '1':
                    description['P_TRANSIT'] = True
                elif description['P_TRANSIT'] == '0':
                    description['P_TRANSIT'] = False
                json_dev = {"name": name,
                            "device_type": type_id,
                            "device_role": device_role,
                            "site": site_id,
                            "tags": config.TAGS,
                            "comments": description.pop('hint'),
                            "custom_fields": description
                            }

                result.append([json_dev, {
                                            "primary_ip": ip_address + ip_mask,
                                            "addresses": dev.get('addresses'),
                                            }])
            else:
                print('Dev has removed but in netbox')
        else:
            print('Не установлен Тип в config для данного устройства:', name_type, name, ip_address)

    create_dev = add_devices(result)

    return create_dev


def device_name_MODEM(init_map, region):

    result = []
    device_role = net_box.dcim.device_roles.get(name='SIP').id
    site_id = net_box.dcim.sites.get(name='MODEM_SITE').id
    ip_mask = '/' + net_box.ipam.prefixes.get(site_id=site_id, role='sip').prefix.split('/')[-1]

    for ip, dev in init_map.items():

        type_id = data_dev_hook(dev['model'])

        json_dev = {"name": dev['id'],
                    "device_type": type_id,
                    "device_role": device_role,
                    "site": site_id,
                    "tags": config.TAGS,
                    "comments": dev['description'],
                    }

        result.append([json_dev, {
                                "primary_ip": ip + ip_mask,
                                "addresses": dev.get('addresses'),
                                }])

    create_dev = add_devices(result)
    return create_dev


@lru_cache(maxsize=40)
def data_dev_hook(model):

    slug_model = slugify('' + model)
    type_id = net_box.dcim.device_types.get(slug=slug_model).id

    return type_id


def add_devices(json_names):

    create_devices = []

    for name in json_names:
        name_double = name[0]['name']
        try:
            dev_id = net_box.dcim.devices.get(name=name[0]['name'])
            if dev_id:
                name_default = dev_id.name
                count = 0
                while dev_id:
                    count += 1
                    name_double = name_default + '_' + str(count)
                    dev_id = net_box.dcim.devices.get(name=name_double)

            if not dev_id:
                name[0]['name'] = name_double
                created_dev = net_box.dcim.devices.create(name[0])
                created_dev.update(name[1])
                create_devices.append(created_dev)

        except pynetbox.core.query.RequestError as e:

            print(e.error)

    return create_devices


if __name__ == "__main__":
    pass
