import logging
import os
from argparse import ArgumentParser, FileType
from configparser import ConfigParser

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import from_json
from pyspark.sql.types import (StringType, StructField, StructType,
                               TimestampType)

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
logger = logging.getLogger("spark_logger")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_spark_session():
    try:
        spark = SparkSession \
                .builder \
                .appName("StructedStreamming") \
                .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.4.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
                .config("spark.cassandra.connection.host", "cassandra") \
                .config("spark.cassandra.connection.port","9042")\
                .config("spark.cassandra.auth.username", "cassandra") \
                .config("spark.cassandra.auth.password", "cassandra") \
                .getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        logging.info('Spark session created successfully')
    except Exception:
        logging.error("Couldn't create the spark session")

    return spark

def create_initial_dataframe(spark_session,kafka_config):
    """
    Reads the streaming data and creates the initial dataframe accordingly.
    """
    try:
        df = spark_session \
            .readStream \
            .format("kafka") \
            .options(**kafka_config)\
            .option("startingOffsets", "earliest")\
            .option("failOnDataLoss", "false")\
            .load()\
            .select('value','timestamp')

        logging.info("Initial dataframe created successfully")
    except Exception as e:
        logging.warning(f"Initial dataframe couldn't be created due to exception: {e}")

    return df

def create_final_dataframe(df):
    """
    Modifies the initial dataframe, and creates the final dataframe.
    """
    schema = StructType([
                StructField("registertime",TimestampType(),False),
                StructField("userid",StringType(),False),
                StructField("regionid",StringType(),False),
                StructField("gender",StringType(),False),
            ])

    df = df.selectExpr("CAST(value AS STRING)","timestamp") \
    .select(from_json(F.col("value"), schema).alias("data"),"timestamp") \
    .select("data.*","timestamp")\
    .withColumnRenamed("userid","user_id")\
    .withColumnRenamed("regionid","region")

    return df

def start_streaming(df):
    """
    Starts the streaming to table spark_streaming.random_names in cassandra
    """
    logging.info("Streaming is being started...")
    my_query = (df.writeStream
                  .format("org.apache.spark.sql.cassandra")
                  .outputMode("append")
                  .options(table="user_data", keyspace="spark_kafka_cassandra")\
                  .option("checkpointLocation", os.path.join(BASE_DIR,"checkpoint"))
                  .start())

    return my_query.awaitTermination()




def main(config):
    spark = create_spark_session()
    df = create_initial_dataframe(spark, config)
    df = create_final_dataframe(df)
    start_streaming(df)
    spark.stop()

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'))
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()


    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser['spark-kafka'])
    config['kafka.sasl.jaas.config'] = f"org.apache.kafka.common.security.plain.PlainLoginModule required username='{config['kafka.sasl.username']}' password='{config['kafka.sasl.password']}';"
    config.update(config_parser['consumer'])

    main(config)