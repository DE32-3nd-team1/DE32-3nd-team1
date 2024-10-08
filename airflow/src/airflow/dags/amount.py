from pyspark.sql import SparkSession
import pymysql

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
print(photo_id)

sql_second = f"select * from goods WHERE model_id={photo_id}"
                                  
