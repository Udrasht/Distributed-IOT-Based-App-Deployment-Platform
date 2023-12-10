import json
from json_utilities import *

def write_all_sensors(verticals):
    unique_sensors=[]
    for application_entity in verticals:
        sensor_types = verticals[application_entity]
        unique_sensors.extend(sensor_types)
    
    unique_sensors = set(unique_sensors)
    unique_sensors.discard('Timestamp')
    unique_sensors = list(unique_sensors)
    write_JSON(FOLDER_PATH,'unique_sensors.json',unique_sensors)

verticals = read_JSON(FOLDER_PATH,'verticals.json')
write_all_sensors(verticals)
