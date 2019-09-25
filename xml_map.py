from lxml import etree
import os
import processor.config
import Switches


def main(map_loc):
    with open(map_loc, 'r', encoding='utf-8-sig') as xml_map_reader:
        xml_map = xml_map_reader.read()
        xml_map = etree.fromstringlist(xml_map)
    xml_map = filtration(xml_map)

    return xml_map

def filtration(xml_map):
    for name in xml_map:
        for dev in name:
            print(dev)
    return xml_map

if __name__ == "__main__":
    map_filter=main(processor.config.XMLMAP)
    # Switches.result()