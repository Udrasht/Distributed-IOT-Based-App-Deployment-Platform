import json
from json_utilities import *

def get_verticals():
    verticals_JSON = read_JSON(FOLDER_PATH,'verticals.json')
    verticals = []
    for vertical in verticals_JSON:
         verticals.append(vertical)
    return verticals

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


verticals_list = get_verticals()
nodes_list = read_JSON(FOLDER_PATH,'nodes.json')
node_partition,vertical_partition = get_node_details(verticals_list,nodes_list)

write_JSON(FOLDER_PATH,'node_partition.json',node_partition)
write_JSON(FOLDER_PATH,'vertical_partition.json',vertical_partition)

