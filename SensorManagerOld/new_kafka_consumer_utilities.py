from kafka import KafkaConsumer, TopicPartition
import json 
import ast


def get_latest_data_from_topic(topic_name,partion_num):
    consumer = KafkaConsumer(bootstrap_servers=['20.196.205.46:9092'])

    # Get the latest offset for the partition
    partition = TopicPartition(topic_name, partion_num)
    consumer.assign([partition])
    consumer.seek_to_end(partition)
    latest_offset = consumer.position(partition)

    # Read the last message from the partition
    consumer.seek(partition, latest_offset - 1)
    message = next(consumer)

    return message.value 

def get_last_n_data_from_topic(topic_name,partion_num,n_messages):

    # Set the Kafka broker and topic information
    bootstrap_servers = ['20.196.205.46:9092']

    # Create a KafkaConsumer instance and seek to the end of the partition
    consumer = KafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset='latest',
        enable_auto_commit=False,
        value_deserializer=lambda x: x.decode('utf-8')
    )
    consumer.assign([TopicPartition(topic_name, partion_num)])
    consumer.seek_to_end()

    # Get the current position in the partition and calculate the offset for the last n messages
    end_offset = consumer.position(TopicPartition(topic_name, partion_num))
    start_offset = end_offset - n_messages

    # Seek to the start offset and consume messages until the end of the partition
    consumer.seek(TopicPartition(topic_name, partion_num), start_offset)
    messages = []
    for message in consumer:
        messages.append(json.loads(message.value))

        # Exit the loop when we have printed the desired number of messages
        if message.offset == end_offset - 1:
            break

    # Close the KafkaConsumer
    consumer.close()
    return json.dumps(messages)