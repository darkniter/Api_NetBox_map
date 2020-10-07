import processor.config as config
import pynetbox
from processor.utilities.slugify import slugify
net_box = pynetbox.api(config.NETBOX_URL, config.TOKEN, threading=True)


def add_site(trans_name, name, region):
    backup_region = None
    region_id = None

    backup_region = net_box.dcim.regions.get(slug=region)
    if backup_region:
        region_id = backup_region.id
    elif not backup_region:
        raise ValueError(f"No region_info for {trans_name}")

    slug = slugify(name)

    site_info = net_box.dcim.sites.create({
        "name": name,
        "slug": slug,
        "region": region_id,
        "tags": config.TAGS,
        "description": trans_name,
     })

    print("add_site:", site_info)
    return site_info
