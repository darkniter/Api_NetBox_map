import config
import pynetbox

net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def add_sites(site_list):

    sites_info = []

    for site in site_list:

        sites_info.append(net_box.site.create({}))

    return sites_info
