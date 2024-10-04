import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import datetime as dt
import numpy as np

st.title("CNN JOB MON")

def send2url():
    # 서버로 보낼 URL 정의
    url = "https://127.0.0.1:8002"  # 실제로 데이터를 보낼 URL
    # 버튼을 클릭하면 POST 요청을 보냄
    if st.button("Send Message"):
        if user_input:
            # 보낼 데이터를 정의
            data = {"message": user_input}

            try:
                # POST 요청 보내기
                response = requests.post(url, json=data)

                # 응답 처리
                if response.status_code == 200:
                    st.success("Message sent successfully!")
                else:
                    st.error(f"Failed to send message. Status code: {response.status_code}")                                                                                          except Exception as e:
            st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a message before sending.")

def load_data():
    d = "hello streamlit"
    return d

data = load_data()
print(data)

st.text(data)
