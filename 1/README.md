### Основные Kafka сущности:
1. **Broker** - отвечает за прием, сохранение и передачу сообщений между продюсерами (Producer) и консюмерами (Consumer). Брокеров может быть много, тогда они объединяются в кластер
2. **Zookeeper** - БД для хранения метаданных. Управляет кластером, хранит его состояние, обнаруживает брокеров, выбирает контроллер кластера, отслеживает состояние узлов и обеспечивает функциональность и надежность кластера
3. **Controller кластера** - специальный брокер, обеспечивает консистентность данных. Отвечает за назначение мастеров партиций и отслеживает состояние брокеров

Настроим Zookeeper:
```
zookeeper:                                 # Определим сервис Zookeeper
    image: confluentinc/cp-zookeeper:7.2.1 # Выбираем Docker образ
    hostname: zookeeper                    # Имя хоста внутри Docker (можно использовать его, а не IP)
    container_name: zookeeper              # Имя контейнера
    ports:                                 
        - "2181:2181"                      # Пробрасываем порт 2181 между контейнером и хостом
    environment:
        ZOOKEEPER_CLIENT_PORT: 2181        # Порт, который Zookeeper слушает для клиентов
```

Далее настроим Broker-Kafka
```
kafka:                                   # Определим сервиса Kafka
    image: confluentinc/cp-server:7.2.1  # Выбираем Docker образ для Kafka
    hostname: kafka                      # Имя хоста внутри Docker (можно использовать его, а не IP)
    container_name: kafka                # Имя контейнера
    depends_on:                          # Зависимости между сервисами
      - zookeeper                        # Kafka запустится после от ZooKeeper
    ports:  
      - "9092:9092"                      # Основной порт для клиентских подключений к Kafka
    environment:                         # Переменные окружения для конфигурации Kafka
      KAFKA_BROKER_ID: 1                                        # Уникальный идентификатор брокера Kafka
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'                 # Подключение к ZooKeeper
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT # Настройка протоколов безопасности
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092    # Адрес, который клиенты используют для подключения
```

### Advertised Listeners

Что это такое?
KAFKA_ADVERTISED_LISTENERS — это параметр, который сообщает клиентам (Producers, Consumers), по какому адресу они могут подключиться к брокеру Kafka.

Давайте попробуем изменить существующий advertise listener добавить ещё один:

```
kafka:                                   
    ...
    ports:  
      - "9092:9092"                      
    environment:                         
      KAFKA_BROKER_ID: 1                                        
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'                 
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT 
      KAFKA_ADVERTISED_LISTENERS: MY_LISTENER_1://localhost:9092,MY_LISTENER_2://localhost:9093
```

Пробуем запустить, но контейнер kafka падает с такой ошибкой
`No security protocol defined for listener MY_LISTENER_1`

Мы забыли объявить слушателей в KAFKA_LISTENER_SECURITY_PROTOCOL_MAP, вот как это работает 
Разберем такую запись: `MY_LISTENER_1:PLAINTEXT`
1. MY_LISTENER_1 - имя ADVERTISED_LISTENER-a
2. PLAINTEXT - протокол безопасности

Тогда добавим для каждого созданного нами ADVERTISED_LISTENER-a протокол
```
kafka:                                   
    ...
    ports:  
      - "9092:9092"                      
    environment:                         
      KAFKA_BROKER_ID: 1                                        
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'                 
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: MY_LISTENER_1:PLAINTEXT,MY_LISTENER_2:PLAINTEXT 
      KAFKA_ADVERTISED_LISTENERS: MY_LISTENER_1://localhost:9092,MY_LISTENER_2://localhost:9093
```

Теперь контейнер падает с такой ошибкой
requirement failed: inter.broker.listener.name must be a listener name defined in advertised.listeners. The valid options based on currently configured listeners are MY_LISTENER_1,MY_LISTENER_2

Все верно, мы не указали, кто будет `INTER_BROKER`. INTER_BROKER - это такой брокер, через котрого будет происходить всё общение между остальными брокерами, по сути это телефонная система офиса, где каждый брокер это сотрудник

```
kafka:                                   
    ...
    ports:  
      - "9092:9092"                      
    environment:                         
      KAFKA_BROKER_ID: 1                                        
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'                 
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: MY_LISTENER_1:PLAINTEXT,MY_LISTENER_2:PLAINTEXT 
      KAFKA_ADVERTISED_LISTENERS: MY_LISTENER_1://localhost:9092,MY_LISTENER_2://localhost:9093
      KAFKA_INTER_BROKER_LISTENER_NAME: MY_LISTENER_1
```

Теперь наш сервис успешно запускается
