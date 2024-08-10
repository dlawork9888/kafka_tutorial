# KAFKA TUTORIAL

## KAFKA ?

- 대규모 실시간 데이터 스트림 처리를 위해 LinkedIn에서 개발
- 현재는 Apache Software Foundation에서 관리하는 오픈 소스 스트림 처리 플랫폼
- 고성능, 확장성, 내구성, 그리고 높은 처리량을 제공하는 분산 이벤트 스트리밍 시스템으로 설계

### ROLE of KAFKA

- Message Broker: 다양한 소스에서 오는 데이터 스트림을 받아서 이를 다수의 시스템이나 애플리케이션에 분산

- 이벤트 스트리밍 플랫폼: 실시간 데이터 피드를 처리하고, 저장하며, 분석할 수 있는 기능을 제공

- 데이터 통합: 서로 다른 소스와 시스템 간의 데이터를 통합하고 연동

### Basic Component

- Topic: 데이터를 저장하는 카테고리나 피드. 하나의 토픽은 하나 이상의 파티션으로 나누어져있음

- Partition: 토픽 내의 데이터를 여러 브로커에 걸쳐 분할하여 저장, 각 파티션은 독립적인 단위로 취급

  - Scale Out: 많은 브로커에 걸쳐 데이터를 저장하고 처리 -> 시스템의 처리량 증가, 더 많은 컨슈머를 동시에 처리

  - 순서 보장: 각 파티션 내에서 메시지는 엄격하게 순차적으로 정렬되어 저장, 특정 파티션에서 메시지의 순서를 보장하지만 여러 파티션에 걸쳐있는 경우 전체 토픽의 순서는 보장되지 않음

  - Replication: 파티션은 여러 브로커에 복제될 수 있음. 각 파티션에는 리더와 팔로워가 있는데, 모든 읽기와 쓰기 작업은 리더를 통해 이루어짐. 팔로워는 리더의 복제본을 유지하다가 리더가 죽을 경우 하나의 팔로워가 리더로 승격

  - 고가용성: 파티션의 데이터가 여러 브로커에 복제 -> 단일 브로커의 장애가 전체시스템의 가용성에 큰 영향을 미치지 않음. 클러스터 내에서 브로커가 실패하더라도 해당 파티션의 복제본을 가진 다른 브로커가 작업을 수행할 수 있음

- Producer: 데이터를 생성, Kafka Topic에 데이터를 보냄

- Consumer: Kafka Topic에서 데이터를 읽는 역할, Consumer Group을 만들어서 데이터 처리를 분산시킬 수도 있음(파티션을 공유하면서 메시지를 처리)

- Zookeeper: 분산 시스템을 위한 오픈 소스 조정 서비스, Apache Software Foundation에서 관리. 분산 애플리케이션 간에 일관성 있는 데이터를 유지하고 상태 정보와 메타데이터를 관리. -> 메타데이터 관리, 클러스터 상태 동기화 등 관리자 역할

## Kafka Multi-broker Cluster

### docker-compose.yml

