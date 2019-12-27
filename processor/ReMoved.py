from functools import partial


def main(vlans_map, xl_map, filtred_map, connect):
    global net_box
    net_box = connect

    rename_list = partial(device_find, xl_map)
    list(map(rename_list,))
    return''

def device_find():

    return ''
if __name__ == "__main__":
    main()
