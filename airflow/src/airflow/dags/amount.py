from pyspark.sql import SparkSession
import pymysql
import os

spark = SparkSession.builder.appName("joinDF").getOrCreate()

def connect():
    conn = pymysql.connect(
            host = os.getenv("DB_IP", "localhost"),
            user = 'team1',
            passwd = '1234',
            db = 'team1',
            charset = 'utf8',
            port = int(os.getenv("DB_PORT", "53306"))
    )
    return conn

def select(query: str, size: int):
    conn = connect()
    with conn:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Read a single record
            cursor.execute(query)
            if size == -1:
                result = cursor.fetchall()
            else:
                result = cursor.fetchmany(size)
    return result

def dml(sql, *values):
  conn = connect()
  with conn:
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount

sql_first = "select id from model WHERE predict_bool=1 AND total IS NULL ORDER BY id LIMIT 1"
photo_id = select(sql_first, size = 1)
#print(photo_id)
sum_result = spark.sql(
        f"select SUM(won) from goods WHERE model_id={photo_id['id']}"
        )
sum_won = sum_result.collect()[0][0]
#price = select(sql_second, size = 1)
sql_second = "UPDATE model SET total = %s WHERE id = %s"
insert_loop = 1
for _ in range(insert_loop):
        insert_row = dml(sql_second, sum_won, photo_id['id'])
