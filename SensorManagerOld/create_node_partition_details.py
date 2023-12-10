import requests
import json

APPLICATION_ENTITY_URI = "http://dev-rs-testing.iiit.ac.in:8000/resource/sensors"
NODES_URI="http://dev-rs-testing.iiit.ac.in:8000/resource/nodes"

def print_JSON(json_dict):
    print(json.dumps(json_dict,indent=4))

def get_all_application_entities(application_entity_json_dict):
    all_application_entities=[]
    for application_entity in application_entity_json_dict:
        all_application_entities.append(application_entity)
    return all_application_entities

def get_all_nodes(node_result_dict):
    all_nodes = []
    for node in node_result_dict['results']['Timestamp']:
        all_nodes.append(node)
    return all_nodes

def build_topic_name(application_entity):
    return application_entity+'-topic'

def get_node_details(application_entities_list,all_nodes_list):
    ae_node_details={}
    ae_partition_mapping={}
            
    partition_num = 0
    application_entity_idx=0
    for node in all_nodes_list:
        if node.startswith(application_entities_list[application_entity_idx]):
            node_details={}
            node_details['topic-name']=build_topic_name(application_entities_list[application_entity_idx])
            node_details['partition-number']=partition_num
            node_details['application-entity']=application_entities_list[application_entity_idx]
            ae_node_details[node]=node_details
        else:
            partition_num=0
            application_entity_idx=application_entity_idx+1
            node_details={}
            node_details['topic-name']=build_topic_name(application_entities_list[application_entity_idx])
            node_details['partition-number']=partition_num
            node_details['application-entity']=application_entities_list[application_entity_idx]
            ae_node_details[node]=node_details
            
        partition_num=partition_num+1
        ae_partition_mapping[application_entities_list[application_entity_idx]]=partition_num
    return ae_node_details,ae_partition_mapping
        
def write_node_details_to_json(ae_node_details):
# Open a new file for writing
    with open("./SensorManager/node_details.json", "w") as file:
        # Use the json.dump() function to write the dictionary to the file
        json.dump(ae_node_details, file)

def write_partition_mapping_to_json(ae_partition_mapping):
    # Open a new file for writing
    with open("./SensorManager/ae_partition_mapping.json", "w") as file:
        # Use the json.dump() function to write the dictionary to the file
        json.dump(ae_partition_mapping, file)

def write_ae_sensors_to_json(ae_sensor_details):
    # Open a new file for writing
    with open("./SensorManager/ae_sensor_details.json", "w") as file:
        # Use the json.dump() function to write the dictionary to the file
        json.dump(ae_sensor_details, file)


def write_all_sensors(application_entity_dict):
    unique_sensors=[]
    for application_entity in application_entity_dict:
        sensor_types = application_entity_dict[application_entity]
        unique_sensors.extend(sensor_types)
    
    unique_sensors = set(unique_sensors)
    unique_sensors.discard('Timestamp')
    unique_sensors = list(unique_sensors)
    with open('./SensorManager/unique_sensors.json', 'w') as f:
        json.dump(unique_sensors, f)

    print(unique_sensors)


        
APPLICATION_ENTITY_DATA = requests.get(APPLICATION_ENTITY_URI)
APPLICATION_ENTITY_DICT = APPLICATION_ENTITY_DATA.json()
NODES_RESULT = requests.get(NODES_URI)
NODE_RESULT_DICT = NODES_RESULT.json()


all_application_entities = get_all_application_entities(APPLICATION_ENTITY_DICT)
all_nodes = get_all_nodes(NODE_RESULT_DICT)

# print("AE")
# print(all_application_entities)
# print("NODES")
# print(all_nodes)
# print("AE_NODES_PARTITION")
ae_node_details,ae_partition_mapping = get_node_details(all_application_entities,all_nodes)
write_all_sensors(APPLICATION_ENTITY_DICT)
# print_JSON(ae_node_details)
# print_JSON(ae_partition_mapping)
write_node_details_to_json(ae_node_details)
write_partition_mapping_to_json(ae_partition_mapping)
write_ae_sensors_to_json(APPLICATION_ENTITY_DICT)


    


