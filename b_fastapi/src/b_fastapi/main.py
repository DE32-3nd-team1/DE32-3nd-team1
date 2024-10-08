from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
import os
import shutil
import pymysql
from datetime import datetime
import uuid
import pandas as pd
import json

app = FastAPI()

# 데이터베이스 설정
DB_CONFIG = {
    "host": os.getenv("DB", "43.203.236.175"),
    "user": "team1",
    "password": "1234",
    "database": "team1",
    "port": int(os.getenv("DB_PORT", 53306)),
    "cursorclass": pymysql.cursors.DictCursor
}
# 업로드 디렉토리 설정 (환경 변수에서 가져오거나 기본값 사용)
upload_directory = os.getenv('UPLOAD_DIR', ' home/ubuntu/images')
# 이미지 업로드 엔드포인트
@app.post("/upload_image/")
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
            shutil.copyfileobj(file.file, f)
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
                sql = """
                    INSERT INTO model (purchase_date, weekday, predict_bool, img_src)
                    VALUES (%s, %s, %s, %s)
                """
                predict_bool = False  
                cursor.execute(sql, (purchase_date.strftime("%Y-%m-%d %H:%M:%S"), weekday, predict_bool, img_src))
                conn.commit()
                insert_row_count = cursor.rowcount  # 삽입된 행 수 확인
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")

    # 업로드 결과 반환
    return {
        "status": "success",
        "filename": file.filename,
        "file_location": img_src,
        "purchase_date": purchase_date.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday": weekday,
        "insert_row_count": insert_row_count,
    }
@app.post("/model_result/")
async def get_model_result(
    predict: bool = Form(...),  # Form 필드로 예측 여부를 받음
):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn:
            with conn.cursor() as cursor:
                # SQL 쿼리: 예측 여부가 True이고 id 값이 가장 큰 레코드 조회
                sql = """
                SELECT g.id, g.model_id, g.name, g.cnt, g.won, m.id AS model_id, m.purchase_date, m.weekday, m.predict_bool, m.img_src
                FROM goods g
                JOIN model m ON g.model_id = m.id
                WHERE m.predict_bool = TRUE
                ORDER BY m.id DESC
                LIMIT 1;
                """
                cursor.execute(sql)
                result = cursor.fetchone()  # 가장 큰 id 하나만 가져옴, 쿼리결과

                if not result:
                    raise HTTPException(status_code=404, detail="No results found")

                # pandas dataframe으로 변환
                df = pd.DataFrame([result])

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 리턴 값을 JSON 형태로 Streamlit에 보내기
    return df.to_json(orient="records")
    

    ### SQL SELECT 사용해서 예측여부가 True인 것들 중 id 값이 가장 큰 것 가지고 오기
    ### goods, model 을 join 하고 key 값은 외래키 model_id
    ### SELECT 문의 return 값이 있겠쥬
    ### 위 리턴값을 json 형태로 streamlit에 보내주기 (return 뒤에 써주면 됨)
    ### 그 전에 확인 : 리턴값을 pd.dataframe(리턴값) 했을 때 바로 가능하도록 만들어서 보내기

@app.post("/labels/")
async def update_labels(
    labels: str = Form(...),
):
    print(labels)
    labels = labels.replace("'",'"')  # 문자열에서 작은따옴표를 큰따옴표로 변환
    try:
        label_data = json.loads(labels)  # labels는 문자열로 전달되기 때문에 JSON으로 변환
        label_data = label_data['labels']
        
        # 모델에서 예측된 가장 최근의 id를 가져오는 쿼리
        conn = pymysql.connect(**DB_CONFIG)
        with conn:
            with conn.cursor() as cursor:
                # 가장 최근의 id 값을 가져오는 쿼리 실행
                sql_get_id = """
                    SELECT m.id
                    FROM model m
                    WHERE m.predict_bool = TRUE
                    ORDER BY m.id DESC
                    LIMIT 1;
                """
                cursor.execute(sql_get_id)
                result = cursor.fetchone()

                if not result:
                    raise HTTPException(status_code=404, detail="No model result found with predict_bool=True")
                
                # 가져온 id를 변수에 저장
                model_id = result['id']

                # 라벨 데이터를 업데이트하는 쿼리
                for item in label_data:
                    sql_update = """
                    UPDATE labels
                    SET name = %s, cnt = %s, won = %s
                    WHERE goods_id = %s;
                    """
                    # UPDATE 쿼리에 model_id를 조건으로 추가
                    cursor.execute(sql_update, (item['nm'], item['cnt'], int(item['unitprice'].replace(",", "")), model_id))

                conn.commit()

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {"message": "success"}

### SQL INSERT 사용해서 Label 테이블에 변경된 데이터를 고치기
### return에는 간단하게 잘 보내졌다고 알려주삼 ex) message : success

