import psycopg2
import pandas as pd
import json


def sql_file_runner(sql_file):

    with open('../Resources/Config/db_config.json', 'r') as f:
        conn_json = json.load(f)

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=conn_json["host"],
        port=conn_json["port"],
        database=conn_json["db"],
        user=conn_json["uid"],
        password=conn_json["pwd"]
    )

    # Open the SQL file and read its contents
    with open(sql_file, 'r') as f:
        sql = f.read()

    # Create a cursor object to execute SQL queries
    cur = conn.cursor()

    # Execute the SQL query
    cur.execute(sql)

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and database connection
    cur.close()
    conn.close()


def sql_query_runner(sql_query):

    with open('../Resources/Config/db_config.json', 'r') as f:
        conn_json = json.load(f)

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=conn_json["host"],
        port=conn_json["port"],
        database=conn_json["db"],
        user=conn_json["uid"],
        password=conn_json["pwd"]
    )

    if sql_query.startswith("SELECT"):
        # Execute an SQL query and get the results in a DataFrame
        df = pd.read_sql_query(sql_query, conn)

        conn.close()
        return df

    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()
    cursor.close()
    # Close the database connection
    conn.close()