```yml
version: '3'

services:
  zookeeper1:
    image: zookeeper:3.7
    hostname: zookeeper1
    ports:
      - "2181:2181"
    environment:
      ZOO_MY_ID: 1
      ZOO_PORT: 2181
      ZOO_SERVERS: server.1=zookeeper1:2888:3888;2181 server.2=zookeeper2:2888:3888;2182 server.3=zookeeper3:2888:3888;2183
    volumes:
      - ~/data/zookeeper1/data:/data
      - ~/data/zookeeper1/datalog:/datalog

  zookeeper2:
    image: zookeeper:3.7
    hostname: zookeeper2
    ports:
      - "2182:2182"
    environment:
      ZOO_MY_ID: 2
      ZOO_PORT: 2182
      ZOO_SERVERS: server.1=zookeeper1:2888:3888;2181 server.2=zookeeper2:2888:3888;2182 server.3=zookeeper3:2888:3888;2183
    volumes:
      - ~/data/zookeeper2/data:/data
      - ~/data/zookeeper2/datalog:/datalog

  zookeeper3:
    image: zookeeper:3.7
    hostname: zookeeper3
    ports:
      - "2183:2183"
    environment:
      ZOO_MY_ID: 3
      ZOO_PORT: 2183
      ZOO_SERVERS: server.1=zookeeper1:2888:3888;2181 server.2=zookeeper2:2888:3888;2182 server.3=zookeeper3:2888:3888;2183
    volumes:
      - ~/data/zookeeper3/data:/data
      - ~/data/zookeeper3/datalog:/datalog

  kafka1:
    image: confluentinc/cp-kafka:7.0.0
    hostname: kafka1
    ports:
      - "9091:9091"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper1:2181,zookeeper2:2182,zookeeper3:2183
      KAFKA_ADVERTISED_LISTENERS: LISTENER_DOCKER_INTERNAL://kafka1:19091,LISTENER_DOCKER_EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9091
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_DOCKER_INTERNAL:PLAINTEXT,LISTENER_DOCKER_EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_DOCKER_INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - ~/data/kafka1/data:/tmp/kafka-logs
    depends_on:
      - zookeeper1
      - zookeeper2
      - zookeeper3
  
  kafka2:
    image: confluentinc/cp-kafka:7.0.0
    hostname: kafka2
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper1:2181,zookeeper2:2182,zookeeper3:2183
      KAFKA_ADVERTISED_LISTENERS: LISTENER_DOCKER_INTERNAL://kafka2:19092,LISTENER_DOCKER_EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_DOCKER_INTERNAL:PLAINTEXT,LISTENER_DOCKER_EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_DOCKER_INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - ~/data/kafka2/data:/tmp/kafka-logs
    depends_on:
      - zookeeper1
      - zookeeper2
      - zookeeper3

  kafka3:
    image: confluentinc/cp-kafka:7.0.0
    hostname: kafka3
    ports:
      - "9093:9093"
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zookeeper1:2181,zookeeper2:2182,zookeeper3:2183
      KAFKA_ADVERTISED_LISTENERS: LISTENER_DOCKER_INTERNAL://kafka3:19093,LISTENER_DOCKER_EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_DOCKER_INTERNAL:PLAINTEXT,LISTENER_DOCKER_EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_DOCKER_INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - ~/data/kafka3/data:/tmp/kafka-logs
    depends_on:
      - zookeeper1
      - zookeeper2
      - zookeeper3



  kafdrop:
    image: obsidiandynamics/kafdrop
    restart: "no"
    ports:
      - "9000:9000"
    environment:
      KAFKA_BROKER_CONNECT: "kafka1:19091"
    depends_on:
      - kafka1
      - kafka2
      - kafka3
```

#### ZooKeeper

- 3 ZooKeeper

  - 다중 ZooKeeper ?
  
    ##### 고가용성

    단일 주키퍼 서버 사용시 장애가 발생하면 전체 시스템이 영향을 받을 수 있음. 여러 노드 사용 시, 하나의 노드에 문제가 발생해도 나머지 노드들이 시스템을 계속 운영 -> 고가용성 보장

    ##### 장애 허용

    ZooKeeper 앙상블(클러스터)은 노드 중 하나 이상이 실패하도 계속 작동할 수 있도록 설계.
    3개 노드의 경우, 최대 1개 노드까지 동시에 실패할 수 있으며 시스템은 여전히 작동.
    <= Quorum(다수결 원칙)에 기반한 결정을 가능하게 함, 데이터의 일관성과 무결성 유지


    ##### 데이터 일관성
    ZooKeeper는 모든 노드가 데이터 업데이트에 대해 동의하도록 요구.
    3개의 노드를 사용함으로써, 어느 하나의 노드에서 데이터가 변경되면 다른 두 노드에도 동일한 변경이 반영되어야 함.

