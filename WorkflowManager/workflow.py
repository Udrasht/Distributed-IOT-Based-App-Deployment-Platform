import requests
import json
from flask import request, jsonify


result=[]


def read_JSON(file_name):
    with open(file_name, 'r') as f:
            data = json.load(f)
    return data

def get_api_data(application_entity,sensorType):
    app_json = read_JSON('./app.json')
    location = app_json['location']
    # application_entity = app_json['applicationType']
    # sensorType = app_json['sensorTypes']
    # sensorType=",".join(sensorType)
    respone = requests.get('http://20.21.102.175:2041/api/sensor/data/latest/'+location+'/'+application_entity+'?last=1&sensor='+sensorType)
    respone = respone.json()
    print(respone[0])
    return jsonify(respone[0])


def collect_data(location,vertical):
    #collect data
    request_string="https://api/sensor/data/latest/"+location+"/"+vertical
    response = requests.get(request_string)
    data = response.json()
    return jsonify(data)

def check_min_limit(data,limit):
    #check min limit
    if data < limit:
        result[1]=1

def check_max_limit(data,limit):
    #check max limit
    result[2]=1

def print_result(result):
    print(result)
    #print result

# def send_notification():
#     #send notification




