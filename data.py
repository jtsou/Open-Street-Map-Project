
# coding: utf-8

# # OPEN STREET MAP CASE STUDY PROJECT

# MAP AREA
# San Francisco, CA, USA
# 
# https://mapzen.com/data/metro-extracts/your-extracts/99d97e82a282
# I chose this area with regards to the recent events, I am proud of how California is at the frontier to right what is wrong. 
# Also, the idea of contributing to the community is pretty cool.


import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "san-francisco_california.osm" 
SF = "sanfran.osm.json"

k = 1 

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()




with open(SF, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


from collections import defaultdict

def count_tags(filename):
    
    counts = defaultdict(int)
    for line in ET.iterparse(filename):
        current = line[1].tag
        counts[current] += 1
    return counts


def test():

    tags = count_tags(SF)
    pprint.pprint(tags)

    

if __name__ == "__main__":
    test()


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        
        if lower.search(element.attrib['k']):
            keys['lower'] += 1
        elif lower_colon.search(element.attrib['k']):
            keys['lower_colon'] += 1 
        elif problemchars.search(element.attrib['k']):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1
        
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys



def test_data():
    keys = process_map(SF)
    pprint.pprint(keys)



if __name__ == "__main__":
    test_data()



def count_street(filename):
    streets = {}
    for event, elem in ET.iterparse(filename, events=('start', 'end')):
        if event == 'end':
            key = elem.attrib.get('k')
            if key == 'addr:street':
                street = elem.attrib.get('v')
                if street not in streets:
                    streets[street] = 1
                else:
                    streets[street] += 1
    return streets


postcodes = count_street(OSM_FILE)
sorted_by_occurrence = [(k, v) for (v, k) in sorted([(value, key) for (key, value) in postcodes.items()], reverse=True)]

print 'street values and occurrence in San-Francisco_california.osm:\n'
pprint.pprint(sorted_by_occurrence)


from collections import defaultdict
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons",'Terrace',"Plaza","Way","Center","Broadway","Post"]

mapping = { "St": "Street",
            "St.": "Street",
           'st':'Street',
            "Ave": "Avenue",
           'ave':"Avenue",
            "Rd.": "Road",
            "W.": "West",
            "N.": "North",
            "S.": "South",
            "E": "East",
           "Ln":'"Lane',
           'way':"Way"
          
          }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types

def update_name(name, mapping):
    after = []
    for part in name.split(" "):        
        if part in mapping.keys():
            part = mapping[part]
        after.append(part)
    return " ".join(after)
    
    return name
def map_test():
    st_types = audit(SF)
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            

if __name__ == '__main__':
    map_test()



def count_keys(filename):
    keys = {}
    for event, elem in ET.iterparse(filename, events=('start', 'end')):
        if event == 'end':
            key = elem.attrib.get('k')
            if key:
                if key not in keys:
                    keys[key] = 1
                else:
                    keys[key] += 1
    return keys

keys = count_keys(SF)
sorted_by_occurrence = [(k, v) for (v, k) in sorted([(value, key) for (key, value) in keys.items()], reverse=True)]

print 'Keys and occurrence in San-Francisco_california.osm:\n'
pprint.pprint(sorted_by_occurrence)



def count_postcodes(filename):
    postcodes = {}
    for event, elem in ET.iterparse(filename, events=('start', 'end')):
        if event == 'end':
            key = elem.attrib.get('k')
            if key == 'addr:postcode':
                postcode = elem.attrib.get('v')
                if postcode not in postcodes:
                    postcodes[postcode] = 1
                else:
                    postcodes[postcode] += 1
    return postcodes

postcodes = count_postcodes(OSM_FILE)
sorted_by_occurrence = [(k, v) for (v, k) in sorted([(value, key) for (key, value) in postcodes.items()], reverse=True)]

print 'Postcode values and occurrence in San-francisco_california.osm:\n'
pprint.pprint(sorted_by_occurrence)



def update_postcode(postcode):
    first_five = re.findall(r'\d{5}',postcode)
    if len(first_five) > 0 :  
        return first_five[0]  
    else: 
        return None


OSM_FILE = "san-francisco_california.osm" 
SF = "sanfran.osm.json"

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def is_address(elem):
    if elem.attrib['k'][:5] == "addr:":
        return True

def is_postcode(elem):
    if elem.attrib['k'] == 'addr:postcode':
        return True
        
        
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :

        address_info={}
        nd_info=[]
        node['type']=element.tag
        node['id']=element.attrib['id']
        if 'visible' in element.attrib.keys():
            node['visible']=element.attrib['visible']
        if 'lat' in element.attrib.keys():
            node['pos']=[float(element.attrib['lat']), float(element.attrib['lon'])]
        node['created']={'version':element.attrib['version'],
                        'changeset':element.attrib['changeset'],
                        'timestamp':element.attrib['timestamp'],
                        'user':element.attrib['user'],
                        'uid':element.attrib['uid']}
        
        
        for tag in element.iter('tag'):
            p = problemchars.search(tag.attrib['k'])
            
            if p:
                continue
            elif is_address(tag): 
                if ':' in tag.attrib['k'][5:]:
                    continue
                else: 
                    after_colon = tag.attrib['k'][5:]
                    if tag.attrib['k'] == "addr:postcode":
                        newpostcode = update_postcode(tag.attrib['v'])
                        address_info[tag.attrib['k']]=newpostcode

                    else :
                        address_info[tag.attrib['k'][5:]]=update_name(tag.attrib['v'], mapping)
            
            
            else:
                node[tag.attrib['k']] = tag.attrib['v']
        if address_info != {}:
            node['address'] = address_info
        for tag2 in element.iter('nd'):
            nd_info.append(tag2.attrib['ref'])
        
        if nd_info != []:
            node['node_refs'] = nd_info
        return node
    else:
        return None


def process_map(file_in, pretty = False):

    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    data = process_map(SF, True)
    pprint.pprint(data)
    
    

if __name__ == "__main__":
    test()




