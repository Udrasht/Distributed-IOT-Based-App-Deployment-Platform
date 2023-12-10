import sys
import os
from flask import Flask, request, abort, jsonify, make_response
from flask_cors import cross_origin, CORS

from kafka_consumer_sensor import get_latest_node_data, get_latest_n_node_data
from json_utilities import read_JSON, FOLDER_PATH
from logger import logger
import json
from kafka_consumer_sensor import get_latest_node_data, get_latest_n_node_data
from json_utilities import read_JSON, FOLDER_PATH, print_JSON

# Get the absolute path of the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Set the current working directory to the parent directory of the script directory
os.chdir(os.path.join(script_dir, '..'))
print(os.getcwd())

app = Flask(__name__)
CORS(app)


def filter_location(sensor_type, locations):
    if sensor_type == 'SR-OC':
        locations = [location[-7:] for location in locations]
    return locations


# SENSOR REGISTRY APIs - TODO later
@app.route('/api/sensor/register/vertical', methods=['GET', 'POST'])
@cross_origin()
def vertical_registration():
    req_body = request.get_json()
    vertical = req_body['vertical']
    node_name = req_body['node_name']
    descriptor = req_body['descriptor']
    print(descriptor)
    return "vertical registration"


# @app.route('/api/sensor/location/<vertical>', methods=['GET'])
# @cross_origin()
# def get_vertical_vise_location(vertical):
#     vertical_location = read_JSON(FOLDER_PATH, 'vertical_location.json')
#     if vertical in vertical_location:
#         return jsonify(vertical_location[vertical])
#     else:
#         return jsonify({'statusCode': '400', 'message': 'Invalid Vertical'})


# localhost:8050/api/sensor/intersection/verticals?applicationType=AQ,SR-OC,SR-QA,SR-AC
@app.route('/api/sensor/intersection/verticals', methods=['GET'])
@cross_origin()
def get_vertical_vise_location():
    applicationTypes = request.args.get('applicationType')
    applicationTypes = applicationTypes.split(",")
    vertical_nodes = read_JSON(FOLDER_PATH, 'vertical_location.json')
    list_list_location = []
    for applicationType in applicationTypes:
        nodes = vertical_nodes[applicationType]
        nodes = [node[-7:-3] for node in nodes]
        list_list_location.append(nodes)

    # print(list_list_location)

    intersection_location = set(list_list_location[0]).intersection(*list_list_location[1:])
    intersection_location = list(intersection_location)
    print(intersection_location)
    return jsonify(intersection_location)


# localhost:8050/api/sensor/intersection/verticals?applicationType=AQ,SR-OC,SR-QA,SR-AC&location=KH03
@app.route('/api/sensor/intersection/nodes', methods=['GET'])
@cross_origin()
def get_location_vise_nodes():
    applicationTypes = request.args.get('applicationType')
    location = request.args.get('location')
    applicationTypes = applicationTypes.split(",")
    vertical_nodes = read_JSON(FOLDER_PATH, 'vertical_location.json')

    all_location_nodes = []
    for applicationType in applicationTypes:
        nodes = vertical_nodes[applicationType]
        for node in nodes:
            if node.startswith(location) or applicationType == 'SR-OC' and node.startswith('GW-' + location):
                val = {}
                option = f"Type : {applicationType}, Location : {location}, Node : {node[-2:]}"
                sensorType = applicationType
                option_node = location+"-"+node[-2:]
                val['text']=option
                val['sensorType']=applicationType
                val['node']=option_node
                all_location_nodes.append(val)

    # print(all_location_nodes)
    return jsonify(all_location_nodes)


# SENSOR LISTING APIS
@app.route('/api/platform/sensor/types', methods=['GET'])
@cross_origin()
def get_all_sensor_types():
    verticals = read_JSON(FOLDER_PATH, 'vertical_partition.json')
    vertical_list = list(verticals.keys())
    return jsonify(vertical_list)


@app.route('/api/platform/sensor/nodes/<sensor_type>', methods=['GET'])
@cross_origin()
def get_all_nodes_of_sensor_types(sensor_type):
    vertical_location = read_JSON(FOLDER_PATH, 'vertical_location.json')
    locations = vertical_location[sensor_type]
    locations = filter_location(sensor_type, locations)
    return jsonify(locations)


