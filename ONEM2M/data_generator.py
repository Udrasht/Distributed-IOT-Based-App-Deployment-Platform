import os
import time
import math
import json
import random
import threading
import requests
from IPython.display import clear_output
data_frequency =10 #10 seconds
APPLICATION_ENTITY='IAS-IOT-AVISHKAR-23'

def read_source_tree_JSON():
    with open('./ONEM2M/source_tree.json', 'r') as f:
        data = json.load(f)
    return data


def post_random_data(nodename,n_fields):
    n_field = int(n_fields)

    timestamp = int(time.time())
    occupancy_state = random.randint(0, 1)
    _data_cin =[timestamp,occupancy_state]
    for i in range(n_fields-2):
        _data_cin.append(random.randint(1,50))

    URL = 'http://127.0.0.1:5089/~/in-cse/in-name/'+APPLICATION_ENTITY+'/'+nodename+'/Data'
    headers = {
      'X-M2M-Origin': 'admin:admin',
      'Content-Type': 'application/json;ty=4'
    }
    payload = {
        "m2m:cin": {
            "con": "{}".format(_data_cin),
            "lbl": [nodename],
            "cnf": "text"
        }
    }
    response = requests.request("POST", URL, headers=headers, json=payload)
    print(response.text)
    return response.status_code

source_tree = read_source_tree_JSON()
def run():
    publish_count=0
    while True:
        for node in source_tree['nodes']:
            status_code = post_random_data(node['nodename'],node['n_fields'])
            if status_code == 201:
                
                print("Data publishing at " + str(data_frequency) + "-second frequency")
                print("Publish Successful")
                print("Number of data point published = " + str(publish_count))
            else:
                print("Unable to publish data, process failed with a status code: " + str(status_code))
        time.sleep(data_frequency)
        publish_count += 1
        clear_output(wait=True)


run()
