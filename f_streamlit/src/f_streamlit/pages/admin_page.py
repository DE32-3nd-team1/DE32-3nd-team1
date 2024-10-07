import streamlit as st
from datetime import date, datetime
import json
from f_streamlit.st_module import save_uploaded_file, get_predict, check_box_input
from PIL import Image # 위에서 선언 후 사용해야한다.

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

# request하기 -> 에측 여부가 false인 것들 -> dataframe으로 변환 후에 보여주기


# 레이아웃 설정
col1, col2 = st.columns(2)

# 왼쪽 상단 - 사진 출력
with col1:
    file_path="/home/kim1/code/DE32-3nd-team1/f_streamlit/src/f_streamlit/test.png"
    from PIL import Image # 위에서 선언 후 사용해야한다.

    img = Image.open(file_path)
    st.image(img)
    #show_image()

# 오른쪽 상단 - JSON 출력
with col2:
    st.header("예측 결과")
    
    json_data = get_predict()

    keys = get_keys(json_data)
    values = get_values(json_data)
    for key,value in zip(keys,values):
        st.write(f"{key} : {value}")
    #st.json(data)

# 하단 - 텍스트 입력
st.header("정정 ")
l = ["name", "age", "city"]
for i in l:
    check_box_input(i)
