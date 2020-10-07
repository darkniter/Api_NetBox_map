import processor.config as config
import pynetbox
from processor.utilities.slugify import slugify
net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN, threading=True)


def add_regions(name, parent=None, slug=None):
    name = name.strip()
    if parent:
        parent = parent.strip()
        parent_id = net_box.dcim.regions.get(name=parent).id

    slug = slug or slugify(name)

    if not net_box.dcim.regions.get(name=name):
        if parent and parent_id:

            region_info = net_box.dcim.regions.create({"name": name,
                                                       "slug": slug,
                                                       "parent": parent_id,
                                                       })
        else:
            region_info = net_box.dcim.regions.create({"name": name,
                                                       "slug": slug,
                                                       })
        print("add_regions:", region_info)
        return region_info
