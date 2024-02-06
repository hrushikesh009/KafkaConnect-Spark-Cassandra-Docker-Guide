## Confluent Cloud and Kafka Topic Setup

### 1. **Setup Confluent Cloud:**
   - Visit [Confluent Cloud signup page](https://confluent.cloud/signup).
   - Enter details, confirm email, choose Basic cluster, configure settings, name your cluster, and launch.

### 2. **Create Kafka Topic:**
   - From Confluent Cloud, go to "Topics" and create "user-data" with default partitions.
   - Use Confluent Cloud Console to view the topic and produce key-value messages.

### 3. **Produce Messages from CLI:**
   - Learn to produce real-time data stream messages from the CLI.

### 4. **Explore Kafka Topic:**
   - View and explore "user-data" topic, adding messages across partitions.

## Datagen Source Connector Setup

### 1. **Navigate to Confluent Cloud:**
   - Log in to your Confluent Cloud account.

### 2. **Access Connectors:**
   - Go to the Connectors section in Confluent Cloud Console.

### 3. **Create Connector:**
   - Click "Add Connector" -> "Datagen Source."

### 4. **Configure Datagen Connector:**
   - Set connector name, topic ("user-data"), tasks, and key-value JSON schema.
   - Define data generator properties like iterations, schema filename, and keyfield.

### 5. **Enable Connector:**
   - Launch the Datagen Source Connector and verify successful data generation.

### 6. **Monitor Connector:**
   - Check the Confluent Cloud Console for the connector's status to ensure smooth operation.

### 7. **Review and Adjust:**
   - Periodically review and adjust Datagen Source Connector settings as needed.

## KafkaConnect-Spark-Cassandra-Docker-Guide

### Setup Guide

1. **Clone Repository:**
   ```
   git clone git@github.com:hrushikesh009/KafkaConnect-Spark-Cassandra-Docker-Guide.git
   ```

2. **Navigate to Project:**
   ```bash
   cd KafkaConnect-Spark-Cassandra-Docker-Guide
   ```

3. **Create `kafka_config.ini` in `config` folder:**
   - Copy and paste the following content:

     ```ini
     [consumer]
     group.id="spark-kafka-cassandra"
     auto.offset.reset=earliest

     [spark-kafka]
     kafka.bootstrap.servers= "Your Confluent Bootstrap Server"
     kafka.security.protocol=SASL_SSL
     kafka.sasl.username="Your API Key generated on Confluent"
     kafka.sasl.password="Your API Secret generated on Confluent"
     kafka.ssl.endpoint.identification.algorithm=https
     kafka.sasl.mechanism=PLAIN
     subscribe="Your topic name"
     ```

4. **Docker Setup:**
   - Build the Spark image using:
     ```bash
     docker build -name spark:1 .
     ```
   - Bring all containers, including Spark and Cassandra, with:
     ```bash
     docker-compose up -d
     ```

5. **Cassandra Setup:**
   - Access the Cassandra server:
     ```bash
     docker exec -it cassandra /bin/bash
     ```
   - Access CQLSH CLI:
     ```bash
     cqlsh -u cassandra -p cassandra
     ```
   - Run the following commands to create keyspace `spark_kafka_cassandra` and table `user-data`:
     ```sql
     CREATE KEYSPACE spark_kafka_cassandra WITH replication = {'class':'SimpleStrategy','replication_factor':1};
     CREATE TABLE IF NOT EXISTS spark_kafka_cassandra.user-data (
                                        registertime TIMESTAMP,
                                        user_id TEXT,
                                        region TEXT,
                                        gender TEXT,
                                        PRIMARY KEY (userid)
                                    );

     DESCRIBE spark_kafka_cassandra.user-data;
     ```

6. **Run the Spark Script:**
   - Copy local PySpark script into the container:
     ```bash
     docker cp spark_streaming.py kafka-config.ini spark_master:/opt/bitnami/spark/
     ```
   - Access the Spark container and install necessary JAR files under the jars directory:
     ```bash
     docker exec -it spark_master /bin/bash
     cd ..
     spark-submit --master local[2] spark_streaming.py kafka-config.ini
     ```
   - After running the command, verify data population into the Cassandra table.

7. **Enjoy :)**

## Technologies Used:

- **Confluent Kafka:** Cloud-based Kafka Connect configuration.
- **Spark:** Utilizing Structured Streaming for real-time data processing.
- **Cassandra:** NoSQL database for seamless data storage.
- **Docker:** Containerized environment for easy setup and reproducibility.
- **Python:** Scripting language for additional automation.


