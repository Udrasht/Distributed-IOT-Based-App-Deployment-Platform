import json
FOLDER_PATH="./sensor_json/"

def print_JSON(json_dict):
    print(json.dumps(json_dict,indent=4))

def read_JSON(path,file_name):
    with open(path+file_name, 'r') as f:
            data = json.load(f)
    return data

def write_JSON(path,file_name,json_object):
     with open(path+file_name, "w") as file:
        json.dump(json_object, file)