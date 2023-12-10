from json_utilities import *

all_locations = read_JSON(FOLDER_PATH,'locations.json')
all_nodes = read_JSON(FOLDER_PATH,'nodes.json')

location_node={}
for location in all_locations:
    location_node[location]=[]
# print_JSON(location_node)
for location in all_locations:
    for node in all_nodes:
        if location in node:
            location_node[location].append(node)
                

write_JSON(FOLDER_PATH,'location_node.json',location_node)
# print_JSON(location_node)


