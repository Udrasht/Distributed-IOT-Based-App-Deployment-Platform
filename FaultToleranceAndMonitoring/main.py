import requests
from flask import Flask
from flask_cors import cross_origin
from service_registry import *
from datetime import datetime
from logger import logger

app = Flask(__name__)


@app.route("/home", methods=['GET'])
@cross_origin()
def home():
    logger.info("Successfully initialized")
    return "Hi, this is Fault Tolerance and Monitoring Manager"


@app.route("/health", methods=['GET'])
@cross_origin()
def health():
    logger.info("Health checked")
    return "Ok"


@app.route("/check_health", methods=['GET'])
@cross_origin()
def check_health_services():
    objs = get_all_service_registry()
    ans = []

    for obj in objs:
        s = "http://" + obj["ip"] + ":" + obj["port"] + "/health"
        try:
            res = requests.get(s)
            if res.status_code == 200:
                obj["status"] = "Ok"
            else:
                obj["status"] = "Down"
        except Exception as e:
            obj["status"] = "Down"
            print(e)
        obj["timestamp"] = datetime.now()
        ans.append(obj)

    return ans


@app.route("/get_logs", methods=['GET'])
@cross_origin()
def get_logs():
    logs = ""
    with open("fault_logs.log", "r") as log_file:
        for line in (log_file.readlines()[-10:]):
            logs += line

    print(logs)
    return {"logs": logs}


@app.route("/all_services", methods=["GET"])
@cross_origin()
def all_services():
    res = get_all_service_registry()
    print(res)
    return res


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