```yml

  zookeeper1:
      image: zookeeper:3.7 # 도커허브가 제공하는 베이스이미지
      hostname: zookeeper1 # 컨테이너 호스트 이름
      ports:
        - "2181:2181" # 호스트포트 - 컨테이너포트 매핑
      environment: # 컨테이너 내 환경 변수
        ZOO_MY_ID: 1 # 현재 ZooKeeper 인스턴스의 ID를 1로 설정. 클러스터 내의 각 ZooKeeper 서버는 고유한 ID를 가져야함
        ZOO_PORT: 2181 # ZooKeeper 서버가 클라이언트 연결을 수신할 포트
        ZOO_SERVERS: server.1=zookeeper1:2888:3888;2181 server2=zookeeper2:2888:3888;2182 server.3=zookeeper3:2888:3888;2183
        # 클러스터 내 다른 ZooKeeper 서버들과의 통신을 위한 설정
        # 2888 -> 서버 간 데이터를 동기화하는데 사용
        # 3888 -> 리더 선출 과정에 사용
        # ;2181, ;2182, ;2183 각 서버의 클라이언트 포트(zookeeper 3.5부터 적용)
      volumes: # 볼륨 설정
        - ~/data/zookeeper1/data:/data
        - ~/data/zookeeper1/datalog:/datalog

  zookeeper2:
    image: zookeeper:3.7
    hostname: zookeeper2
    ports:
      - "2182:2182"
    environment:
      ZOO_MY_ID: 2
      ZOO_PORT: 2182
      ZOO_SERVERS: server.1=zookeeper1:2888:3888;2181 server.2=zookeeper2:2888:3888;2182 server.3=zookeeper3:2888:3888;2183
    volumes:
      - ~/data/zookeeper2/data:/data
      - ~/data/zookeeper2/datalog:/datalog

  zookeeper3:
    image: zookeeper:3.7
    hostname: zookeeper3
    ports:
      - "2183:2183"
    environment:
      ZOO_MY_ID: 3
      ZOO_PORT: 2183
      ZOO_SERVERS: server.1=zookeeper1:2888:3888;2181 server.2=zookeeper2:2888:3888;2182 server.3=zookeeper3:2888:3888;2183
    volumes:
      - ~/data/zookeeper3/data:/data
      - ~/data/zookeeper3/datalog:/datalog
```

#### Kafka Broker

- 3 Broker 

  - 다중 브로커 ?

    ##### 고가용성

    하나 또는 여러 브로커가 실패해도 다른 브로커들이 계속해서 서비스를 제공할 수 있음

    ##### 데이터 복제를 통한 데이터 내구성

    한 브로커의 데이터가 손상,손실되더라도 다른 브로커에 복제된 데이터로 복구
    replication factor을 통해 관리

    ##### 부하 분산

    메시지의 생산과 소비를 여러 브로커에 분산시켜 처리 -> 각 브로커에 걸리는 부하를 줄이고, 시스템의 처리량 증가
    또한, 큰 데이터 스트림을 처리하는 경우에도 더 나은 성능과 응답성

    ##### 데이터 및 트래픽 분리

    다중 브로커 환경을 통해 특정 데이터 스트림이나 트래픽을 특정 브로커 또는 브로커 그룹에 할당할 수 있음


```yml

  kafka1:
    image: confluentinc/cp-kafka:7.0.0 # Confluent에서 제공하는 Kafka 7.0.0 버전 이미지
    hostname: kafka1 # 컨테이너 호스트 이름
    ports:
      - "9091:9091" # 호스트포트 - 컨테이너포트 매핑
    environment:
      KAFKA_BROKER_ID: 1 # Kafka 브로커의 고유 ID를 1로, 클러스터 내 각 카프카 브로커는 고유한 ID를 가져야함
      KAFKA_ZOOKEEPER_CONNECT: zookeeper1:2181,zookeeper2:2182,zookeeper3:2183 
      # 카프카 브로커가 주키퍼 서비스와 연결하기 위한 정보, 각 주키퍼 서버의 호스트 이름과 포트 번호
      KAFKA_ADVERTISED_LISTENERS: LISTENER_DOCKER_INTERNAL://kafka1:19091,LISTENER_DOCKER_EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9091
      # Kafka 브로커가 클라이언트에 자신을 알리는 방법, 내부 및 외부 네트워크 주소를 설정
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_DOCKER_INTERNAL:PLAINTEXT,LISTENER_DOCKER_EXTERNAL:PLAINTEXT
      # 각 리스너의 보안 프로토콜 설정, 여기서는 PLAINTEXT(암호화 안됨, 말그대로 그냥 텍스트)
      KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_DOCKER_INTERNAL
      # 브로커 간 통신에 사용할 리스너의 이름
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 2
      # 오프셋 토픽(토픽 파티션)의 복제 계수를 2로 설정, 토픽의 모든 파티션이 2개의 브로커에 복제되어 저장됨
    volumes: # 볼륨 설정 
      - ~/data/kafka1/data:/tmp/kafka-logs
    depends_on:
      - zookeeper1
      - zookeeper2
      - zookeeper3
  
  kafka2:
    image: confluentinc/cp-kafka:7.0.0
    hostname: kafka2
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper1:2181,zookeeper2:2182,zookeeper3:2183
      KAFKA_ADVERTISED_LISTENERS: LISTENER_DOCKER_INTERNAL://kafka2:19092,LISTENER_DOCKER_EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_DOCKER_INTERNAL:PLAINTEXT,LISTENER_DOCKER_EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_DOCKER_INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 2
    volumes:
      - ~/data/kafka2/data:/tmp/kafka-logs
    depends_on:
      - zookeeper1
      - zookeeper2
      - zookeeper3

  kafka3:
    image: confluentinc/cp-kafka:7.0.0
    hostname: kafka3
    ports:
      - "9093:9093"
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zookeeper1:2181,zookeeper2:2182,zookeeper3:2183
      KAFKA_ADVERTISED_LISTENERS: LISTENER_DOCKER_INTERNAL://kafka3:19093,LISTENER_DOCKER_EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_DOCKER_INTERNAL:PLAINTEXT,LISTENER_DOCKER_EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_DOCKER_INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - ~/data/kafka3/data:/tmp/kafka-logs
    depends_on:
      - zookeeper1
      - zookeeper2
      - zookeeper3

```

