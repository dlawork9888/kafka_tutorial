from kafka import KafkaProducer
import json
import time

# Kafka 프로듀서 설정
producer = KafkaProducer(
    bootstrap_servers=['127.0.0.1:9091', '127.0.0.1:9092', '127.0.0.1:9093'], # Kafka 브로커 주소
    value_serializer=lambda v: json.dumps(v).encode('utf-8') # 메시지를 JSON 형식으로 직렬화
)


def send_message(test_message): # DICT
    producer.send('test', value=test_message) # test토픽에 보냄
    producer.flush()
    print("Message sent:", test_message)


if __name__ == "__main__":
    print("topic: test(defualt)")
    while True:
        key = input("key: (quit -> q)")
        value = input("value: ")
        send_message({key : value})

