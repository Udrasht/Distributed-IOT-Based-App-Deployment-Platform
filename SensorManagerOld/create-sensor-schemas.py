import json
import psycopg2


def read_node_JSON():
    with open('./SensorManager/config.json', 'r') as f:
        data = json.load(f)
    return data

def read_db_config():
    with open('./Resources/Config/db_config.json','r') as f:
        conn_json = json.load(f)
    return conn_json


# establish connection
conn_details = read_db_config()

conn = psycopg2.connect(
        host=conn_details["host"],
        port=conn_details["port"],
        database='SensorManager',
        user=conn_details["uid"],
        password=conn_details["pwd"]
    )

# Create a cursor object
cur = conn.cursor()

def create_schema_for_sensor(sensor_type):
    print("creating schma for",sensor_type)
    
    # Define your table schema
    table_schema = f'''
CREATE TABLE IF NOT EXISTS {sensor_type} (
    sensor_id INT NOT NULL,
    nodename VARCHAR(50) NOT NULL,
    eopch_time BIGINT NOT NULL,
    occupancy_state INT NOT NULL,
    sensor_data BIGINT NOT NULL,
    PRIMARY KEY (sensor_id,nodename)
);
'''

    # Execute the schema to create the table
    cur.execute(table_schema)

    # Commit the transaction
    conn.commit()



sensor_types = read_node_JSON()['sensor-type']

for sensor_type in sensor_types:
    create_schema_for_sensor(sensor_type)


# Close the cursor and connection
cur.close()
conn.close()