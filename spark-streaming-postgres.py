import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import split
import time

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

load_dotenv(override=True, dotenv_path="./dev.env")


# Initialize SparkSession
def create_spark_session() -> SparkSession:
    spark = (
        SparkSession.builder.appName("Kafka Spark Streaming to Postgres")
        .config("spark.log.level", "ERROR")
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
    df_output = (
        df.select(split(df.value, "\t").alias("data")).selectExpr(
            "CAST(data AS STRING)"
        )
        # .select(from_json(col("value"), schema).alias("data"))
        # .select("data.*")
    )
    return df_output


# Write to Console
# query = df_output.writeStream.outputMode("append").format("console").start()


if __name__ == "__main__":
    spark = create_spark_session()
    df = read_from_kafka(spark)
    tranformed_df = transform_data(df)
    # tranformed_df.printSchema()

    # write to console
    # query = tranformed_df.writeStream.outputMode("append").format("console").start()

    # write to csv
    # query = (
    #     tranformed_df.writeStream.outputMode("append")
    #     .format("csv")
    #     .option("path", "./output")
    #     .option("checkpointLocation", "./checkpoint")
    #     .start()
    # )

    # make colums
    query = (
        tranformed_df.writeStream.outputMode("append")
        .format("csv")
        .option("path", "./output")
        .option("checkpointLocation", "./checkpoint")
        .start()
    )

    # Await Termination
    query.awaitTermination()
