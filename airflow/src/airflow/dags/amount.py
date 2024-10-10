from pyspark.sql import SparkSession
import pymysql
import os
import pandas as pd

spark = SparkSession.builder.appName("joinDF").getOrCreate()

def connect():
    conn = pymysql.connect(
            host = os.getenv("DB_IP", "13.125.51.70"),
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

def fetch_data(sql):
    conn = connect()
    with conn:
        df = pd.read_sql(sql, conn)
    return df

def update_accuracy_scores():
    sql_fourth = """
    insert into accuracy_scores (model_id, label_id, goods_id, name_score, count_score, amount_score, total_score)
    select
        g.model_id,
        l.id AS label_id,
        g.id AS goods_id,
        SUM(CASE WHEN l.name = g.name THEN 1 ELSE 0 END) AS total_name_score,
        SUM(CASE WHEN l.cnt = g.cnt THEN 1 ELSE 0 END) AS total_count_score,
        SUM(CASE WHEN l.won = g.won THEN 1 ELSE 0 END) AS total_amount_score,
        SUM(
            CASE WHEN l.name = g.name THEN 1 ELSE 0 END +
            CASE WHEN l.cnt = g.cnt THEN 1 ELSE 0 END +
            CASE WHEN l.won = g.won THEN 1 ELSE 0 END
        ) AS total_total_score
    from
        goods g
    join
        labels l ON g.model_id = l.model_id
    WHERE
        g.model_id NOT IN (select model_id FROM accuracy_scores)
        AND NOT EXISTS (
            select 1
            from accuracy_scores a
            WHERE a.model_id = g.model_id
            AND a.label_id = l.id
            AND a.goods_id = g.id
        )
    GROUP BY
        g.model_id,
        l.id;
    """
    dml(sql_fourth)


def update_model_total():
    # 예측한 모델중 총액이 NULL인 id를 위에서부터 출력하는 쿼리
    sql_first = "select id from model WHERE predict_bool=1 AND total IS NULL ORDER BY id LIMIT 1"
    temp_result = select(sql_first, size = 1)
    if temp_result:
        photo_id = temp_result[0]['id']

        print("="*10)
        print(photo_id)
        print("="*10)

        # goods 테이블의 특정 model_id에서의 물건들의 금액 합을 출력하는 쿼리
        sql_second=f"select SUM(won) from goods WHERE model_id={photo_id}"

        sum_df = fetch_data(sql_second)
        pyspark_sum_df = spark.createDataFrame(sum_df)
        pyspark_sum_df.createOrReplaceTempView("pyspark_sum")
        sum_result = spark.sql("select `SUM(won)` from pyspark_sum")
        sum_won = sum_result.collect()[0][0]
        print("="*10)
        print(sum_won)
        print("="*10)

        # model 테이블의 id에 해당하는 total (총액)을 업데이트 시키는 쿼리
        sql_third = "update model SET total = %s WHERE id = %s"
        dml(sql_third, sum_won, photo_id)

    else:
        print("="*10)
        print("No photo_id found. Exiting the function.")
        print("="*10)

    # 모델 정확도 점수 테이블에 goods 테이블과 labels 테이블의 값이 모두 있는 경우 실행하는 쿼리
    # 값의 일치 불일치에 따라 각각 1점씩 점수를 부여하고 총점을 insert 하는 쿼리
    update_accuracy_scores()

update_model_total()
