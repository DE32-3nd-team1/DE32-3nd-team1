import streamlit as st
from datetime import date, datetime
import json
from PIL import Image # 위에서 선언 후 사용해야한다.
import pandas as pd
import requests
import os

# 현재 파일의 절대 경로 확인
current_file_path = os.path.dirname(os.path.abspath(__file__))

# 이미지 파일의 경로 설정
base_url = os.getenv("FASTAPI_URL") + ":" + str(os.getenv("FASTAPI_PORT"))
t_file_path = os.path.join(current_file_path, "test.jpg")  # 경로 안전하게 결합

file_path = ""

# 예측결과가 True인 것들 중에서 num의 값이 가장 큰 것
def request_model_result():
    url = f"{base_url}/model_result"
    response = requests.get(url, params={"key1": "1", "key2": "1"})  # 키를 적절히 수정하세요
    #response = [{"id":5,"model_id":1,"name":"샀원명","cnt":1,"won":1500,"m.id":1,"purchase_date":"2024-10-07 00:00:00","weekday":"","predict_bool":1,"img_src":"home/ubuntu/images/test1.png"}]
   
    if response.status_code != 200:
        data = {"nm": ["현대)더커진진주탱초불그룹", "동아)박카스밧텡크릴리40g", "서울)커피우유300ml"],"unitprice": ["1,700", "2,500", "2,000"],"cnt": ["1", "1", "1"],"price": ["1,700", "2,500", "8,545"]}
        print(type(data))
        df = pd.DataFrame(data)

        file_path = "./test.jpg"

        return df

    # 빈 DataFrame 생성
    df = pd.DataFrame(columns=['nm', 'cnt', 'unitprice'])

    # 데이터 추가를 위한 리스트 생성
    data_list = []  # 새롭게 추가할 데이터 저장 리스트

    for data in response:
        # 각 항목을 딕셔너리로 변환
        data_dict = {
            'nm': data['name'],        # 'name' 값을 'nm'으로 매핑
            'cnt': data['cnt'],        # 'cnt' 값 추가
            'unitprice': data['won']   # 'won' 값을 'unitprice'로 매핑
        }
        # 리스트에 딕셔너리 추가
        data_list.append(data_dict)

    # 리스트를 DataFrame으로 변환
    new_df = pd.DataFrame(data_list)

    # 기존 DataFrame과 새로운 DataFrame을 pd.concat()으로 합치기
    df = pd.concat([df, new_df], ignore_index=True)

    # name, cnt, won를 데이터프레임이 넣기
    #response = json.dumps(transformed_data, ensure_ascii=False, indent=4)
    df1 = pd.DataFrame(df)

    file_path = response["img_src"]
    return df1,file_path

def submit_labels_to_api(labels):
    url = f"{base_url}/labels/"

    # 파일 전송을 위한 multipart/form-data 준비
    payload = {
        "labels" : labels,
    }

    #response = requests.post(url, json=payload)
    response = requests.post(url, json={"labels": json.loads(labels)})
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to submit datetime"}

def fit2dataframe(data):
    transformed_data = {
        "nm": [item["nm"] for item in data],
        "unitprice": [item["unitprice"] for item in data],
        "cnt": [item["cnt"] for item in data],
        "price": [item["price"] for item in data]
    }
    print(transformed_data)
    return transformed_data

# request하기 -> 에측 여부가 true인 것 중 제일 마지막 
df = request_model_result()

# 레이아웃 설정
col1, col2 = st.columns(2)

l = [0]

with col1:
    st.header("예측 결과")

    st.dataframe(df)
    if l is None:
        l = [0]

with col2:
    st.header("정정할 데이터")
    
    edited_df = st.data_editor(df, num_rows="dynamic", key="editable_table")
    col3, col4 = st.columns(2)
    # '변경 완료' 버튼
    with col3:
        if st.button("변경본 제출"):
            print("url 요청 - 수정된 데이터")
            # 수정된 데이터 전송 로직 추가
            edited_df = pd.DataFrame(edited_df)
            json_data = edited_df.to_json(orient="records", force_ascii=False)
            response = submit_labels_to_api(json_data)
            st.success("정정 데이터를 성공적으로 제출했습니다.")

    with col4:
        # '그대로 제출' 버튼
        if st.button("원본 제출"):
            print("url 요청 - 원본 데이터")
            # 원본 데이터 전송 로직 추가
            json_data = df.to_json(orient="records", force_ascii=False)
            response = submit_labels_to_api(json_data)
            st.success("기본 데이터를 성공적으로 제출했습니다.")


# 이미지 파일을 불러오는 로직
if file_path == "":
    img = Image.open(t_file_path)
else:
    img = Image.open(file_path)

# 이미지 출력
st.image(img)
