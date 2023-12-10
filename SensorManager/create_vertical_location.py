from json_utilities import read_JSON,write_JSON,FOLDER_PATH,print_JSON

def get_verticals():
    verticals_JSON = read_JSON(FOLDER_PATH,'verticals.json')
    verticals = []
    for vertical in verticals_JSON:
         verticals.append(vertical)
    return verticals

nodes = read_JSON(FOLDER_PATH,'nodes.json')
verticals = get_verticals()

vertical_location = {}
vertical_idx=0
for vertical in verticals:
    vertical_location[vertical]=[]

for node in nodes:
    if node.startswith(verticals[vertical_idx]):
        vertical_location[verticals[vertical_idx]].append(node.replace(verticals[vertical_idx]+"-","") )
    else:
        vertical_idx=vertical_idx+1
        vertical_location[verticals[vertical_idx]].append(node.replace(verticals[vertical_idx]+"-","") )

write_JSON(FOLDER_PATH,'vertical_location.json',vertical_location)
# print_JSON(vertical_location)
     