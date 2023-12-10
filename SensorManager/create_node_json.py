import requests
import json
from json_utilities import *

def get_all_nodes(node_result_dict):
    node_result_dict = node_result_dict['results']
    all_nodes = []
    for node in node_result_dict['Timestamp']:
        all_nodes.append(node)
    return all_nodes

PARAMETERS_API="https://iudx-rs-onem2m.iiit.ac.in/resource/nodes/"
PARAMETERS_RESPONSE = requests.get(PARAMETERS_API)
PARAMETERS_JSON = PARAMETERS_RESPONSE.json()


all_nodes = get_all_nodes(PARAMETERS_JSON)
write_JSON(FOLDER_PATH,'nodes.json',all_nodes)

