
import requests
import json
from flask import Flask,request,jsonify
from flask_cors import cross_origin

app = Flask(__name__)

def read_JSON(file_name):
    with open(file_name,'r') as f:
        data = json.load(f)
    return data


def collect_data(): 
    app_json = read_JSON('./app.json')
    location = app_json['location']
    application_entity = app_json['applicationType']
    sensorType = app_json['sensor Types']
    respone = requests.get('http://20.21.182.175:2041/api/sensor/data/latest/'+location+'/'+application_entity+'?last=1&sensor='+sensorType).json()
    print(respone[0])
    return jsonify(respone[0][sensorType])
	
def check_min_limit(data,limit): 
    if data < limit: 
        return 1 
    else: return 0 
	
def send_notification(limit_status):
    if limit_status:
        send_email = requests.post("").json()
        return jsonify(send_email)
	

@app.route("/",methods=['GET'])
@cross_origin()
def index():
	data=collect_data()
	limit_status = check_min_limit(data,2)
	send_notification(limit_status)




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
    