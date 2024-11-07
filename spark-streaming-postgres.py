import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.functions import split, col
import time
from output_schemas import snowplow_schema
from sqlalchemy import create_engine, Table, MetaData, URL, Column, String

# set spark environment variables
# os.environ["SPARK_HOME"] = r"e:\snowplow-micro\.venv\lib\site-packages\pyspark"
# os.environ["PYSPARK_PYTHON"] = "python"
# os.environ["PYSPARK_SUBMIT_ARGS"] = (
#     "--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 pyspark-shell"
# )
# testing basic dataframe
# data = [
#     ("Finance", 10),
#     ("Marketing", 20),
# ]
# df = spark.createDataFrame(data=data)
# df.show(10, False)

load_dotenv(override=True, dotenv_path="./.env.dev")


# Initialize SparkSession
def create_spark_session() -> SparkSession:
    spark = (
        SparkSession.builder.appName("Kafka Spark Streaming to Postgres")
        .config("spark.log.level", "INFO")
        # add packages work with kafka and postgres
        .config(
            "spark.jars.packages",
            "org.postgresql:postgresql:42.7.4,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3",
        )
        .getOrCreate()
    )
    return spark


# Read from Kafka
def read_from_kafka(spark_session: SparkSession) -> DataFrame:
    df = (
        spark_session.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9094")
        .option("subscribe", "enriched_good_data_topic")  # Our topic name
        .option(
            "startingOffsets", "earliest"
        )  # Start from the beginning when we consume from kafka
        .load()
    )
    return df


# Process Data
def transform_data(df: DataFrame) -> DataFrame:
    # df_output = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
    """split data into columns and then add schemas"""
    df_output = df.select(split(df.value, "\t").alias("data")).select(
        *[col("data")[i].alias(snowplow_schema[i]) for i in range(len(snowplow_schema))]
    )
    return df_output


def write_to_csv(df: DataFrame) -> StreamingQuery:
    query = (
        df.writeStream.outputMode("append")
        .format("csv")
        .option("header", "true")
        .option("path", "./output")
        .option("checkpointLocation", "./checkpoint")
        .start()
    )
    return query


def write_to_console(df: DataFrame) -> StreamingQuery:
    query = df.writeStream.outputMode("append").format("console").start()
    return query


def foreach_batch_function(df: DataFrame, epoch_id) -> None:
    postgres_url = f'jdbc:postgresql://{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}'
    df.write.mode("append").format("jdbc").option("url", postgres_url).option(
        "driver", "org.postgresql.Driver"
    ).option("dbtable", "snowplow_events").option(
        "user", os.getenv("POSTGRES_USER")
    ).option(
        "password", os.getenv("POSTGRES_PASSWORD")
    ).save()


def write_to_postgres(df: DataFrame) -> StreamingQuery:
    query = df.writeStream.foreachBatch(foreach_batch_function).start()
    return query


def create_postgres_table():
    postgres_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
    )

    engine = create_engine(postgres_url)
    metadata_obj = MetaData()
    table = Table(
        "snowplow_events",
        metadata_obj,
        *(Column(col_name, String) for col_name in snowplow_schema),
    )
    metadata_obj.create_all(engine)


if __name__ == "__main__":
    create_postgres_table()
    spark = create_spark_session()
    df = read_from_kafka(spark)
    tranformed_df = transform_data(df)

    # tranformed_df.printSchema()

    # query = write_to_csv(tranformed_df)

    query = write_to_postgres(tranformed_df)

    # Await Termination
    query.awaitTermination()
