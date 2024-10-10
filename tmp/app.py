from pyspark.sql import SparkSession

# SparkSession 생성
spark = SparkSession.builder.appName("SparkPi").getOrCreate()

# Pi 계산 작업
def compute_pi(partitions):
    n = 100000 * partitions
    def inside(_):
        from random import random
        x, y = random(), random()
        return x*x + y*y < 1
    count = spark.sparkContext.parallelize(range(0, n), partitions).filter(inside).count()
    return 4.0 * count / n

if __name__ == "__main__":
    partitions = 4
    pi = compute_pi(partitions)
    print(f"Pi is roughly {pi}")

    # SparkSession 종료
    spark.stop()

