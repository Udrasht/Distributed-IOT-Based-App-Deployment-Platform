import os
import json
from flask import Flask
from flask_cors import cross_origin
from flask import request
import threading
from LoadBalancer import LoadBalancer
from logger import logger

app = Flask(__name__)

loadBalancerIp = "20.21.102.175"
nginxPath = "/etc/nginx"

os.system("chmod 600 ./VM-keys/VM1_key.cer")
os.system("chmod 600 ./VM-keys/VM2_key.cer")
os.system("chmod 600 ./VM-keys/VM3_key.cer")


@app.route("/home", methods=['GET'])
@cross_origin()
def home():
    return "Hi, this is Load Balancer"


@app.route("/health", methods=['GET'])
@cross_origin()
def health():
    logger.info("Health Checked")
    return "Ok"


@app.route("/get_logs", methods=['GET'])
@cross_origin()
def get_logs():
    logs = ""
    with open("../../logs/lb_logs.log", "r") as log_file:
        for line in (log_file.readlines()[-100:]):
            logs += line

    print(logs)
    return {"logs": logs}


@app.route("/registerApp", methods=['GET'])
@cross_origin()
def registerApp():
    """
    The name of first (original) container of the app should preferably be appName_instance_1. Not following this in
    no way affect the functioning of the code
    """
    appName = request.args.get("appName")
    imageName = request.args.get("imageName")
    vmIp = request.args.get("vmIp")
    containerPort = request.args.get("containerPort")
    hostPort = request.args.get("hostPort")
    containerId = request.args.get("containerId")

    lbb = LoadBalancer()
    return lbb.registerApp(appName, imageName, vmIp, int(containerPort), int(hostPort), containerId, "VM1")


@app.route("/deregisterApp", methods=['GET'])
@cross_origin()
def deregisterApp():
    appName = request.args.get("appName")
    lbb = LoadBalancer()
    try:
        lbb.deregisterApp(appName)
    except Exception as e:
        logger.error(str(e))
        return f'{appName} deregistration failed, it has probably been deregistered already!'
    return f'{appName} has been deregistered successfully!'


@app.route("/getVmDetails", methods=['GET'])
@cross_origin()
def getVmDetails():
    with open('VmDetails.json') as json_file:
        dicts = json.load(json_file)

    return dicts


@app.route("/getAppsDetails", methods=['GET'])
@cross_origin()
def getAppsDetails():
    with open('AppDetails.json') as json_file:
        appDetailsDict = json.load(json_file)

    return appDetailsDict


@app.route("/getAppsHealth", methods=['GET'])
@cross_origin()
def getAppsHealth():
    with open('AppHealth.json') as json_file:
        appHealthDict = json.load(json_file)

    return appHealthDict


if __name__ == "__main__":
    lb = LoadBalancer()
    thread = threading.Thread(target=lb.balance, args=("VM1",))
    thread.start()
    app.run(host='0.0.0.0', port=8050, debug=True, threaded=True, use_reloader=False)
    thread.join()
