import streamlit as st
from datetime import date, datetime
import json
from f_streamlit.st_module import save_uploaded_file, get_predict, check_box_input
from PIL import Image # 위에서 선언 후 사용해야한다.
import pandas as pd
import requests

def show_image(file_path="/home/kim1/code/DE32-3nd-team1/f_streamlit/src/f_streamlit/test.png"):
    from PIL import Image # 위에서 선언 후 사용해야한다.
    
    img = Image.open(file_path)
    st.image(img)

def get_keys(json_data):
    # 키값만 추출하여 리스트로 만들기
    keys_list = list(json_data.keys())
    return keys_list

def get_values(json_data):
    values_list = list(json_data.values())
    return values_list

def request_model_result():
    url = "http://127.0.0.1:8002/model_result" 

    #response = requests.get(url,data,payload)
    # 주어진 딕셔너리
    data = [
        {
            "nm": "현대)더커진진주탱초불그룹",
            "unitprice": "1,700",
            "cnt": "1",
            "price": "1,700"
        },
        {
            "nm": "동아)박카스밧텡크릴리40g",
            "unitprice": "2,500",
            "cnt": "1",
            "price": "2,500"
        },
        {
            "nm": "서울)커피우유300ml",
            "unitprice": "2,000",
            "cnt": "1",
            "price": "8,545"
        }
    ]

    response = json.dumps(data, ensure_ascii=False, indent=4)
    print(response)
    df = pd.DataFrame(response)
    print(df)
    return df

def submit_labels_to_api(labels):
    url = "http://127.0.0.1:8002/labels/"

    # 파일 전송을 위한 multipart/form-data 준비
    payload = {
        "temp" : "temp",
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to submit datetime"}

# request하기 -> 에측 여부가 true인 것 중 제일 마지막 
df = request_model_result()

# 레이아웃 설정
col1, col2 = st.columns(2)

# 왼쪽 상단 - 사진 출력
with col1:
    file_path="/home/kim1/code/DE32-3nd-team1/f_streamlit/src/f_streamlit/test.png"
    from PIL import Image # 위에서 선언 후 사용해야한다.

    img = Image.open(file_path)
    st.image(img)
    #show_imag기e()

# 오른쪽 상단 - JSON 출력
with col2:
    st.header("예측 결과")

    st.dataframe(df)
    #goods+model 테이블 join한 것을 조회 :
    #json_data = get_predict()
    
    #keys = get_keys(json_data)
    #values = get_values(json_data)
    #for key,value in zip(keys,values):
    #    st.write(f"{key} : {value}")

# 하단 - 텍스트 입력
st.header("정정 ")
l = ["name", "age", "city"]
labels = {}

for i in l:
    correct = check_box_input(i)
    if correct is not None:  # None이 아닐 때만 추가
        labels[i] = correct

submit_labels_to_api(labels)
#response 보내
