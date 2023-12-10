# IAS-IOT-AVISKAR-23

## Important commands

### Copy from local machine to VM
scp -r -i {VM_KEY_PATH} {SOURCE_FOLDER_PATH} {VM_USERNAME}@{VM_IP_ADDRESS}:{DESTINATION_PATH}

### Permission Denied Error
chmod 0600 {VM_KEY_PATH}

### SSH to VM
cd IAS-IOT-AVISHKAR-23
ssh -i {VM_KEY_PATH} {VM_USERNAME}@{VM_IP_ADDRESS}

ssh -i VM-keys/azure_VM1_key.pem vmadmin@13.81.42.121
ssh -i VM-keys/azure_VM2_key.pem azureuser@40.115.28.100
ssh -i VM-keys/azure_VM3_key.pem azureuser@51.144.255.78

### TO RUN PLATFORM INITIALIZER
python3 PlatformInitializer/main.py

### Install the important dependencies
pip install pymongo
pip install requests
pip install flask
pip install -U flask-cors
pip install kafka-python
pip install psycopg2
if above commnad give error pip install psycopg2-binary

### For fetching data from ONEM2M server
###### start the server
cd ONEM2M; ./start_om2m_server.sh
###### start data generator.py
python3 ONEM2M/data_generator.py
###### start the fetching script from ONEM2M server
python3 SensorManager/dataSend.py
###### start the flask application
python3 SensorManager/main.py 


#### Kafka commands

list kafka topics
kafka-topics.sh --bootstrap-server 20.196.205.46:9092 --list

create a topic
kafka-topics.sh --bootstrap-server 20.196.205.46:9092 --topic first_topic --create --partitions 3 --replication-factor 1

delete a topic
bin/kafka-topics.sh --bootstrap-server 20.196.205.46:9092 --delete --topic topic_name

bin/kafka-topics.sh --bootstrap-server 20.196.205.46:9092 --delete --topic topic_name


#### Sensor APIs

### To fetch last n values of a node of specific sensor type
GET localhost:8000/api/sensordata/latest/<sensor_type>/<nodename>/<n_messages>
### To fetch the latest value of a node of specific sensor type
GET localhost:8000/api/sensordata/latest/<sensor_type>/<nodename>