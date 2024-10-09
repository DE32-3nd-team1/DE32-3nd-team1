from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
import os
import shutil
import pymysql
from datetime import datetime
import uuid
import pandas as pd
import json
import mariadb

app = FastAPI()

# 데이터베이스 설정
DB_CONFIG = {
    "host": os.getenv("DB_IP", "172.31.10.216"),
    "user": "team1",
    "password": "1234",
    "database": "team1",
    "port": int(os.getenv("DB_PORT", 53306)),
    "cursorclass": pymysql.cursors.DictCursor
}
# 업로드 디렉토리 설정 (환경 변수에서 가져오거나 기본값 사용)
upload_directory = os.getenv('UPLOAD_DIR', 'images/')
# 이미지 업로드 엔드포인트
@app.post("/upload_image")
async def upload_image(
    file: UploadFile = File(...),
    date: str = Form(...),
    time: str = Form(...),
    weekday: str = Form(...)
):
    # 허용된 이미지 확장자 목록
    allowed_extensions = {"jpeg", "jpg", "png"}

    # 파일 확장자 확인
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Only jpeg, jpg, and png files are allowed.")

    os.makedirs(upload_directory, exist_ok=True)  # 디렉토리가 없으면 생성

    # 고유한 파일명 생성 (UUID 사용)
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    img_src = os.path.join(upload_directory, unique_filename)

    # 파일 저장
    try:
        with open(img_src, "wb") as f:
            print("파일 저장")
            #print(file.file.read())
            shutil.copyfileobj(file.file, f)
            #from PIL import Image

            # 저장된 이미지 파일 열기
            #with Image.open(img_src) as img:
                #img.show()  # 이미지가 제대로 열리면 보여줌
            #f.write(file.file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File saving failed: {str(e)}")


    # 날짜와 시간 데이터 합치기 및 유효성 검사
    try:
        # date와 time을 합쳐서 purchase_date 생성
        purchase_date = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date or time format: {str(e)}")

    # 데이터베이스에 파일 경로 및 구매 정보 저장
    try: 
        conn = pymysql.connect(**DB_CONFIG)
        with conn:
            with conn.cursor() as cursor:

                sql_insert_model = """
                    INSERT INTO model (purchase_date, weekday, predict_bool, img_src)
                    VALUES (%s, %s, %s, %s)
                """
                predict_bool = False
                cursor.execute(sql_insert_model, (purchase_date.strftime("%Y-%m-%d %H:%M:%S"), weekday, predict_bool, img_src))
                conn.commit()

                # 삽입된 model 테이블의 ID 값 가져오기
                model_id = cursor.lastrowid
                #print(f"Inserted model_id: {model_id}")

                # goods 테이블에서 model_id와 연관된 상품들의 금액 합계를 계산
                sql_sum_won = """
                    SELECT COALESCE(SUM(won), 0) AS total_won
                    FROM goods
                    WHERE model_id = %s;
                """
                cursor.execute(sql_sum_won, (model_id,))
                result = cursor.fetchone()
                total_won = result['total_won'] if result and result['total_won'] else 0
                #print(f"Calculated total_won: {total_won}")
                
                # model 테이블의 total 필드 업데이트
                sql_update_model = """
                    UPDATE model
                    SET total = %s
                    WHERE id = %s;
                """
                cursor.execute(sql_update_model, (total_won, model_id))
                
                conn.commit()
                insert_row_count = cursor.rowcount  # 삽입된 행 수 확인
    except (pymysql.MySQLError, mariadb.Error) as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



    # 업로드 결과 반환
    return {
        "status": "success",
        "filename": file.filename,
        "file_location": img_src,
        "purchase_date": purchase_date.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday": weekday,
        "insert_row_count": insert_row_count,
        "total_won": total_won
    }
@app.get("/model_result")
async def get_model_result():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn:
            with conn.cursor() as cursor:
                # SQL 쿼리: 예측 여부가 True이고 id 값이 가장 큰 model_id에 해당하는 goods 테이블의 모든 상품 조회
                sql = """
                SELECT g.name AS nm, g.won AS unitprice, g.cnt
                FROM goods g
                JOIN model m ON g.model_id = m.id
                WHERE m.predict_bool = TRUE
                ORDER BY m.id DESC
                LIMIT 1;
                """
                cursor.execute(sql)
                results = cursor.fetchall()  # 최신 model_id에 해당하는 모든 상품을 가져옴

                if not results:
                    raise HTTPException(status_code=404, detail="No results found")

                # pandas dataframe으로 변환
                df = pd.DataFrame(results)

    except (pymysql.MySQLError, mariadb.Error) as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    # 리턴 값을 JSON 형태로 Streamlit에 보내기
    return df.to_json(orient="records")



    ### SQL SELECT 사용해서 예측여부가 True인 것들 중 id 값이 가장 큰 것 가지고 오기
    ### goods, model 을 join 하고 key 값은 외래키 model_id
    ### SELECT 문의 return 값이 있겠쥬
    ### 위 리턴값을 json 형태로 streamlit에 보내주기 (return 뒤에 써주면 됨)
    ### 그 전에 확인 : 리턴값을 pd.dataframe(리턴값) 했을 때 바로 가능하도록 만들어서 보내기

@app.post("/labels")
async def upload_image(request: Request):

    labels = await request.json()  # JSON으로 요청 본문 읽기
    print(labels)  # 받은 데이터 출력

    try:
        label_data = json.loads(labels)  # labels는 문자열로 전달되기 때문에 JSON으로 변환
        conn = pymysql.connect(**DB_CONFIG)
        with conn:
            with conn.cursor() as cursor:
                for item in label_data['labels']:
                    sql = """
                    INSERT INTO labels (name, cnt, won)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    cnt = VALUES(cnt), won = VALUES(won);
                    """
                    # item에서 각각의 필드를 추출하여 SQL에 적용
                    cursor.execute(sql, (item['nm'], item['cnt'], item['unitprice']))

                conn.commit()

    except (pymysql.MySQLError, mariadb.Error) as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    return {"message": "success"}

### SQL INSERT 사용해서 Label 테이블에 변경된 데이터를 고치기
### return에는 간단하게 잘 보내졌다고 알려주삼 ex) message : success

@app.get("/accuracy")
async def get_accuracy_percentage():
    try:
        # DB 연결
        conn = pymysql.connect(**DB_CONFIG)
        with conn:
            with conn.cursor() as cursor:
                # SQL 쿼리: accuracy_scores 테이블에서 가장 최근 model_id에 대한 데이터 가져오기
                sql = """
                SELECT name_score, count_score, amount_score
                FROM accuracy_scores
                WHERE model_id = (SELECT MAX(model_id) FROM accuracy_scores)
                """
                cursor.execute(sql)
                results = cursor.fetchall()

                if not results:
                    raise HTTPException(status_code=404, detail="No accuracy data found for the model")

                # 맞은 수량 계산
                total_correct = sum(row[0] + row[1] + row[2] for row in results)  # 각 행의 name, count, amount 점수 합계
                total_possible = len(results) * 3  # 각 행당 3개의 점수 가능 (name_score, count_score, amount_score)

                # 정확도 비율 계산
                accuracy_percentage = (total_correct / total_possible) * 100

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 정확도 비율을 JSON으로 반환
    return {"accuracy_percentage": round(accuracy_percentage, 2)}