import subprocess
import threading
import requests
from flask import Flask
from flask_cors import cross_origin
from kafka import KafkaProducer, KafkaConsumer
import json
from azure.storage.blob import BlobServiceClient
import os
from service_registry import *
from logger import logger

app = Flask(__name__)

# Configure Kafka producer and consumer
producer = KafkaProducer(
    bootstrap_servers=['20.196.205.46:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,  # Number of times to retry a message in case of failure
    max_in_flight_requests_per_connection=1,  # Ensure only one request is in-flight
    acks='all',  # Wait for all replicas to acknowledge the message
)

consumer = KafkaConsumer("DeploymentManager", bootstrap_servers=['20.196.205.46:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))

requests_m1_c, requests_m1_p = [], []  # For message 1
requests_m2_c, requests_m2_p = [], []  # For message 2
requests_m3_c, requests_m3_p = [], []  # For message 3
lock = threading.Lock()


def delete_local_file(app_name):
    files = os.listdir(app_name)

    # Loop through the list and delete each file
    for file in files:
        file_path = os.path.join(app_name, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"{file_path} deleted successfully.")
        except Exception as e:
            print(f"Error: {e}")

    os.rmdir(app_name)
    print("####### Directory deleted #######")


def download_from_blob(app_name, folder_name):
    STORAGE_CONTAINER = 'iascontainer'
    AZURE_BLOB_CONN_STRING = 'DefaultEndpointsProtocol=https;AccountName=iot3storage;AccountKey=u3yqnLbhzlY+AQLJspkYm679Ivav12oAtt0f7allcFReHvcZVbAdCL9nD6Xkb0Ls3MaxNfXIQ2p2+ASt23CK7w==;EndpointSuffix=core.windows.net'
    # FOLDER_NAME = 'sampleApp4_fa5801d2-e21b-11ed-a400-3035adbc6520'

    # Create a directory with the same name as the folder on Azure Blob Storage
    os.makedirs(app_name, exist_ok=True)

    # Create the subdirectories inside the main directory
    os.makedirs(os.path.join(app_name, 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(app_name, 'static', 'js'), exist_ok=True)

    # Connect to the Azure Blob Storage container
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONN_STRING)
    container_client = blob_service_client.get_container_client(STORAGE_CONTAINER)

    # List all the blobs in the folder
    blob_list = container_client.list_blobs(name_starts_with=app_name)

    # Loop through the blob list and download each file to the local directory
    for blob in blob_list:
        # Define the path to save the file locally
        file_path = os.path.join(app_name, blob.name.replace(app_name + '/', ''))
        print(file_path)

        # Download the blob to a file
        with open(file_path, "wb") as my_blob:
            download_stream = container_client.download_blob(blob)
            my_blob.write(download_stream.readall())

        print(f"{file_path} downloaded successfully.")


# def download_from_blob(app_name, folder_name):
#     STORAGE_CONTAINER = 'iascontainer'
#     AZURE_BLOB_CONN_STRING = 'DefaultEndpointsProtocol=https;AccountName=iot3storage;AccountKey=u3yqnLbhzlY+AQLJspkYm679Ivav12oAtt0f7allcFReHvcZVbAdCL9nD6Xkb0Ls3MaxNfXIQ2p2+ASt23CK7w==;EndpointSuffix=core.windows.net'

#     # Create the blob service client
#     blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONN_STRING)

#     # Get a reference to the container
#     container_client = blob_service_client.get_container_client(STORAGE_CONTAINER)

#     # List all the blobs in the folder
#     blob_list = container_client.list_blobs(name_starts_with=folder_name)

#     # Loop through the blob list and print out the name of each blob
#     os.mkdir(app_name)
#     print("####### Directory made #######")

#     for blob in blob_list:
#         # Download the blob to a file
#         # Define the name of the file to download
#         file_name = blob.name.replace(folder_name, '', 1)

#         # Download the blob to a file
#         with open(app_name + "/" + file_name, "wb") as my_blob:
#             download_stream = container_client.download_blob(blob)
#             my_blob.write(download_stream.readall())
#         with open(app_name + "/" + file_name, "wb") as my_blob:
#             download_stream = container_client.download_blob(blob)
#             my_blob.write(download_stream.readall())
#             print(file_name + " #### Copied ####")
#             my_blob.close()

#     # Copying the hard-coded shell file in our local app name folder

#     print("########## Deployment code also copied ##########")


def deployInVM(service_start_shell_file, app_name, vm_ip, vm_username, vm_key_path, vm_service_path):
    file_copy_command = f"scp -o StrictHostKeyChecking=no -r -i {vm_key_path}  {app_name} {vm_username}@{vm_ip}:{vm_service_path}"

    execute_command = f"""
        ssh -o StrictHostKeyChecking=no -i {vm_key_path} {vm_username}@{vm_ip} cd {app_name} && sudo bash ./{service_start_shell_file}
    """

    os.system(file_copy_command)
    print("Folder copied")

    # delete_local_file(app_name)

    output = subprocess.check_output(execute_command.split())
    container_id = output.strip().decode('utf-8')
    print("Executed on VM")
    return container_id


def unDeployInVM(service_stop_shell_file, app_name, vm_ip, vm_username, vm_key_path):
    execute_command = f"""
        ssh -o StrictHostKeyChecking=no -i {vm_key_path} {vm_username}@{vm_ip} "cd {app_name}; sudo bash ./{service_stop_shell_file}; rm -r ../{app_name}; cd .."
        """

    os.system(execute_command)
    print("App stopped")


def create_file(path, file_name, docker_code):
    f = open(path + '/' + file_name, 'w')
    f.write(docker_code)
    f.close()


def docker_file_raw_text():
    docker_code = f"""
        FROM python:3.10
        ADD . .
        RUN pip3 install -r requirements.txt
        CMD python3 -u main.py
        """
    return docker_code


def service_start_raw_text(docker_file_name, image_name, container_name, host_port, container_port):
    print("Host port - ", host_port)
    service_start_shell_script = f'''
        docker build -f {docker_file_name} -t {image_name} .
        docker container run -d --name {container_name} -p {host_port}:{container_port} {image_name}
    '''

    return service_start_shell_script


def service_stop_raw_text(container_name):
    service_stop_shell_script = f'''
        docker stop {container_name}
        docker rm {container_name}
    '''

    return service_stop_shell_script


def generate_docker_file_and_service_start_shell(path, service, host_port, container_port):
    service = service.lower()
    docker_file_name = service + "_docker_file"
    image_file_name = service + "_img"
    container_file_name = service + "_container"
    service_start_file_name = service + "_start.sh"
    service_stop_file_name = service + "_stop.sh"

    docker_code = docker_file_raw_text()
    create_file('./' + path, docker_file_name, docker_code)

    service_start_code = service_start_raw_text(docker_file_name, image_file_name, container_file_name, host_port,
                                                container_port)
    create_file('./' + path, service_start_file_name, service_start_code)

    service_end_code = service_stop_raw_text(container_file_name)
    create_file('./' + path, service_stop_file_name, service_end_code)

    return service_start_file_name


def deploy_app(node_name, vm_ip, vm_port, app_name):
    # Kafka code to get app name and other details from  Application Manager
    folder_name = f'{app_name}/'
    # Kafka code to get VM details from  Node Manager
    vm_username = "azureuser"
    vm_key_path = f"./VM-keys/{node_name}_key.cer"
    vm_service_path = f"/home/azureuser/{app_name}"
    # ...............................................................

    # Getting app to be deployed in above VM details

    download_from_blob(app_name, folder_name)

    service_start_file_name = generate_docker_file_and_service_start_shell(app_name, app_name, vm_port, 7700)

    container_id = deployInVM(service_start_file_name, app_name, vm_ip, vm_username, vm_key_path, vm_service_path)

    return container_id


def un_deploy_app(app_name, vm_ip):
    service = app_name.lower()
    service_stop_file_name = service + "_stop.sh"
    vm_username = "azureuser"
    vm_key_path = "./VM-keys/VM1_key.cer"

    # ...............................................................
    unDeployInVM(service_stop_file_name, app_name, vm_ip, vm_username, vm_key_path)

    return "Deployment Manager has completed its job"


# -------------------------KAFKA-----------------------------

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
    global requests_m1_c, requests_m1_p, requests_m2_c, requests_m2_p, requests_m3_c, requests_m3_p
    global consumer, producer
    for message in consumer:
        request_data = message.value

        # M1 - message from app manager to deploy
        if "deploy app" in request_data['msg']:
            app_name = request_data['msg'].split("$")[1]
            msg = {
                'to_topic': 'NodeManager',
                'from_topic': 'DeploymentManager',
                'request_id': request_data['request_id'],
                'msg': f'give best node${app_name}'
            }
            send(request_data, msg, requests_m1_c, requests_m1_p)

        # M3 - message from app manager to stop app
        if "stop app" in request_data['msg']:
            app_name = request_data['msg'].split("$")[1]

            # deploy the app
            try:
                print("Unregistering by LB")
                params = {"appName": app_name}
                res = requests.get("http://20.21.102.175:8050/deregisterApp", params=params)
                logger.info(res.text)
                # un_deploy_app(app_name, vm_ip)

                msg = {
                    'to_topic': 'first_topic',
                    'from_topic': 'DeploymentManager',
                    'request_id': request_data['request_id'],
                    'msg': f'done stopped${app_name}'
                }

                unregister_app(app_name)

            except Exception as e:
                msg = {
                    'to_topic': 'first_topic',
                    'from_topic': 'DeploymentManager',
                    'request_id': request_data['request_id'],
                    'msg': f'App {app_name} not stopped. Error - {str(e)}'
                }

            send(request_data, msg, requests_m3_c, requests_m3_p)

        # M2 - message from node manager with ip and port
        if "ans-node" in request_data['msg']:
            res = json.loads(request_data['msg'].split("$")[1].replace('\'', '"'))
            ip_deploy = res["node_ip"]
            port_deploy = res["port"]
            app_name = res["app_name"]
            node_name = res["node_name"]
            print(ip_deploy, port_deploy, app_name, node_name)

            # deploy the app
            try:
                container_id = deploy_app(node_name, ip_deploy, port_deploy, app_name)
                params = {'appName': app_name, 'imageName': str(app_name).lower() + "_image", 'vmIp': ip_deploy,
                          'hostPort': port_deploy, 'containerPort': 8050, 'containerId': container_id}

                logger.info(str(params))
                res = requests.get("http://20.21.102.175:8050/registerApp", params=params)
                logger.info(str(res))

                msg = {
                    'to_topic': 'first_topic',
                    'from_topic': 'DeploymentManager',
                    'request_id': request_data['request_id'],
                    'msg': f'done {app_name} deploy - {str(res.text)}'
                }

                register_app(app_name, ip_deploy, port_deploy)

            except Exception as e:
                msg = {
                    'to_topic': 'first_topic',
                    'from_topic': 'DeploymentManager',
                    'request_id': request_data['request_id'],
                    'msg': f'App {app_name} not deployed. Error - {str(e)}'
                }

            send(request_data, msg, requests_m2_c, requests_m2_p)


@app.route("/home", methods=['GET'])
@cross_origin()
def home():
    return "Hi, this is DeploymentManager"


@app.route("/health", methods=['GET'])
@cross_origin()
def health():
    return "Ok"


@app.route("/get_logs", methods=['GET'])
@cross_origin()
def get_logs():
    logs = ""
    with open("/logs/depmgr_logs.log", "r") as log_file:
        for line in (log_file.readlines()[-10:]):
            logs += line

    print(logs)
    return {"logs": logs}


if __name__ == "__main__":
    thread = threading.Thread(target=consume_requests)
    thread.start()
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
    thread.join()
