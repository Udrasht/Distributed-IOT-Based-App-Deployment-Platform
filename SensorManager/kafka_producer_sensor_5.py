import requests
import json
import time
import random
from json_utilities import *
from kafka_consumer_sensor import *
from kafka import KafkaProducer

DATA_URI = "https://iudx-rs-onem2m.iiit.ac.in/channels/"

# serializer for kafka
def json_serializer(sensor_data):
    return json.dumps(sensor_data).encode('utf-8')

def parse_data(sensor_format,sensor_data):
    new_object = {
    "node_name": sensor_format["id"],
    "timestamp": sensor_data["created_at"],
    "description": sensor_format["description"]
    }

    for key in sensor_format.keys():
        if key.startswith("field") and key in sensor_data and key in sensor_format:
            new_key = sensor_format[key]
            new_value = sensor_data[key]
            new_object[new_key] = new_value

    return new_object

# get all nodes
all_nodes = read_JSON(FOLDER_PATH,'nodes.json')
channel_format = read_JSON(FOLDER_PATH,'channel_format.json')
node_partition = read_JSON(FOLDER_PATH,'node_partition.json')
# iterate through all the nodes
while True:
    for i in range(150,200):
        node = all_nodes[i]
        node_data_response = requests.get(DATA_URI+node+"/feeds")
        if node_data_response.status_code == 200:
            node_data_json = node_data_response.json()
            topic_name = node_partition[node]['topic-name']
            partition_num = int(node_partition[node]['partition-number'])
            parsed_data = parse_data(channel_format[node],node_data_json['feeds'][0])
            try:
                last_data = get_latest_node_data(topic_name,partition_num)
                last_data = last_data.decode('utf-8')
                last_data = json.loads(last_data)
                if last_data['timestamp'] != parsed_data['timestamp']:
                    print(f"pushing new data into the topic {topic_name} partition {partition_num}")
                    producer = KafkaProducer(bootstrap_servers=['20.196.205.46:9092'],value_serializer=json_serializer)
                    producer.send(topic_name,value=parsed_data,partition=partition_num)
                    producer.close()
                else:
                    print("current data and last data are same")
            except AssertionError:
                print(f"Unable to fetch last data, writing the current data into the topic {topic_name} partition {partition_num}")
                producer = KafkaProducer(bootstrap_servers=['20.196.205.46:9092'],value_serializer=json_serializer)
                producer.send(topic_name,value=parsed_data,partition=partition_num)
                producer.close()
        