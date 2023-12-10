from oneM2M_functions import *
import json

def read_node_JSON():
    with open('./ONEM2M/source_tree.json', 'r') as f:
        data = json.load(f)
    return data

server = "http://127.0.0.1:5089"
cse = "/~/in-cse/in-name/"

node_data = read_node_JSON()

# ------------------------------------------
ae = node_data['application']
lbl_ae = ["Label-1", "Label-2"]
create_ae(server+cse, ae, lbl_ae)
# ------------------------------------------

descriptor_container_name = "Descriptor"
lbl_cnt = ["CNT-Label-1", "CNT-Label-2"]
# create_cnt(server+cse+ae + "/" + node_container_name, descriptor_container_name, lbl_cnt)

data_container_name = "Data"
lbl_cnt = ["CNT-Label-1", "CNT-Label-2"]
# create_cnt(server+cse+ae + "/" + node_container_name, data_container_name, lbl_cnt)

lbl_cin = ["CIN-Label-1", "CIN-Label-2"]

for nodes in node_data['nodes']:
    node_container_name = nodes['nodename']
    lbl_cnt = ["CNT-Label-1", "CNT-Label-2"]
    create_cnt(server+cse+ae, node_container_name, lbl_cnt)
    create_cnt(server+cse+ae + "/" + node_container_name, descriptor_container_name, lbl_cnt)
    create_cnt(server+cse+ae + "/" + node_container_name, data_container_name, lbl_cnt)
    content_instance = str(nodes['descriptor'])
    create_data_cin(server+cse+ae + "/" + node_container_name +"/"+ descriptor_container_name, content_instance, lbl_cin)
    create_data_cin(server+cse+ae + "/" + node_container_name +"/"+ data_container_name, 0, lbl_cin)

