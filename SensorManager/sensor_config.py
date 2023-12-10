import os
os.system('python3 SensorMgr/sensor_config/create_verticals_json.py')
os.system('python3 SensorMgr/sensor_config/create_node_json.py')
os.system('python3 SensorMgr/sensor_config/create_node_partition_mapping.py')
os.system('python3 SensorMgr/sensor_config/create_unique_sensors_json.py')
os.system('python3 SensorMgr/sensor_config/save_channel_format.py')