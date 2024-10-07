import streamlit as st
from datetime import date, datetime,time
import json
from f_streamlit.st_module import save_uploaded_file, get_predict, check_box_input
import requests

# FastAPI 서버로 datetime을 전송하는 함수
def submit_img_datetime_to_api(file, date, time, weekday):
    url = "http://127.0.0.1:8002/upload_image/"
    
    # 파일 전송을 위한 multipart/form-data 준비
    files = {
        "file": (file.name, file, file.type)
    }
    payload = {
        "date": date.strftime("%Y-%m-%d"),  # 날짜를 문자열로 변환
        "time": time.strftime("%H:%M:%S"),  # 시간을 문자열로 변환
        "weekday": weekday,
    }

    response = requests.post(url, files=files, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to submit datetime"}


st.header("이미지 업로드")
date = st.date_input("When did you take a picture", value=None)
time = st.time_input("Select a time", value=time(12, 0))

uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["png", "jpg", "jpeg"])
if uploaded_file:
    st.image(uploaded_file, caption="업로드된 이미지", use_column_width=True)
weekday = ""
if date:
    # 입력된 날짜의 요일 구하기
    weekday = date.strftime("%A")  # 요일을 문자열로 추출 (예: "Monday")
    # 요일 출력
    #st.write(f"The selected day is: {weekday}")

# 모든 값이 입력된 경우 FastAPI로 전송
if all([uploaded_file, date, time]):
    # FastAPI 서버로 POST 요청 보내기
    response = submit_img_datetime_to_api(uploaded_file,date,time, weekday)

    # 서버 응답 출력
    if "error" in response:
        st.write(response["error"])
    else:
        st.write("File uploaded successfully!")
