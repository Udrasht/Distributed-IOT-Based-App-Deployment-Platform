import requests
import json
import time
from json_utilities import *


DATA_URI = "https://iudx-rs-onem2m.iiit.ac.in/channels/"

# get all nodes
all_nodes = read_JSON(FOLDER_PATH,'nodes.json')

# iterate through all the nodes
channel_format={}
for node in all_nodes:
    node_data_response = requests.get(DATA_URI+node+"/feeds")
    if node_data_response.status_code == 200:
        node_data_json = node_data_response.json()
        channel_format[node] = node_data_json['channel']

write_JSON(FOLDER_PATH,'channel_format.json',channel_format)



