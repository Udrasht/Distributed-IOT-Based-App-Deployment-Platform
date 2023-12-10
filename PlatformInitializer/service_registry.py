from kazoo.client import KazooClient


def register_service(service_name, ip, port):
    zk = KazooClient(hosts='20.196.205.46:2181')
    zk.start()
    if zk.exists(f"/services/{service_name}") is not None:
        zk.delete(f'/services/{service_name}', recursive=True)

    zk.ensure_path(f"/services/{service_name}")
    my_byte_string = f"{ip}:{port}".encode('utf-8')
    zk.create(f"/services/{service_name}/instance1", my_byte_string)

    zk.stop()


def unregister_service():
    zk = KazooClient(hosts='20.196.205.46:2181')
    zk.start()
    zk.delete('/services', recursive=True)
    zk.stop()


def get_all_service_registry():
    zk = KazooClient(hosts='20.196.205.46:2181')
    zk.start()

    # Get all the services registered in ZooKeeper under /services
    services = zk.get_children('/services')
    details = []

    # Iterate over each service and get the IP and port information for each instance
    for service in services:
        instances = zk.get_children(f'/services/{service}')
        for instance in instances:
            instance_data, _ = zk.get(f'/services/{service}/{instance}')
            ip, port = instance_data.decode('utf-8').split(':')
            res = {"service": service, "ip": ip, "port": port}
            details.append(res)

    zk.stop()
    return details


def get_all_app_registry():
    zk = KazooClient(hosts='20.196.205.46:2181')
    zk.start()

    # Get all the services registered in ZooKeeper under /services
    apps = zk.get_children('/apps')
    details = []

    # Iterate over each service and get the IP and port information for each instance
    for app in apps:
        instances = zk.get_children(f'/apps/{app}')
        for instance in instances:
            instance_data, _ = zk.get(f'/apps/{app}/{instance}')
            ip, port = instance_data.decode('utf-8').split(':')
            res = {"app": app, "ip": ip, "port": port}
            details.append(res)

    zk.stop()
    return details


def get_all_iot_registry():
    zk = KazooClient(hosts='20.196.205.46:2181')
    zk.start()

    # Get all the services registered in ZooKeeper under /services
    iotnodes = zk.get_children('/iotnodes')
    details = []

    # Iterate over each service and get the IP and port information for each instance
    for iotnode in iotnodes:
        instances = zk.get_children(f'/iotnodes/{iotnode}')
        for instance in instances:
            instance_data, _ = zk.get(f'/iotnodes/{iotnode}/{instance}')
            ip, port = instance_data.decode('utf-8').split(':')
            res = {"iotnode": iotnode, "ip": ip, "port": port}
            details.append(res)

    zk.stop()
    return details
