import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import datetime as dt
import numpy as np
import os

st.title("CNN JOB MON")

def send2url(user_input, url="http://172.17.0.1:8002"):
    print(url)
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
#AWS
#send2url(my_input, "http://172.31.32.196:8002")

#local
send2url(my_input, "http://172.0.0.1:8002")
