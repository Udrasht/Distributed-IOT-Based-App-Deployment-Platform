import psycopg2
import json
import re
from json_utilities import *

def read_columns_name(values):
    # Access the column names for the table and make the string of column names for create query table    
    columns='id SERIAL,node_name VARCHAR(50), description VARCHAR(150),'
    if isinstance(values, list):
        for value in values:
            value = value.replace("-","_")
            value = value.replace(" ","_")
            value = value.replace(".","$")
            if re.match(r'^\d', value):
                value ='_'+value
            columns=columns+value+' VARCHAR(50),'
    columns = columns + " PRIMARY KEY (node_name,timestamp)"
    return columns

#create table with name =table_name and colums=comums
def create_table(table_name,columns,cur):

    #first check if same table name exist or not
    cur.execute(f"SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{table_name}')")
    table_exists = cur.fetchone()[0]

    if not table_exists:
        create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        # print(create_query)
        # print()
        cur.execute(create_query)
        conn.commit()
        print(f"{table_name} table created.")
    else:
        print(f"{table_name} table already exists.")
    
#read JSON file
verticals = read_JSON(FOLDER_PATH,'verticals.json')
# print_JSON(verticals)
# read the config file
conn_json=read_JSON(FOLDER_PATH,'db_config.json')
print(conn_json)
# Establish a connection to the local PostgreSQL instance
conn = psycopg2.connect(
    host=conn_json["host"],
    port=conn_json["port"],
    database="SensorManager",
    user=conn_json["uid"],
    password=conn_json["pwd"]
)
cur = conn.cursor()

# # iterate over json file to create all the table
for key, values in verticals.items():
    table_name=key
    table_name=table_name.replace("-", "_")
    
    
    columns=read_columns_name(values)
    create_table(table_name,columns,cur)

cur.close()
conn.close()

