from pymongo import MongoClient
import certifi
from uuid import uuid4


def get_connection():
    ca = certifi.where()
    # password : ias-iot-avishkar-23
    client = MongoClient("mongodb+srv://hkashyap0809:ias-iot-avishkar-23@sensor-cluster.jzrhdzp.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=ca)
    return client


def create_schema(db,sensor_type):
    collection = db.create_collection(sensor_type)

    schema = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['nodename', 'sensor_data','timestamp','occupancy_state'],
        'properties': {
            'id':{
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'nodename': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'sensor_data': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'timestamp': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'occupancy_state': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            }
        }
        }
    }
    collection.create_index([('id', 1)], unique=True)
    collection.create_index([('nodename', 1)])
    collection.create_index([('timestamp', 1)])
    collection.create_index(schema)


# Set up a connection to MongoDB Atlas

# Connect to a database in MongoDB Atlas
client = get_connection()
db_name = 'sensor-database'
db = client[db_name]






# create_schema(db,'temperature')
# collection = db['temperature']
# doc = [{"id": str(uuid4()), "nodename": "h105", "sensor_data": 234,"timestamp":"3453","occupancy_state":"0"},
#        {"id": str(uuid4()), "nodename": "h205", "sensor_data": 4,"timestamp":"345345","occupancy_state":"0"},
#        {"id": str(uuid4()), "nodename": "obh", "sensor_data": 756,"timestamp":"345345","occupancy_state":"0"},]
# collection.insert_many(doc)