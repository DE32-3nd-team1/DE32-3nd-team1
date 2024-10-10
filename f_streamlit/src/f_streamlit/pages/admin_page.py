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
m_id = -1

# 예측결과가 True인 것들 중에서 num의 값이 가장 큰 것
def request_model_result():
    global m_id
    global file_path
    try:
        url = f"{base_url}/model_result"
        r_response = requests.get(url, params={"key1": "1"})  # 키를 적절히 수정하세요
    #response = [{"id":5,"model_id":1,"name":"샀원명","cnt":1,"won":1500,"m.id":1,"purchase_date":"2024-10-07 00:00:00","weekday":"","predict_bool":1,"img_src":"home/ubuntu/images/test1.png"}]
        # 빈 DataFrame 생성
        response = r_response.json()
        #print(response)
        response_list = json.loads(response)
        print(response_list)
        rows = len(response_list[0])
        file_path = response_list[0].get(str(0), None)['img_src']
        print(file_path)
        m_id = int(response_list[0].get(str(0), None)['model_id']
         
        df = pd.DataFrame(columns=['goods_id','nm', 'cnt', 'unitprice'])

        # 데이터 추가를 위한 리스트 생성
        data_list = []  # 새롭게 추가할 데이터 저장 리스
        for i in range(rows):
        # 각 항목에 접근
            data = response_list[0].get(str(i), None)
            print(data)
            # 각 항목을 딕셔너리로 변환
            data_dict = {
                'goods_id' : data['id'],
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
        df1 = pd.DataFrame(df)
        print(df1)
        print("===="*33)
        print(m_id)

        return df1

    except Exception as e:
        print(e)
        if r_response.status_code != 200:
            print(e)
            data = {"nm": ["현대)더커진진주탱초불그룹", "동아)박카스밧텡크릴리40g", "서울)커피우유300ml"],"unitprice": ["1,700", "2,500", "2,000"],"cnt": ["1", "1", "1"],"price": ["1,700", "2,500", "8,545"]}
            #print(type(data))
            df = pd.DataFrame(data)
            file_path = "./test.jpg"
            return df

def submit_labels_to_api(r_labels):
    global m_id 
    url = f"{base_url}/labels"

    labels = json.loads(r_labels)

    payload = {"labels" : labels, "model_id" : m_id }
    json_data = json.dumps(payload, ensure_ascii=False)
    
    response = requests.post(url, json=json_data)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to submit datetime"}

# request하기 -> 에측 여부가 true인 것 중 제일 마지막 
df = request_model_result()
# 레이아웃 설정
col1, col2 = st.columns(2)

l = [0]

with col1:
    st.header("예측 결과")
    st.dataframe(df)

with col2:
    st.header("정정할 데이터")
    
    edited_df = st.data_editor(df, num_rows="dynamic", key="editable_table")
    col3, col4 = st.columns(2)
        # '변경 완료' 버튼
    with col3:
        try:    
            if st.button("변경본 제출"):
                print("url 요청 - 수정된 데이터")
                # 수정된 데이터 전송 로직 추가
                edited_df = pd.DataFrame(edited_df)
                json_data = edited_df.to_json(orient="records", force_ascii=False)
                response = submit_labels_to_api(json_data)
                st.success("정정 데이터를 성공적으로 제출했습니다.")
        except Exception as e:
            print(e)
            st.write("잠시 후에 다시 시도해주세요")
    with col4:
        try:
        # '그대로 제출' 버튼
            if st.button("원본 제출"):
                print("url 요청 - 원본 데이터")
                # 원본 데이터 전송 로직 추가
                json_data = df.to_json(orient="records", force_ascii=False)
                response = submit_labels_to_api(json_data)
                st.success("기본 데이터를 성공적으로 제출했습니다.")
        except Exception as e:
            print(e)
            st.write("잠시 후에 다시 시도해주세요")

# 이미지 파일을 불러오는 로직
if file_path == "":
    img = Image.open(t_file_path)
    print(t_file_path)
else:
    img = Image.open(file_path)
    print(file_path)

# 이미지 출력
st.image(img)
