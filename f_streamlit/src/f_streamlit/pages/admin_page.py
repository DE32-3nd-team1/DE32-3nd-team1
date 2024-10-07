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
    transformed_data = {
        "nm": [item["nm"] for item in data],
        "unitprice": [item["unitprice"] for item in data],
        "cnt": [item["cnt"] for item in data],
        "price": [item["price"] for item in data]
    }

    #response = json.dumps(transformed_data, ensure_ascii=False, indent=4)
    df = pd.DataFrame(transformed_data)
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

def select_row():
    # 선택할 행 선택하기 (인덱스 선택)
    selected_row_index = st.selectbox("행을 선택하세요:", df.index)

    # 선택된 행 데이터 출력
    if selected_row_index is not None:
        st.subheader(f"선택된 행 (인덱스: {selected_row_index})")
        st.write(df.loc[selected_row_index])
        return df.loc[selected_row_index]
    
    return []

def select_rows():
    selected_rows = st.multiselect(
        "선택할 상품을 고르세요:",
        options=df.index,
        #format_func=lambda x: df.at[x, x.index]
    )
    if st.button("선택완료", key="submit_button"):
        # 버튼 클릭 시 선택된 행을 반환
        if selected_rows:
            return selected_rows
        else:
            return [0]
    return None  # 버튼 클릭 전에 반환할 기본값

# request하기 -> 에측 여부가 true인 것 중 제일 마지막 
df = request_model_result()

# 레이아웃 설정
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# 왼쪽 상단 - 사진 출력
with col1:
    file_path="/home/kim/code/DE32-3nd-team1/f_streamlit/src/f_streamlit/test.png"
    from PIL import Image # 위에서 선언 후 사용해야한다.

    img = Image.open(file_path)
    st.image(img)
    #show_imag기e()

l = [0]
# 오른쪽 상단 - JSON 출력
with col2:
    st.header("예측 결과")

    st.dataframe(df)
    #goods+model 테이블 join한 것을 조회 :
    l = select_rows()
    if l is None:
        l = [0]
    #print(df)
    #l = df.index.to_list()

selected_section = st.sidebar.selectbox("섹션을 선택하세요:", l)

#각 섹션에 대한 내용 정의
if selected_section == l[0]:
    st.header("홈")
    st.write("여기는 홈 페이지입니다.")

elif selected_section == "데이터 업로드":
    st.header("데이터 업로드")
    uploaded_file = st.file_uploader("파일을 업로드하세요", type=["csv", "txt"])
    if uploaded_file is not None:
        st.success("파일이 업로드되었습니다.")

elif selected_section == "예측 결과":
    st.header("예측 결과")
    st.write("여기에서 예측 결과를 확인할 수 있습니다.")
    # 예측 결과에 대한 추가 코드를 여기에 추가

elif selected_section == "정정":
    st.header("정정")
    st.write("정정할 내용을 입력하세요.")
    # 정정 입력에 대한 추가 코드를 여기에 추가

# 제출 버튼 생성
if st.button("제출"):
    if labels:
        print("url 요청")
        print(labels)
        response = submit_labels_to_api(labels)
        st.success("정정 데이터를 성공적으로 제출했습니다.")
    else:
        st.warning("제출할 데이터가 없습니다.")
