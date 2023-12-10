from json_utilities import *

def get_verticals():
    verticals_JSON = read_JSON(FOLDER_PATH,'verticals.json')
    verticals = []
    for vertical in verticals_JSON:
         verticals.append(vertical)
    return verticals


verticals = get_verticals()
nodes = read_JSON(FOLDER_PATH,'nodes.json')

vertical_idx=0
location_set=set()
for node in nodes:
    if node.startswith(verticals[vertical_idx]):
          loc = node.replace(verticals[vertical_idx]+"-","")
          location_set.add(loc)
    else:
        vertical_idx = vertical_idx+1
        loc = node.replace(verticals[vertical_idx]+"-","")
        location_set.add(loc)

locations = list(location_set)
locations = sorted(locations)
write_JSON(FOLDER_PATH,'locations.json',locations)
# print(locations)
