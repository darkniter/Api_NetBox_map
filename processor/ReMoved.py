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
    # ,'name','remove','name'
    return list(map(switch, mode))


def switch(mode):

    device_find_tmp = partial(device_find, mode)
    renamed = list(map(device_find_tmp, map_scan))

    print()
    return renamed


def device_find(mode, number_site):
    dev = map_scan.get(number_site)
    ip_address = dev.get('address')
    site_arr = xl_map.get(ip_address)

    number_house = re.sub('[,/]', '_', dev.get('name').split()[-1].split('.')[0])
    if site_arr:
        site_name = (site_arr[0] + ' ' + number_house).strip()
    else:
        print('Err xl', dev.get('name'))
        return 'ERROR'

    site_name = transliterate(site_name)
    site_info = net_box.dcim.sites.get(name=site_name.strip())

    if not site_info:
        site_info = net_box.dcim.sites.get(slug=slugify(site_name.strip()))

    # region_info = net_box.dcim.regions.get(slug=region)

    # if not region_info:
    #     print(region)

    if not site_info:
        return ('Error')

    names_regions = []
    region_tmp = region

    while region_tmp:
        name_this_region = net_box.dcim.regions.get(slug=region)
        names_regions.append(name_this_region.slug)
        region_tmp = name_this_region.parent
        if region_tmp:
            region_tmp = region_tmp.slug

    names_regions = names_regions[-1]

    name_prefix_tmp = dev.get('name').split('.')
    name_prefix_tmp.remove(name_prefix_tmp[0])
    name_prefix = '.'.join(name_prefix_tmp)

    name = '-'.join((names_regions, site_info.slug))
    if name_prefix:
        name = name + '.' + name_prefix

    if mode == 'name':
        return remove_name(name, site_arr[3].get('P_REMOVED'))
    if mode == 'remove' and site_arr[3].get('P_REMOVED') == '1':
        return remove_checkbox(name)


def remove_name(name, xl_dev_rm):
    dev_netbox = net_box.dcim.devices.get(name=name)
    if not dev_netbox:
        dev_netbox = net_box.dcim.devices.get(name="REMOVED " + name)
        if dev_netbox and (xl_dev_rm == '1' or dev_netbox.custom_fields.get('P_REMOVED')) :
            try:
                dev_netbox.update({"name": "REMOVED " + name})
                return "REMOVED : " + name
            except BaseException as err:

                return 'Failed ' + name + 'Err:' + str(err)
    else:
        return name


def remove_checkbox(name):
    dev_netbox = net_box.dcim.devices.get(name=name, custom_fields={'P_REMOVED': 0})
    if dev_netbox:
        try:
            dev_netbox.update({"custom_fields": {'P_REMOVED': 1}})
            return "CHANGED :" + name
        except BaseException as err:

            return 'Failed ' + name + 'Err:' + str(err)
    else:
        return name


if __name__ == "__main__":
    main()
