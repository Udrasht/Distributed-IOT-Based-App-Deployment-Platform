from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError
from kafka.protocol.admin import DeleteTopicsRequest


def give_existing_topics():
    # Set up KafkaAdminClient with your Kafka broker address(es)
    admin_client = KafkaAdminClient(bootstrap_servers=['20.196.205.46:9092'])

    # Use the KafkaAdminClient to get the list of topics
    try:
        topics = admin_client.list_topics()
        print("Existing topics in the Kafka cluster:")
        print(topics)
        return topics
    except KafkaError as e:
        print("Error listing topics: ", e)

def create_topic(topic_name,n_partition):
    # Initialize admin client
    admin_client = KafkaAdminClient(bootstrap_servers=['20.196.205.46:9092'])

    # Create new topic configuration
    topic_config = {
        "cleanup.policy": "delete",
        "compression.type": "gzip",
        "retention.ms": "86400000"
    }

    # Create new topic object
    new_topic = NewTopic(name=topic_name, num_partitions=n_partition, replication_factor=1)

    # Create the new topic on Kafka server
    admin_client.create_topics([new_topic])

def delete_topic(topic_name):
    # Set up KafkaAdminClient with your Kafka broker address(es)
    admin_client = KafkaAdminClient(bootstrap_servers=['20.196.205.46:9092'],request_timeout_ms=100000)

    # Use the KafkaAdminClient to delete the topic
    try:
        admin_client.delete_topics(topics=[topic_name])
        print("The topic {} has been deleted from the Kafka cluster.".format(topic_name))
    except KafkaError as e:
        print("Error deleting topic {}: {}".format(topic_name, e))


