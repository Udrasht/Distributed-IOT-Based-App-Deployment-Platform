# FETCHING THE DATA FROM OM2M SERVER AND 
# WRITING IT TO THE RESPECTIVE KAFKA TOPIC

import ast
import matplotlib.pyplot as plt
import time
from IPython.display import clear_output
import requests
import json
import threading
from kafka import KafkaProducer
import json
from kafka_utilities import *

BASE_URI = "http://localhost:5089/~/in-cse/in-name/"
RCN = "/?rcn=4"
APPLICATION_ENTITY = "IAS-IOT-AVISHKAR-23"

URL_DESC = BASE_URI + APPLICATION_ENTITY
URL = BASE_URI + APPLICATION_ENTITY + RCN

HEADERS = {
    'X-M2M-Origin': 'admin:admin',
    'Accept': 'application/json'
}
PAYLOAD = {}


# printing readable JSON
def print_JSON(json_dict):
    print(json.dumps(json_dict, indent=4))


# find descriptor
def find_descriptor(url_des):
    url_des = url_des + "/Descriptor/la"
    response = requests.request("GET", url_des, headers=HEADERS, data=PAYLOAD)
    data = json.loads(response.text)
    return data["m2m:cin"]["con"]


# serializer for kafka
def json_serializer(sensor_data):
    return json.dumps(sensor_data).encode('utf-8')


# getting partition and topic details
def give_partition_and_topic_details(descriptor):
    partition_details = {}
    topic_details = {}
    sensor_types = []
    discard_values = ['timestamp', 'occupancy-state']
    partition_number = 0

    for key in descriptor:
        partition_details[key] = partition_number
        partition_number = partition_number + 1
        for sensor_type in descriptor[key]:
            sensor_types.append(sensor_type)

    sensor_types = set(sensor_types)
    for value in discard_values:
        sensor_types.remove(value)

    for sensor_type in sensor_types:
        topic_details[sensor_type] = f"{sensor_type}-topic"

    return partition_details, topic_details


# get the descriptor details
def get_descriptor():
    HEADERS = {
        'X-M2M-Origin': 'admin:admin',
        'Accept': 'application/json'
    }
    PAYLOAD = {}
    response = requests.request("GET", URL, headers=HEADERS, data=PAYLOAD)
    data = json.loads(response.text)
    descriptor = {}

    for itr in data["m2m:ae"]["m2m:cnt"]:
        description = find_descriptor(URL_DESC + "/" + itr["rn"])
        descriptor[itr["rn"]] = ast.literal_eval(description)

    return data, descriptor


# get request to getch the latest data
def fetch_latest_data(url_des):
    url_des = url_des + "/Data/la"
    response = requests.request("GET", url_des, headers=HEADERS, data=PAYLOAD)
    data = json.loads(response.text)
    return data["m2m:cin"]["con"]


def fetch_data_write_in_topic(url_desc, itr, descriptor):
    sensor_data = fetch_latest_data(URL_DESC + "/" + itr["rn"])
    nodename = itr["rn"]
    node_descriptor = descriptor[itr["rn"]]

    parameters = node_descriptor
    sensor_data = ast.literal_eval(sensor_data)
    time_stamp = sensor_data[0]
    occupancy_state = sensor_data[1]

    for i in range(2, len(parameters)):
        if (parameters[i] not in data_dict):
            data_dict[parameters[i]] = []
        node_data = {
            "nodename": nodename,
            "value": sensor_data[i],
            "timestamp": time_stamp,
            "occupancy-state": occupancy_state
        }
        data_dict[parameters[i]].append(node_data)


if __name__ == "__main__":
    print("URL ", URL)
    print("URL DESC", URL_DESC)

    data, descriptor = get_descriptor()
    print("DESCRIPTOR DICT ")
    print_JSON(descriptor)

    partition_details, topic_details = give_partition_and_topic_details(descriptor)
    print("PARTITION DETAILS")
    print_JSON(partition_details)
    print("TOPIC DETAILS")
    print_JSON(topic_details)
    n_partition = len(partition_details)

    while True:
        data_dict = {}
        threads = []
        # looping through nodes
        for itr in data["m2m:ae"]["m2m:cnt"]:
            thread = threading.Thread(target=fetch_data_write_in_topic, args=(URL_DESC, itr, descriptor))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        nodes_json = json.dumps(data_dict)
        print("DATA")
        print_JSON(data_dict)

        # separate the data from the dictionary
        for sensor in data_dict:
            for sensor_data in data_dict[sensor]:
                kafka_topic = topic_details[sensor]
                print(
                    f"topic_name={kafka_topic},partition={partition_details[sensor_data['nodename']]},data={sensor_data}")
                producer = KafkaProducer(bootstrap_servers=['20.196.205.46:9092'], value_serializer=json_serializer)
                producer.send(kafka_topic, value=sensor_data, partition=partition_details[sensor_data['nodename']])
                producer.close()

#     # give the data to the producer
#     # producer.send("sensor-kafka-topic",value=nodes_json)
#     # producer.close()
#     break
#     # time.sleep(10)
#     # result = thread.join()


# def main_fun( URL_DESC, itr ):
#     sensor_data = fetch_latest_data(URL_DESC + "/" + itr["rn"])
#     nodename = itr["rn"]
#     node_descriptor = desc_dict[itr["rn"]]

#     # print(itr["rn"], desc_dict[itr["rn"]], sensor_data)
#     parameters = node_descriptor

#     sensor_data = ast.literal_eval(sensor_data)
#     time_stamp = sensor_data[0]
#     occupency_state = sensor_data[1]

#     for i in range(2, len(parameters)):
#         if (parameters[i] not in dict_json):
#             dict_json[parameters[i]] = []
#         node_data = {
#             "nodename": nodename,
#             "value": sensor_data[i],
#             "timestamp": time_stamp,
#             "occupancy-state": occupency_state
#         }
#         dict_json[parameters[i]].append(node_data)

# response = requests.request("GET", URL, headers=HEADERS, data=PAYLOAD)
# data = json.loads(response.text)

# n_nodes = len(data["m2m:ae"]["m2m:cnt"])

# # no of nodes

# print("NODES", n_nodes)

# desc_dict = {}
# for itr in data["m2m:ae"]["m2m:cnt"]:
#     description = desc_find(URL_DESC + "/" + itr["rn"])
#     desc_dict[itr["rn"]] = ast.literal_eval(description)

# print("DESCRIPTOR DICT", json.dumps(desc_dict,indent=4))


# fetching data from OM2M using Threading
# producer = KafkaProducer(bootstrap_servers=['20.196.205.46:9092'],value_serializer=json_serializer)

# while True:
#     dict_json = {}
#     threads = []
#     #looping through nodes
#     for itr in data["m2m:ae"]["m2m:cnt"]:

#         thread = threading.Thread(target=main_fun, args=(URL_DESC, itr))
#         threads.append(thread)
#         thread.start()

#     for t in threads:
#         t.join()

#     nodes_json = json.dumps(dict_json)
#     print_JSON(dict_json)

#     # separate the data from the dictionary
#     for keys in dict_json:
#         # print(keys)
#         # print_JSON(dict_json[keys])
#         v=1
#         # kafka_topic = kafka_topics[keys]
#         # kafka_value = dict_json[keys][0]


#     # give the data to the producer
#     # producer.send("sensor-kafka-topic",value=nodes_json)
#     # producer.close()
#     break
#     # time.sleep(10)
#     # result = thread.join()
