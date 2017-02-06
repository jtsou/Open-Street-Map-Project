
# coding: utf-8

# # OPEN STREET MAP CASE STUDY PROJECT

# MAP AREA
# San Francisco, CA, USA
# 
# https://mapzen.com/data/metro-extracts/your-extracts/99d97e82a282
# I chose this area with regards to the recent events, I am proud of how California is at the frontier to right what is wrong. 
# Also, the idea of contributing to the community is pretty cool.

# In[1]:

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


# In[2]:

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "san-francisco_california.osm" 
SF = "sanfran.osm.json"

k = 10 

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
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


# In[3]:

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


# In[4]:

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
    # You can use another testfile 'map.osm' to look at your solution
    # Note that the assertions will be incorrect then.
    keys = process_map(SF)
    pprint.pprint(keys)



if __name__ == "__main__":
    test_data()


# In[5]:

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


# In[6]:

from collections import defaultdict
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons",'Terrace',"Plaza","Way","Center","Broadway","Post"]
# UPDATE THIS VARIABLE
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
    # Split name string to test each part of the name;
    # Replacements may come anywhere in the name.
    for part in name.split(" "):
        # Check each part of the name against the keys in the correction dict
        if part in mapping.keys():
            # If exists in dict, overwrite that part of the name with the dict value for it.
            part = mapping[part]
        # Assemble each corrected piece of the name back together.
        after.append(part)
    # Return all pieces of the name as a string joined by a space.
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


# In[7]:

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


# In[ ]:

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


# In[ ]:

def update_postcode(postcode):
    if re.match(r'$\d{5}^', postcode):
        return postcode
    try:
        return re.findall(r'^(\d{5})-\d{4}$', postcode)[0]
    except:
        pass


# In[ ]:

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

OSM_FILE = "san-francisco_california.osm" 
SF = "sanfran.osm.json"

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def is_address(elem):
    if elem.attrib['k'][:5] == "addr:":
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
            if tag.attrib['k']=='addr:street':
                update_name(tag.attrib['v'],mapping)
            if tag.attrib['k']=='addr:postcode':
                update_postcode(tag.attrib['v'])
            if p:
                continue
            elif is_address(tag):
                if ':' in tag.attrib['k'][5:]:
                    continue
                else:
                    address_info[tag.attrib['k'][5:]]=tag.attrib['v']
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


# In[ ]:



