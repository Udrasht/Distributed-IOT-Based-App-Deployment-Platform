import random
import flask
import psycopg2
from flask_cors import cross_origin
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import InstanceViewTypes, InstanceViewStatus
import psutil
import datetime
import pandas as pd
import threading
from flask import Flask
from kafka import KafkaProducer, KafkaConsumer
import json
from logger import logger


def sql_query_runner(sql_query):
    conn_json = {
        "host": "ias-dev.postgres.database.azure.com",
        "port": "5432",
        "uid": "iasgroup3",
        "pwd": "IASdev@2022",
        "db": "ias"
    }

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=conn_json["host"],
        port=conn_json["port"],
        database=conn_json["db"],
        user=conn_json["uid"],
        password=conn_json["pwd"]
    )

    if sql_query.startswith("SELECT"):
        # Execute an SQL query and get the results in a DataFrame
        df = pd.read_sql_query(sql_query, conn)

        conn.close()
        return df

    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()
    cursor.close()
    conn.close()


class Node:
    def __init__(self, subscription_id, resource_group_name, vm_name, client_id, client_secret, tenant_id):
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.vm_name = vm_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

        credential = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
        self.compute_client = ComputeManagementClient(credential, self.subscription_id)

    def get_health(self):
        vm = self.compute_client.virtual_machines.get(self.resource_group_name, self.vm_name)

        # Get the CPU usage of the VM using psutil
        cpu_usage_percent = psutil.cpu_percent()

        # Get the memory usage of the VM using psutil
        memory_usage_percent = psutil.virtual_memory().percent

        # Get the disk usage of the VM using the Azure Compute Management Client
        disk_usage_percent = 0
        for disk in vm.storage_profile.data_disks:
            disk_instance_view = self.compute_client.disks.get(self.resource_group_name, disk.name,
                                                               expand=InstanceViewTypes.instance_view).instance_view
            disk_status = [status for status in disk_instance_view.statuses if status.code.startswith('PowerState/')][0]
            if disk_status.display_status == 'Attached':
                for volume in disk_instance_view.volumes:
                    if volume.status == InstanceViewStatus('Attached'):
                        disk_usage_percent += volume.disk_usage_percent

        health = ((100 - cpu_usage_percent) + (100 - memory_usage_percent) + (100 - disk_usage_percent)) / 3

        return cpu_usage_percent, memory_usage_percent, disk_usage_percent, health

    def monitor(self):
        cpu_usage, memory_usage, disk_usage, health = self.get_health()

        # log
        query = f"INSERT INTO infra.node_health_log (node_name, cpu_usage, memory_usage, disk_usage, health, added_on) " \
                f"VALUES ('{self.vm_name}', '{cpu_usage}', '{memory_usage}', '{disk_usage}', '{health}', '{datetime.datetime.now()}');"
        sql_query_runner(query)

        # Check for overload of resources
        threshold = 90
        if cpu_usage > threshold:
            print("Alert: CPU Usage above threshold")
        elif memory_usage > threshold:
            print("Alert: Memory Usage above threshold")
        elif disk_usage > threshold:
            print("Alert: Disk Usage above threshold")


def get_all_nodes():
    query = "SELECT * FROM infra.nodes"
    res = sql_query_runner(query)
    node_names = res['node_name'].tolist()
    return node_names, res


def get_node_health():
    res_json = {
        "subscription_id": "db1bf5b9-f0c1-4638-92be-a7e273b6555f",
        "resource_group_name": "IAS_Project",
        "client_id": "c4c3713c-34db-4c2b-b239-05afa2341bf6",
        "client_secret": "JpM8Q~7xNgu10oLvidc9n2nNzQior4lLbPYnTdhk",
        "tenant_id": "031a3bbc-cf7c-4e2b-96ec-867555540a1c"
    }

    vm_names, vm_info = get_all_nodes()
    nodes_health = dict()

    for i in range(len(vm_names)):
        node = Node(res_json["subscription_id"], res_json["resource_group_name"], vm_names[i], res_json["client_id"],
                    res_json["client_secret"], res_json["tenant_id"])
        cpu_usage, memory_usage, disk_usage, health = node.get_health()
        nodes_health[vm_names[i]] = health
        print(f"Resource Utilization for Node {vm_names[i]}:")
        print(f"CPU usage: {cpu_usage}%")
        print(f"Memory usage: {memory_usage}%")
        print(f"Disk usage: {disk_usage}%\n")
        print(f"Node {vm_names[i]} Health: {health}%\n")

    max_health_node = max(nodes_health, key=lambda x: nodes_health[x])
    print(f"Node {max_health_node} has maximum health of {nodes_health[max_health_node]}%")

    res = vm_info[vm_info['node_name'] == max_health_node]

    # Convert the first row of the filtered dataframe to a JSON string
    res = json.loads(res.iloc[0].to_json())
    res["port"] = random.randrange(7000, 7500, 10)

    # Print the JSON string
    print(res)

    return res


def get_all_nodes_health():
    res_json = {
        "subscription_id": "db1bf5b9-f0c1-4638-92be-a7e273b6555f",
        "resource_group_name": "IAS_Project",
        "client_id": "c4c3713c-34db-4c2b-b239-05afa2341bf6",
        "client_secret": "JpM8Q~7xNgu10oLvidc9n2nNzQior4lLbPYnTdhk",
        "tenant_id": "031a3bbc-cf7c-4e2b-96ec-867555540a1c"
    }

    vm_names, vm_info = get_all_nodes()
    nodes_health = dict()
    res = []

    for i in range(len(vm_names)):
        node = Node(res_json["subscription_id"], res_json["resource_group_name"], vm_names[i], res_json["client_id"],
                    res_json["client_secret"], res_json["tenant_id"])
        cpu_usage, memory_usage, disk_usage, health = node.get_health()
        nodes_health[vm_names[i]] = health
        vm_json = {"name": vm_names[i], "CPU Usage": cpu_usage, "Memory Usage": memory_usage, "Disk Usage": disk_usage,
                   "Health": health}
        res.append(vm_json)

    return res


def monitor_nodes():
    res_json = {
        "subscription_id": "db1bf5b9-f0c1-4638-92be-a7e273b6555f",
        "resource_group_name": "IAS_Project",
        "client_id": "c4c3713c-34db-4c2b-b239-05afa2341bf6",
        "client_secret": "JpM8Q~7xNgu10oLvidc9n2nNzQior4lLbPYnTdhk",
        "tenant_id": "031a3bbc-cf7c-4e2b-96ec-867555540a1c"
    }

    vm_names = get_all_nodes()

    for i in range(len(vm_names)):
        node = Node(res_json["subscription_id"], res_json["resource_group_name"], vm_names[i], res_json["client_id"],
                    res_json["client_secret"], res_json["tenant_id"])
        node.monitor()


def delete_logs():
    query = "DELETE FROM infra.node_health_log WHERE date(added_on) < CURRENT_DATE() - 7;"
    sql_query_runner(query)


app = Flask(__name__)


@app.route("/nodemgr/get-deploy-node", methods=['GET'])
@cross_origin()
def get_deploy_node():
    res = get_node_health()
    return flask.jsonify(res)


@app.route("/nodemgr/get-all-nodes-health", methods=['GET'])
@cross_origin()
def get_all_nodes_health1():
    res = get_all_nodes_health()
    return flask.jsonify(res)


@app.route("/nodemgr/log", methods=['GET'])
@cross_origin()
def get_log():
    monitor_nodes()
    pass


@app.route("/nodemgr/delete-old-logs", methods=['DELETE'])
@cross_origin()
def delete_old_logs():
    delete_logs()
    return "Success"


@app.route("/home", methods=['GET'])
@cross_origin()
def home():
    return "Hi, this is NodeManager"


@app.route("/health", methods=['GET'])
@cross_origin()
def health():
    logger.info("Health Checked")
    return "Ok"


@app.route("/get_logs", methods=['GET'])
@cross_origin()
def get_logs():
    logs = ""
    with open("/logs/nodemgr_logs.log", "r") as log_file:
        for line in (log_file.readlines()[-10:]):
            logs += line

    print(logs)
    return {"logs": logs}


# ---------------------------- KAFKA  ------------------------------


# Configure Kafka producer and consumer
producer = KafkaProducer(
    bootstrap_servers=['20.196.205.46:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,  # Number of times to retry a message in case of failure
    max_in_flight_requests_per_connection=1,  # Ensure only one request is in-flight
    acks='all',  # Wait for all replicas to acknowledge the message
)

consumer = KafkaConsumer("NodeManager", bootstrap_servers=['20.196.205.46:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))

requests_m1_c, requests_m1_p, requests_m2_c, requests_m2_p = [], [], [], []
lock = threading.Lock()


def send(request_data, msg, c_list, p_list):
    request_id = request_data['request_id']

    lock.acquire()
    if request_id in c_list:
        print("Duplicate message!")
        lock.release()
        return
    c_list.append(request_id)
    lock.release()

    print(f"Request : {request_data}")

    # Check if request ID has already been processed before sending message
    lock.acquire()
    if request_id in p_list:
        print("Duplicate message!")
        lock.release()
        return
    p_list.append(request_id)
    lock.release()

    producer.send(msg['to_topic'], msg)


# Define the function for consuming requests and sending responses
def consume_requests():
    global requests_m1_c, requests_m1_p, requests_m2_c, requests_m2_p
    global consumer, producer
    for message in consumer:
        request_data = message.value

        # M1
        if "give best node" in request_data['msg']:
            app_name = request_data['msg'].split("$")[1]
            res = get_node_health()
            res["app_name"] = app_name
            msg = {
                'to_topic': 'DeploymentManager',
                'from_topic': 'NodeManager',
                'request_id': request_data['request_id'],
                'msg': f"ans-node${str(res)}"
            }
            send(request_data, msg, requests_m1_c, requests_m1_p)


if __name__ == "__main__":
    thread = threading.Thread(target=consume_requests)
    thread.start()
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
    thread.join()
