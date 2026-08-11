from kafka import KafkaProducer
import json
import os

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")

producer = None

def get_producer():
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    return producer

def send_event(topic: str, event_data: dict):
    prod = get_producer()
    prod.send(topic, event_data)
    prod.flush()