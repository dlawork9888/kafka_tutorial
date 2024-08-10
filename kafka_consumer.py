# Consumer
from kafka import KafkaConsumer
import json


# 컨슈머 설정 
consumer = KafkaConsumer(
    'test',
    bootstrap_servers=['127.0.0.1:9091', '127.0.0.1:9092', '127.0.0.1:9093'],
    auto_offset_reset='earliest', # 가장 오래된 메시지부터 읽기 시작
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)


if __name__ == "__main__":
    
    print("Topic default: test")
    try:
        for message in consumer:
            print(f"Received message: {message.value} at offset {message.offset}")
    except KeyboardInterrupt:
        print("Interrupted, closing consumer...")
    finally:
        consumer.close()
        print("Consumer closed.")
