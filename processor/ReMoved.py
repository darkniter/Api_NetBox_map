import re
from processor.utilities.transliteration import transliterate
from processor.utilities.slugify import slugify
import processor.config as config
from functools import partial


def main(parent, vlans_map, xl_names, filtred_map, connect):
    global net_box
    net_box = connect
    global xl_map
    xl_map = xl_names
    global map_scan
    map_scan = filtred_map
    global region
    region = config.REG_NAME[parent]
    mode = ['name', 'remove', 'name', ]


def get_names():
    for init in map_scan:

        dev = map_scan[init]

        ip_address = dev.get('address')

        site_arr = xl_map.get(ip_address)

        if (dev.get('description') and site_arr):
            site_arr[3].update({'hint': dev.get('description')})
            desc_tmp = site_arr[3]
            dev['description'] = desc_tmp

        if not site_arr:
            continue

        number_house = re.sub('[,/]', '_', dev.get('name').split()[-1].split('.')[0])
        site_name = (site_arr[0] + ' ' + number_house).strip()
        trans_name = site_arr[2]
        site_name = transliterate(site_name)
        site_info = net_box.dcim.sites.get(name=site_name.strip())

        if not site_info:
            site_info = net_box.dcim.sites.get(slug=slugify(site_name.strip()))

        region_info = net_box.dcim.regions.get(slug=region)

        names_regions = []
        region_tmp = region
        if not region_info:
            while region_tmp:

                name_this_region = net_box.dcim.regions.get(slug=region_tmp)
                names_regions.append(name_this_region.slug)
                region_tmp = name_this_region.parent
                if region_tmp:
                    region_tmp = region_tmp.slug
            names_regions = names_regions[-1]
        else:
            names_regions = region_info.slug

        name_prefix_tmp = dev.get('name').split('.')
        name_prefix_tmp.remove(name_prefix_tmp[0])
        name_prefix = '.'.join(name_prefix_tmp)

        name = '-'.join((names_regions, site_info.slug))
        if name_prefix:
            name = name + '.' + name_prefix

        removed = True

        if site_arr[3].get('P_REMOVED') == '1':
            dev_removed = net_box.dcim.devices.get(name="REMOVED " + name)
            if not dev_removed:
                removed = False
            elif not dev_removed.custom_fields('P_REMOVED'):
                removed = False
        else:
            dev_tmp = net_box.net_box.dcim.devices.get(name=name)
            if dev_tmp:
                if dev_tmp.custom_fields('P_REMOVED'):
                    removed = False

    if removed:
        renamed(name)

    return ''


def renamed(name):
    device = net_box.dcim.devices.get(name=name)
    device
    return''

if __name__ == "__main__":
    main()
