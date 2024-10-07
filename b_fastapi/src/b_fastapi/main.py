from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import os
import shutil
import pymysql
from datetime import datetime
import uuid

app = FastAPI()

# 데이터베이스 설정
DB_CONFIG = {
    "host": os.getenv("DB", "43.203.223.158"),
    "user": "team1",
    "password": "1234",
    "database": "team1",
    "port": int(os.getenv("DB_PORT", 53306)),
    "cursorclass": pymysql.cursors.DictCursor
}
# 업로드 디렉토리 설정 (환경 변수에서 가져오거나 기본값 사용)
upload_directory = os.getenv('UPLOAD_DIR', '/home/joo/code/DE32-3nd-team1/b_fastapi/uploaded_images')
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