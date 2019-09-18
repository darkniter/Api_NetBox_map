import config
import pynetbox
from utilities.slugify import slugify
net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN)


def add_regions(name, parent=None):

    slug = slugify(name)
    parent_id = net_box.dcim.regions.get(name=parent).id
    if not net_box.dcim.regions.get(name=name):
        if parent and parent_id:
            region_info = net_box.dcim.regions.create({"name": name,
                                                       "slug": slug,
                                                       "parent": parent_id
                                                       })
        else:
            region_info = net_box.dcim.regions.create({"name": name,
                                                       "slug": slug
                                                       })
        print(region_info)
        return region_info
