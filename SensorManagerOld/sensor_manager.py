from flask import Flask
import json
from new_kafka_consumer_utilities import *

app = Flask(__name__)

def read_node_details_JSON():
    with open('./SensorManager/node_details.json', 'r') as f:
        data = json.load(f)
    return data

def read_partition_mapping_JSON():
    with open('./SensorManager/ae_partition_mapping.json', 'r') as f:
        data = json.load(f)
    return data

def read_ae_sensor_details_JSON():
    with open('./SensorManager/ae_sensor_details.json', 'r') as f:
        data = json.load(f)
    return data

def read_unique_sensor_JSON():
    with open('./SensorManager/unique_sensors.json', 'r') as f:
        data = json.load(f)
    return data
    
# printing readable JSON
def print_JSON(json_dict):
    print(json.dumps(json_dict,indent=4))

node_details = read_node_details_JSON()
ae_partition_mapping = read_partition_mapping_JSON()
ae_sensor_details = read_ae_sensor_details_JSON()

# API END POINTS

@app.route('/api/sensordata/latest/<nodename>',methods=['GET'])
def get_node_latest_data(nodename):
    topic_name = node_details[nodename]['topic_name']
    partion_num = node_details[nodename]['partition-number']
    return get_latest_data_from_topic(topic_name,partion_num)

@app.route('/api/sensordata/latest/<nodename>/<n_messages>',methods=['GET'])
def get_node_last_n_values(nodename,n_messages):
    topic_name = node_details[nodename]['topic_name']
    partion_num = node_details[nodename]['partition-number']
    return get_last_n_data_from_topic(topic_name,partion_num,n_messages)

@app.route('/api/sensordata/latest/<nodename>/<sensor>',methods=['GET'])
def get_latest_sensor_data_of_node(nodename,sensor):
    application_entity = node_details[nodename]['application-entity']
    if sensor not in ae_sensor_details[application_entity]:
        return "sensor not found"
    else:
        topic_name = node_details[nodename]['topic_name']
        partion_num = node_details[nodename]['partition-number']
        all_data = get_latest_sensor_data_of_node(topic_name,partion_num)
        # convert all_data to json and get only the value of the temperature

    return "node-sensor"


@app.route('/api/sensordata/latest/<nodename>/<sensor>/<n_messages>',methods=['GET'])
def get_last_n_sensor_data_of_node(nodename,sensor,n_messages):
    application_entity = node_details[nodename]['application-entity']
    if sensor not in ae_sensor_details[application_entity]:
        return "sensor not found" 
    else:
        topic_name = node_details[nodename]['topic_name']
        partion_num = node_details[nodename]['partition-number']
        all_data = get_last_n_data_from_topic(topic_name,partion_num,n_messages)
        # convert all_data to json and get only the value of the temperature

    return "node-sensor_n_messages"

@app.route('/api/sensors',methods=['GET'])
def get_all_sensors():
    all_sensors = read_unique_sensor_JSON()
    # print("79",all_sensors)
    return json.dumps(all_sensors)





if __name__ == "__main__":
    app.run(host='localhost',port=8000)
