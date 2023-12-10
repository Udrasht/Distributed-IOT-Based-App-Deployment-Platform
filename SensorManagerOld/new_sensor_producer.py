import json
import requests
from kafka import KafkaProducer


def read_node_details_JSON():
    with open('./SensorManager/node_details.json', 'r') as f:
        data = json.load(f)
    return data

def read_partition_mapping_JSON():
    with open('./SensorManager/ae_partition_mapping.json', 'r') as f:
        data = json.load(f)
    return data

# serializer for kafka
def json_serializer(sensor_data):
    return json.dumps(sensor_data).encode('utf-8')

def print_JSON(json_dict):
    print(json.dumps(json_dict,indent=4))


node_details = read_node_details_JSON()
ae_partition_mapping = read_partition_mapping_JSON()

DATA_URI = "http://dev-rs-testing.iiit.ac.in:8000/resource/data"
SENSOR_DATA = requests.get(DATA_URI)
# SENSOR_DATA.json() type : dict
print_JSON(SENSOR_DATA.json())
sensor_data = SENSOR_DATA.json()
for node in sensor_data:
    topic_name = node_details[node]['topic-name']
    n_partion = node_details[node]['partition-number']
    data = sensor_data[node]['latest_data']
    print(topic_name,n_partion,data)

    # TODO logic to only write the data when the latest data and the previous data is different

    producer = KafkaProducer(bootstrap_servers=['20.196.205.46:9092'],value_serializer=json_serializer)
    producer.send(topic_name,value=data,partition=n_partion)
    producer.close()
