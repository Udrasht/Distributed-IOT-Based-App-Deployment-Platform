import os
import json
import subprocess
import re
import time
import requests
from logger import logger


class LoadBalancer:

    @staticmethod
    def __getAppAndVmDetails__(appName: str):
        with open('AppDetails.json') as json_file:
            apps = json.load(json_file)
        appDict, vmDict = None, None
        for app in apps:
            if app["appName"] == appName:
                appDict = app
                break
        with open('VmDetails.json') as json_file:
            vms = json.load(json_file)

        for vm in vms:
            if vm["vm_name"] == appDict["hostVm"]:
                vmDict = vm
                break

        return appDict, vmDict

    @staticmethod
    def __getDictFromJson__(filename: str, keyId: str, valId: str):
        with open(filename) as json_file:
            dicts = json.load(json_file)

        for d in dicts:
            if d[keyId] == valId:
                return d

    @staticmethod
    def __updateJson__(fileName, keyId, valId, updateKey, newVal, method="overwrite"):
        """
        LoadBalancer.__updateJson__("AppDetails.json", "appName", appName, "instances", instances + 1)
        In AppDetails.json where appName == appName, update key instances value to (instances + 1)
        """
        if method == 'empty':
            with open(fileName, 'w') as json_file:
                json.dump([], json_file, indent=4)
            return


        with open(fileName) as json_file:
            dicts = json.load(json_file)

        if method == 'addDict':
            dicts.append(newVal)
            with open(fileName, 'w') as json_file:
                json.dump(dicts, json_file, indent=4)
            return


        for d in dicts:
            if d[keyId] == valId:
                if method == "overwrite":
                    d[updateKey] = newVal
                    break
                elif method == "append":
                    d[updateKey].append(newVal)
                elif method == "addKey":
                    d[updateKey] = newVal
                elif method == "removeDict":
                    dicts.remove(d)
                elif method == 'pop':
                    d[updateKey].remove(newVal)
                else:
                    raise Exception("invalid update method provided in updateJson!")
                break

        with open(fileName, 'w') as json_file:
            json.dump(dicts, json_file, indent=4)

    @staticmethod
    def addReplica(appName: str, lbVmName: str):
        """
         Go to the VM on which app is hosted
         Create container for that app, add the container id in AppDetails.json
         Update the config file for the app in lbVm
         :param appName: Name of the app whose replica is to be created
         :param lbVmName: Name of VM on which load balancer is running
         :return:
         """

        app, appHostVm = LoadBalancer.__getAppAndVmDetails__(appName)

        commandDocker = f"""sudo docker run --name {appName}_instance_{app["instances"] + 1} -d -p {appHostVm["latestAvailablePort"]}:{app["containerPort"]} {app["imageName"]} && sudo docker ps -l -q """
        commandConnect = f"""ssh -o StrictHostKeyChecking=no -i {appHostVm["vm_key_path"]} {appHostVm["vm_username"]}@{appHostVm["vm_ip"]} """

        result = subprocess.run(
            f"""{commandConnect} {commandDocker} """.split(),
            stdout=subprocess.PIPE)

        output = result.stdout.decode('utf-8')
        replicaContId = output.split()[1]

        LoadBalancer.__updateNginxConfig__(appName, lbVmName, appHostVm["latestAvailablePort"])

        LoadBalancer.__updateJson__('AppDetails.json', "appName", appName, "instances", app["instances"] + 1)
        LoadBalancer.__updateJson__('AppDetails.json', "appName", appName, "containerIds", replicaContId, "append")
        LoadBalancer.__updateJson__('AppDetails.json', "appName", appName, "hostPorts",
                                    appHostVm["latestAvailablePort"],
                                    "append")
        LoadBalancer.__updateJson__('VmDetails.json', "vm_name", appHostVm["vm_name"], "latestAvailablePort",
                                    appHostVm["latestAvailablePort"] + 1)
        logger.info(f"Replica of {appName} created!")

    @staticmethod
    def __updateNginxConfig__(appName: str, lbVmName: str, hostPort: int):
        """
        The method assumes that the confing file in /etc/nginx/conf.d of the lbVm and is named as appName.conf
        Go to the config file location and read the file into a string
        Append server hostVmIp:hostPort; in upstream part of the string
        delete the config file on the server
        Create the config file on the server with the same name and updated contents
        :param appName: Name of the app whose replica has been created
        :param lbVmName: Name of VM on which load balancer is running
        :param hostPort: Port of the VM on which the replica was just created
        """

        # Note that I am reading a file which will be updated immediately after this method gets executed
        app, appHostVm = LoadBalancer.__getAppAndVmDetails__(appName)
        lbVm = LoadBalancer.__getDictFromJson__('VmDetails.json', "vm_name", lbVmName)

        commandConnect = f'''ssh -o StrictHostKeyChecking=no -i {lbVm["vm_key_path"]} {lbVm["vm_username"]}@{lbVm["vm_ip"]}'''
        commandReadConfig = f'''cd /etc/nginx/conf.d && cat {appName}.conf'''

        result = subprocess.run(f'{commandConnect} {commandReadConfig}'.split(), stdout=subprocess.PIPE)
        configData = result.stdout.decode('utf-8')
        upstreamEndIndex = configData.find('}')
        updatedConfigData = f'''{configData[:upstreamEndIndex]}\n    server {appHostVm["vm_ip"]}:{hostPort};\n{configData[upstreamEndIndex:]} '''

        commandEmptyConfig = f'''cd /etc/nginx/conf.d && sudo rm {appName}.conf && sudo touch {appName}.conf'''
        commandUpdateConfig = f"""
cd /etc/nginx/conf.d
sudo touch {appName}.conf
sudo tee {appName}.conf > /dev/null << EOF
{updatedConfigData} 
EOF
sudo nginx -s reload

        """
        os.system(f'''{commandConnect} "{commandEmptyConfig}; {commandUpdateConfig}"''')
        logger.info(f"Added replica to config file of {appName}.config")

    @staticmethod
    def registerApp(appName: str, imageName: str, vmIp: str, containerPort: int, hostPort: int, containerId: str,
                    lbVmName: str):
        """
        When deployment manager deploys the app, it should send the above information to the load balancer.
        Load balance will then register the original instance of the app by updating its jsons
        :param vmIp: The ip of the vm on which the app has been deployed
        :param containerId: ID of the container in which original instance of the app is running
        :param appName: Name of the application. This will also be the name of .conf file in /etc/nginx/conf.d
        :param imageName: The name of the image which was used in docker run command to make the container for the app
        :param containerPort: The port on which the app is listening inside the container
        :param hostPort: The port of the host VM
        :param lbVmName: This is the name of VM on which load balancer is running
        :return: End point of the application
        """

        vm = LoadBalancer.__getDictFromJson__("VmDetails.json", 'vm_ip', vmIp)
        hostVm = vm['vm_name']
        newApp = {
            "appName": appName,
            "imageName": imageName,
            "hostVm": hostVm,
            "instances": 1,
            "containerPort": containerPort,
            "hostPorts": [hostPort],
            "nginxPort": 0,
            "containerIds": [containerId]
        }
        # logic to see if a same name app is being redeployed
        LoadBalancer.__updateJson__('AppDetails.json', 'appName', appName, None, None, "removeDict")
        try:
            LoadBalancer.__updateJson__('VmDetails.json', 'vm_name', hostVm, 'hosted_apps', appName, 'pop')
        except:
            pass

        with open("./AppDetails.json") as file:
            apps = json.load(file)

        apps.append(newApp)

        with open("AppDetails.json", 'w') as json_file:
            json.dump(apps, json_file, indent=4)

        # Add this app in hosted_apps in VmDetails.json
        LoadBalancer.__updateJson__("VmDetails.json", "vm_name", hostVm, "hosted_apps", appName, "append")

        # make a config file in nginx conf.d
        LoadBalancer.__addNginxConfigFile__(appName, lbVmName)

        logger.info(f"Successfully registered {appName}")
        lbVm = LoadBalancer.__getDictFromJson__('VmDetails.json', "vm_name", lbVmName)
        appUpdatedDict = LoadBalancer.__getDictFromJson__("AppDetails.json", "appName", appName)
        LoadBalancer.__updateJson__('AppDetails.json', "appName", appName, "endpoint",
                                    f'http://{lbVm["vm_ip"]}:{appUpdatedDict["nginxPort"]}', 'addKey')

        logger.info(f'Endpoint of {appName} -> http://{lbVm["vm_ip"]}:{appUpdatedDict["nginxPort"]}')
        return f'{lbVm["vm_ip"]}:{appUpdatedDict["nginxPort"]}'

    @staticmethod
    def __addNginxConfigFile__(appName: str, lbVmName: str):
        """
        This method creates a appName.conf file in /etc/nginx/conf.d
        :param appName: Name of app which was registered
        """

        app, appHostVm = LoadBalancer.__getAppAndVmDetails__(appName)
        lbVm = LoadBalancer.__getDictFromJson__('VmDetails.json', "vm_name", lbVmName)

        with open('NginxPort.json') as json_file:
            nginxport = json.load(json_file)

        configData = f"""
upstream {app["appName"]}_servers{{
    #server 20.173.88.38:7200;
    server {appHostVm["vm_ip"]}:{app["hostPorts"][0]};
}}

server {{
    listen 0.0.0.0:{nginxport[0]["latestAvailablePort"]};  

    location / {{
        proxy_pass http://{app["appName"]}_servers/;
    }}
}}

"""
        createConfig = f"""
ssh -o StrictHostKeyChecking=no -i {lbVm["vm_key_path"]} {lbVm["vm_username"]}@{lbVm["vm_ip"]} "
cd /etc/nginx/conf.d
sudo touch {appName}.conf
sudo tee {appName}.conf > /dev/null << EOF
{configData} 
EOF
sudo nginx -s reload
"

"""
        os.system(createConfig)
        LoadBalancer.__updateJson__("AppDetails.json", "appName", appName, "nginxPort",
                                    nginxport[0]["latestAvailablePort"])
        LoadBalancer.__updateJson__("NginxPort.json", "id", "default", "latestAvailablePort",
                                    nginxport[0]["latestAvailablePort"] + 1)
        logger.info(f"{appName}.conf created")

    @staticmethod
    def __getContainerRamUsage__(vm: dict, containerId: str):
        """
        :param vm: Dict containing complete details of the VM on which container is deployed
        :param containerId: id of the container whose RAM usage is to be found
        :return: Percentage of RAM currently under use
        """
        commandConnect = f'''ssh -o StrictHostKeyChecking=no -i {vm["vm_key_path"]} {vm["vm_username"]}@{vm["vm_ip"]}'''
        commandDocker = f'''sudo docker container stats --no-stream {containerId} --format {{{{.MemUsage}}}}'''
        output = subprocess.check_output(f'{commandConnect} {commandDocker}'.split())
        # output.decode.strip is like "40.55MiB / 906MiB"
        # output.decode.strip.split is like ['40.55MiB ', ' 906MiB']
        currMemUsage, totMemAvail = output.decode().strip().split("/")

        currMemUsage = float(re.sub("[^0-9.]", "", currMemUsage))
        totMemAvail = float(re.sub("[^0-9.]", "", totMemAvail))
        return currMemUsage / totMemAvail * 100

    @staticmethod
    def __getContainerCpuUsage__(vm: dict, containerId: str):
        """
        :param vm: Dict containing complete details of the VM on which container is deployed
        :param containerId:  id of the container whose CPU usage is to be found
        :return: Percentage of CPU currently under use
        """

        commandConnect = f'''ssh -o StrictHostKeyChecking=no -i {vm["vm_key_path"]} {vm["vm_username"]}@{vm["vm_ip"]}'''
        commandDocker = f'''sudo docker container stats --no-stream {containerId} --format "{{{{.CPUPerc}}}}"'''
        output = subprocess.check_output(f'{commandConnect} {commandDocker}'.split())
        cpuPercentage = re.sub("[^0-9.]", "", output.decode())
        return float(cpuPercentage)

    @staticmethod
    def __balanceOnce__(lbVmName):
        LoadBalancer.__updateJson__('AppHealth.json', None, None, None, None, 'empty')

        with open('AppDetails.json') as json_file:
            allApps = json.load(json_file)

        for app in allApps:
            logger.info(f"checking load on {app['appName']}")
            appHostVm = LoadBalancer.__getDictFromJson__('VmDetails.json', 'vm_name', app["hostVm"])
            entry = {'appName': f'{app["appName"]}', 'stats': []}
            LoadBalancer.__updateJson__('AppHealth.json', None, None, None, entry, 'addDict')

            for container in app["containerIds"]:
                try:
                    ramUsage = LoadBalancer.__getContainerRamUsage__(appHostVm, container)
                    cpuUsage = LoadBalancer.__getContainerCpuUsage__(appHostVm, container)

                    if ramUsage > 75 or cpuUsage > 80:
                        healthInfo = f'{app["appName"]}, container - {container} is unhealthy; RAM utilization = {ramUsage}% ; CPU utilization = {cpuUsage}% '
                        logger.info(healthInfo)
                        LoadBalancer.__updateJson__('AppHealth.json', 'appName', app['appName'], 'stats', healthInfo, 'append')
                        logger.info('creating replica')
                        LoadBalancer.addReplica(app["appName"], lbVmName)
                        break  # don't create a new container for every unhealthy container. Just create one. If needed
                        # create one more in the next round
                    else:
                        healthInfo = f'{app["appName"]}, container - {container} is healthy; RAM utilization = {ramUsage}% ; CPU utilization = {cpuUsage}%'
                        logger.info(healthInfo)
                        LoadBalancer.__updateJson__('AppHealth.json', 'appName', app['appName'], 'stats', healthInfo,
                                                    'append')
                except:
                    logger.info("Exception encountered while load balancing, possible causes - container deleted, etc")

    @staticmethod
    def balance(lbVmName):
        while True:
            LoadBalancer.__balanceOnce__(lbVmName)
            time.sleep(100)

    @staticmethod
    def __heartBeatOnce__():

        with open('AppDetails.json') as json_file:
            allApps = json.load(json_file)

        for app in allApps:
            response = requests.get(f'{app["endpoint"]}/heartbeat')
            if response.status_code == 200:
                logger.info(f'{app["appName"]} is alive!')
            else:
                logger.info(f'{app["appName"]} is dead!')
                logger.info("Failed with status code:", response.status_code)
            time.sleep(50)

    @staticmethod
    def listenHeartbeat():
        temCounter = 0
        while True:
            LoadBalancer.__heartBeatOnce__()
            time.sleep(5)
            temCounter += 1
            if temCounter == 4:
                break

    @staticmethod
    def __removeNginxEntry(appName, lbVmName: str):
        """
        This methods removes the config files created for appName.conf application
        :param appName: The app to be deleted
        :param lbVmName: Name of the VM on which load balancer is running
        :return: None
        """
        lbVm = LoadBalancer.__getDictFromJson__('VmDetails.json', 'vm_name', lbVmName)
        nginxPath = '/etc/nginx'
        commandConnect = f'ssh -o StrictHostKeyChecking=no -i {lbVm["vm_key_path"]} {lbVm["vm_username"]}@{lbVm["vm_ip"]}'
        commandRemove = f'cd {nginxPath}/conf.d; sudo rm {appName}.conf;'
        commandRestart = 'sudo nginx -s reload;'
        os.system(f'''{commandConnect} "{commandRemove} {commandRestart}"''')
        logger.info(f"Removed config of {appName}")

    @staticmethod
    def deregisterApp(appName: str):
        """
        This method will be called to remove a deployed app from the platform.
        The methods assumes that appName is present in AppDetails.json, ie, the app is actually running on the VM.
        No checks have been added if a app that is not in the VM is being deregistered
        :param appName: The name of the app to be removed
        :return: None
        """
        app, vm = LoadBalancer.__getAppAndVmDetails__(appName)
        commandConnect = f'ssh -o StrictHostKeyChecking=no -i {vm["vm_key_path"]} {vm["vm_username"]}@{vm["vm_ip"]}'

        # delete all app containers
        for container in app['containerIds']:
            commandDeleteContainer = f'sudo docker rm -f {container}'
            os.system(f'''{commandConnect} "{commandDeleteContainer}"''')
        logger.info(f"Deleted all containers of {appName}")

        # delete the app's docker image
        commandDeleteImage = f'''sudo docker image rm {app["imageName"]}'''
        os.system(f'{commandConnect} "{commandDeleteImage}"')
        logger.info(f"Deleted the image of {appName}")

        # update the jsons
        LoadBalancer.__updateJson__('AppDetails.json', 'appName', appName, None, None, 'removeDict')
        LoadBalancer.__updateJson__('VmDetails.json', 'vm_name', app['hostVm'], 'hosted_apps', appName, 'pop')

        # remove nginx entry and restart nginx
        LoadBalancer.__removeNginxEntry(appName, "VM1")

        logger.info(f'{appName} successfully deregistered!')




