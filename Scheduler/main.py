import datetime
import json
import threading
import time
from uuid import uuid1

from flask import Flask
from flask_cors import cross_origin
from kafka import KafkaProducer, KafkaConsumer

from logger import logger

app = Flask(__name__)

# Configure Kafka producer and consumer
producer = KafkaProducer(
    bootstrap_servers=['20.196.205.46:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,  # Number of times to retry a message in case of failure
    max_in_flight_requests_per_connection=1,  # Ensure only one request is in-flight
    acks='all',  # Wait for all replicas to acknowledge the message
)

consumer = KafkaConsumer("Scheduler", bootstrap_servers=['20.196.205.46:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))


@app.route("/home", methods=['GET'])
@cross_origin()
def home():
    return "Hi, this is Scheduler"


@app.route("/health", methods=['GET'])
@cross_origin()
def health():
    logger.info("Health Checked")
    return "Ok"


@app.route("/get_logs", methods=['GET'])
@cross_origin()
def get_logs():
    logs = ""
    with open("/logs/schd_logs.log", "r") as log_file:
        for line in (log_file.readlines()[-10:]):
            logs += line

    print(logs)
    return {"logs": logs}


requests_m1_c, requests_m1_p = [], []  # For message 1
requests_m2_c, requests_m2_p = [], []  # For message 2
requests_m3_c, requests_m3_p = [], []  # For message 3
lock = threading.Lock()


def start_setup_job(app_name, request_data, start_time, msg_id, requests_c, requests_p):
    logger.info(f"App starting after scheduled time - {app_name}. Start time {str(start_time)}")
    msg = {
        "to_topic": "first_topic",
        "from_topic": "Scheduler",
        "request_id": msg_id,
        "msg": f"its time${app_name}"
    }

    print(msg)

    if send(request_data, msg, requests_c, requests_p) == -1:
        print("Duplicate message!")
        return


def end_setup_job(app_name, request_data, end_time, msg_id, requests_c, requests_p):
    logger.info(f"App ending after scheduled time - {app_name}. End time {str(end_time)}")
    msg = {
        "to_topic": "first_topic",
        "from_topic": "Scheduler",
        "request_id": msg_id,
        "msg": f"its end time${app_name}"
    }

    print(msg)

    if send(request_data, msg, requests_c, requests_p) == -1:
        print("Duplicate message!")
        return


def send(request_data, msg, c_list, p_list):
    request_id = request_data['request_id']

    lock.acquire()
    if request_id in c_list:
        print("Duplicate message!")
        lock.release()
        return -1
    c_list.append(request_id)
    lock.release()

    print(f"Request : {request_data}")

    # Check if request ID has already been processed before sending message
    lock.acquire()
    if request_id in p_list:
        print("Duplicate message!")
        lock.release()
        return -1
    p_list.append(request_id)
    lock.release()

    producer.send(msg['to_topic'], msg)


# Define the function for consuming requests and sending responses
def consume_requests():
    global requests_m1_c, requests_m1_p, requests_m2_c, requests_m2_p
    global consumer, producer
    for message in consumer:
        request_data = message.value

        # M2 - message from node manager with ip and port
        if "schedule app" in request_data['msg']:
            res = request_data['msg'].split("$")
            start_time = res[2]
            end_time = res[3]
            app_name = res[1]
            msg_id = request_data['request_id']

            msg = {
                'to_topic': 'first_topic',
                'from_topic': 'Scheduler',
                'request_id': request_data['request_id'],
                'msg': f'done schedule app${app_name}'
            }
            if send(request_data, msg, requests_m1_c, requests_m1_p) == -1:
                print("Duplicate message!")
                continue

            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

            # calculate time difference in seconds
            start_sleep = start_time - datetime.datetime.now()
            end_sleep = end_time - datetime.datetime.now()

            # Subtract 5 hours and 30 minutes from start_sleep and end_sleep
            time_difference = datetime.timedelta(hours=5, minutes=30)
            start_sleep -= time_difference
            end_sleep -= time_difference

            print(datetime.datetime.now())
            print(start_sleep)
            print(end_sleep)

            start_sleep = int(start_sleep.total_seconds())
            end_sleep = int(end_sleep.total_seconds())

            timer1 = threading.Timer(start_sleep, start_setup_job, args=(app_name, request_data, start_time, msg_id, requests_m2_c, requests_m2_p))
            timer1.start()

            timer2 = threading.Timer(end_sleep, end_setup_job, args=(app_name, request_data, end_time, msg_id, requests_m3_c, requests_m3_p))
            timer2.start()


if __name__ == "__main__":
    thread = threading.Thread(target=consume_requests)
    thread.start()
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
    thread.join()