#### Kafdrop

-  Kafka 클러스터의 토픽과 메시지, 컨슈머 그룹 등을 시각화하여 관리할 수 있도록 해주는 웹 UI 

```yml
kafdrop:
    image: obsidiandynamics/kafdrop # Obsidian Dynamics에서 제공하는 kafdrop 이미지
    restart: "no" # 컨테이너의 재시작 정책을 "no"로 설정
    ports:
      - "9000:9000" # 호스트포트 - 컨테이너 포트 매핑
    environment:
      KAFKA_BROKER_CONNECT: "kafka1:19091" 
      # Kafdrop이 Kafka 클러스터와 연결하기 위해 사용할 Kafka 브로커의 주소
      # 여기서는 kafka1의 내부 리스너 포트인 19091을 지정
      # 단일 브로커만 연결
    depends_on: # 시작되기 전에 실행되어야 할 다른 서비스들을 지정
      - kafka1
      - kafka2
      - kafka3
```

#### Bootstrap Server ?

- 클라이언트(Producer/Consumer)가 Broker에 접속할 때에는 부트스트랩 서버를 통해 접근

- 부트스트랩 서버는 카프카 클러스터 내의 모든 Broke들을 총칭하기도 함

##### 클라이언트가 브로커에 연결하는 과정

- 클라이언트가 최초로 특정 Broker에 연결하면, 해당 Broker는 카프카 클러스터 내의 모든 Broker의 리스트를 응답

- 각각의 Broker들은 모든 Broker, Topic, Partition의 정보(Metadata)에 대해 알고 있음

- 클라이언트는 응답 받은 Broker 리스트를 통해 클라이언트(Producer/Consumer)가 메시지를 전달하거나 받아가야 할 Topic(Partition)의 위치를 알게 되고 해당 Partition이 있는 Broker로 연결

- 하지만 해당 Broker에 문제가 발생했을 경우를 대비해 모든 Broker들에 대해 연결을 시도하는 방식이 일반적

### TOPIC 생성

```
- 카프카 브로커 컨테이너에 접속

- kafka-topics를 이용
  - kafka-topics는 /usr/bin에 위치
  - 대부분의 kafka 관련 실행 파일은 여기에 위치함

예시) kafka broker 2에 접속하여 usr/bin에서 아래를 실행

kafka-topics --create --topic my-topic --bootstrap-server kafka2:19092 --partitions 3 --replication-factor 2

--bootstrap-server 옵션에서 kafka2:19092를 지정하여 kafka2 브로커를 부트스트랩 서버로 사용

***
docker-compose.yml에서 kafka1 브로커의

KAFKA_ADVERTISED_LISTENERS: LISTENER_DOCKER_INTERNAL://kafka1:19091,LISTENER_DOCKER_EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9091

KAFKA_ADVERTISED_LISTENERS 환경 변수에 설정된 LISTENER_DOCKER_EXTERNAL 주소가 부트스트랩 서버를 의미
***
```

- kafdrop(localhost:9000)에 접속해서도 토픽을 생성할 수 있음 !

### producer.py

```python

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

```

### consumer.py

```python

# Consumer
from kafka import KafkaConsumer
import json


# consumer 설정 
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

```

- consumer.py를 실행해놓고 producer.py를 통해 메시지 발신해보면 consumer측에서 실시간으로 메시지를 받는 것을 확인할 수 있음 !