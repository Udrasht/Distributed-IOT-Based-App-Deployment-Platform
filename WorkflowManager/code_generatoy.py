app_json={
	"applicationName": "finalSampleApp1",
	"sensorTypes": {
		"AQ": [
			"AQI",
			"PM10",
			"AQL"
		],
		"SR-AQ": [
			"Temperature",
			"CO2",
			"Relative Humidity"
		],
		"SR-AC": [
			"Gas Total Power"
		]
	},
	"location": "KH00-00",
	"userEmail": "hkashyap0809@gmail.com",
	"applicationTypes": [
		"AQ",
		"SR-AQ",
		"SR-AC"
	],
	"applicationTypeInstance": {
		"AQ": 3,
		"SR-AQ": 3,
		"SR-AC": 1
	},
	"workflow": {
		"checkpoint1": {
			"service": "service1",
            "attribute":"data"
		},
		"checkpoint2": {
			"service": "service2",
			"limit": 2,
		},
		"checkpoint3": {
			"service": "service4",
		}
	},
	"applicationDescription": "finalSampleApp1"
}
collect_data_function = f"""
def collect_data(): 
    app_json = read_JSON('./app.json')
    location = app_json['location']
    application_entity = app_json['applicationType']
    sensorType = app_json['sensor Types']
    respone = requests.get('http://20.21.182.175:2041/api/sensor/data/latest/'+location+'/'+application_entity+'?last=1&sensor='+sensorType).json()
    print(respone[0])
    return jsonify(respone[0][sensorType])
"""

check_min_limit_function = f"""
def check_min_limit(data,limit): 
    if data < limit: 
        return 1 
    else: return 0 
"""

check_max_limit_function = f"""
def check_max_limit(data,limit): 
    if data > limit: 
        return 1 
    else: return 0 
"""

send_notification_function = f"""
def send_notification(data,limit_status):
    if limit_status:
        app_json = read_JSON('./app.json')
        {{ payload={{}} }}
        payload['receiver-email'] = app_json['userEmail']
        payload['email_body'] = "The data crossed the limit"
        send_email = requests.post("http://localhost:8000/api/triggeremail", json=payload).json()
        return jsonify(send_email)
"""

service_function_mapping={
    "service1" : collect_data_function,
    "service2" : check_min_limit_function,
    "service3" : check_max_limit_function,
    "service4" : send_notification_function,
}

def get_function_call(checkpoint):
    if checkpoint['service'] == 'service1':
        return "data=collect_data()"
    elif checkpoint['service'] == 'service2':
        return f"limit_status = check_min_limit(data,{checkpoint['limit']})"

    elif checkpoint['service'] == 'service3':
        return f"limit_status = check_max_limit(data,{checkpoint['limit']})"
    elif checkpoint['service'] == 'service4':
        return "send_notification(limit_status)"


def generate_code(workflow_details):
    helper_functions=''
    function_call=''

    for checkpoint in workflow_details:
        print("checkpoint", workflow_details[checkpoint])
        helper_functions = helper_functions + service_function_mapping[workflow_details[checkpoint]['service']]+"\t"
        function_call = function_call + "\t"+get_function_call(workflow_details[checkpoint])+"\n"
            

    rpc_code=f'''
import requests
import json
from flask import Flask,request,jsonify
from flask_cors import cross_origin

app = Flask(__name__)

def read_JSON(file_name):
    with open(file_name,'r') as f:
        data = json.load(f)
    return data

{helper_functions}

@app.route("/",methods=['GET'])
@cross_origin()
def index():
{function_call}



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
    '''
    # print(rpc_code)
    with open("./generated_code.py","w") as file: 
        file.write(rpc_code)
    return rpc_code


# {
#  "Application Name": "room",
#  "Application Description": "moni",
#  "checkpoint1": {
#   "block1": {
#     "block":"block1"
#    "applicationtype": "AQ",
#    "sensortype": "CO2"
#   }
#  },
#  "checkpoint2": {
#   "block2": {},
#   "block3": {}
#  },
#  "checkpoint3": {
#   "block5": {}
#  }
# }

# generate_code(app_json)