import config
import pynetbox
from regions import add_regions as create_reg
# import map_devices
from utilities.slugify import slugify
import map_devices
net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def add_VLAN_G(name, slug=None):
    if not slug:
        slug = slugify(name)

    VLAN_G = net_box.ipam.vlan_groups.create({'name': name, 'slug': slug})

    return VLAN_G


def add_VLANs(regions):

    for region in regions:
        for vlan_groups in regions[region]:
            slug_group = slugify(vlan_groups[1])
            group = net_box.ipam.vlan_groups.get(slug=slug_group)

            if not group:
                group = add_VLAN_G(vlan_groups[1])

            vlans_list = add_vlans_list(group, vlan_groups)
            VLANs = net_box.ipam.vlans.create(vlans_list)

            add_prefixes(VLANs, vlan_groups)
        print(VLANs)

    return VLANs


def add_vlans_list(group, vlan_group):
    vlans_list = []
    init_vlans = []

    for i in [3, 4, 5, 6, 7]:
        init_vlans.append(vlan_group[i])

    for vlans in init_vlans:
        options = vlans.split('-')
        role = net_box.ipam.roles.get(slug=options[1])
        vlans_list.append({
                            "group": group.id,
                            "vid": options[2],
                            "name": '-'.join([options[0], options[1], options[2]]),
                            "status": 1,
                            "role": role.id,
                            "tags": ["test-0919"],
                            })
    return vlans_list


def add_prefixes(vlans, vlan_group):

    init_vlans = []
    result_pref = []
    for i in [3, 5, 6, 7]:
        init_vlans.append(vlan_group[i])

    for prefix in vlans:
        for vlan in init_vlans:
            if not (vlan.find(prefix.name) == -1):
                options = vlan.split('-')
                result_pref.append(net_box.ipam.prefixes.create({
                                                "prefix": options[-1],
                                                "vlan": prefix.id,
                                                "status": 1,
                                                "role": net_box.ipam.roles.get(slug=options[1]).id,
                                                "is_pool": 1,
                                                "tags": ["test-0919"],
                                                }))
    return result_pref


def region_add_from_vlan(regions):
    add_regions = []
    for region in regions:
        for site_in_region in regions[region]:
            if not(net_box.dcim.regions.get(name=regions[region])):
                add_regions.append(create_reg(region))
            if not(net_box.dcim.regions.get(name=site_in_region[1])):
                add_regions.append(create_reg(site_in_region[1], region))
    return add_regions


if __name__ == "__main__":
    region = map_devices.VLAN_map('Куровское')
    region_add_from_vlan(region)
    add_VLANs(region)