@app.route('/api/platform/sensor/data/<sensor_type>/<location>', methods=['GET'])
@cross_origin()
def get_latest_sensor_data(sensor_type, location):
    if sensor_type == 'SR-OC':
        location = 'GW-' + location
    node_partition = read_JSON(FOLDER_PATH, 'node_partition.json')
    location_node = read_JSON(FOLDER_PATH, 'location_node.json')
    verticals_JSON = read_JSON(FOLDER_PATH, 'verticals.json')
    nodename = sensor_type + "-" + location

    topic_name = node_partition[nodename]['topic-name']
    partition_number = int(node_partition[nodename]['partition-number'])
    latest_data = get_latest_node_data(topic_name, partition_number)
    latest_data = json.loads(latest_data.decode('utf-8'))
    return latest_data


# LOCATION VALIDATION AND SENSOR BINDING API
@app.route('/api/sensor/validate', methods=['POST'])
@cross_origin()
def validate_binding():
    request_body = request.get_json()
    # entered by the user
    location = request_body['location']
    vertical = request_body['application-type']
    sensors = request_body['sensors']
    node = vertical + '-' + location
    location_node = read_JSON(FOLDER_PATH, 'location_node.json')
    verticals_JSON = read_JSON(FOLDER_PATH, 'verticals.json')
    print(node)
    print_JSON(location_node[location])
    try:
        if node in location_node[location]:
            for sensor in sensors:
                if sensor not in verticals_JSON[vertical]:
                    print('senor not present')
                    return jsonify({'statusCode': '400', 'message': "This location does not have this sensor"})
            return jsonify({'statusCode': '200', 'message': 'Validated and sensor binded'})
        else:
            print('wrong node')
            return jsonify({'statusCode': '400', 'message': "This location does not have this sensor"})
    except Exception as e:
        print("Exception occured ", e)
        abort(400, 'Some exception occurred')


# SENSOR DATA APIs
@app.route('/api/sensor/data/latest/<location>/<vertical>', methods=['GET'])
@cross_origin()
def node_data(location, vertical):
    if vertical == 'SR-OC':
        vertical = vertical+'-GW'
    nodename = vertical + '-' + location
    nodes = read_JSON(FOLDER_PATH, 'nodes.json')
    node_partition = read_JSON(FOLDER_PATH, 'node_partition.json')
    try:
        if nodename in nodes:
            n_last = request.args.get('last')
            sensor_type = request.args.get('sensor')
            topic_name = node_partition[nodename]['topic-name']
            partition_number = int(node_partition[nodename]['partition-number'])
            if n_last:
                # fetches last n data
                latest_data = get_latest_n_node_data(topic_name, partition_number, int(n_last))
                latest_data = json.loads(latest_data)
                if sensor_type:
                    sensor_type = sensor_type.split(",")
                    # final_data = [{sensor_type:data[sensor_type]} for data in latest_data]
                    final_data = []
                    for data in latest_data:
                        final_dict = {}
                        for sensor in sensor_type:
                            final_dict[sensor] = data[sensor]
                        final_data.append(final_dict)

                    return jsonify(final_data)
                else:
                    return jsonify(latest_data)
            else:
                # fetches latest data
                latest_data = get_latest_node_data(topic_name, partition_number)
                if sensor_type:
                    latest_data = json.loads(latest_data.decode('utf-8'))
                    return jsonify({sensor_type: latest_data[sensor_type]})
                else:
                    return json.loads(latest_data.decode('utf-8'))
        else:
            return json.dumps({'statusCode': '400', 'message': 'node does not exist'})
    except Exception as e:
        print("Exception occurred ", e)
        return json.dumps({'statusCode': '400', 'message': 'some exception occurred'})


@app.route("/home", methods=['GET'])
@cross_origin()
def home():
    return "Hi, this is Sensor manager"


@app.route("/health", methods=['GET'])
@cross_origin()
def health():
    logger.info("Health Checked")
    return "Ok"


@app.route("/get_logs", methods=['GET'])
@cross_origin()
def get_logs():
    logs = ""
    with open("/logs/sensormgr_logs.log", "r") as log_file:
        for line in (log_file.readlines()[-10:]):
            logs += line

    print(logs)
    return {"logs": logs}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False, threaded=True)
