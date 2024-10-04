import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import datetime as dt
import numpy as np

st.title("CNN JOB MON")

def send2url(user_input):
    # 서버로 보낼 URL 정의 (로컬 서버)
    url = "http://127.0.0.1:8002"  # 실제로 데이터를 보낼 URL

    # 버튼을 클릭하면 POST 요청을 보냄
    if st.button("Send Message"):
        if user_input:
            # 보낼 데이터를 정의 (JSON 형식)
            data = {"message": user_input}

            try:
                # POST 요청 보내기
                response = requests.post(url, json=data)

                # 응답 처리
                if response.status_code == 200:
                    st.success("Message sent successfully!")
                else:
                    st.error(f"Failed to send message. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a message before sending.")

# 사용자로부터 입력을 받음
my_input = st.text_input("입력하세요")

# 입력한 내용을 출력
st.write("입력한 내용:", my_input)

# 입력 내용을 서버로 전송
send2url(my_input)

