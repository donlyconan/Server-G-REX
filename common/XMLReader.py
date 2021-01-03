import xml.etree.cElementTree as xml
from collections import namedtuple






def convertR(pathXml="config.xml"):
    tree = xml.ElementTree(file=pathXml)
    dict = {}
    for x in tree.getroot():
        dict[x.get("name")] = int(x.text)

    return namedtuple("R", dict.keys())(**dict), dict


R, _ = convertR()
print(R.INT)