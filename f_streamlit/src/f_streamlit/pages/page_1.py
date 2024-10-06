import streamlit as st
from datetime import date, datetime
import json
from f_streamlit.st_module import save_uploaded_file, get_predict, check_box_input

# 레이아웃 설정
col1, col2 = st.columns(2)

# 왼쪽 상단 - 이미지 입력
with col1:
    st.header("이미지 업로드")
    uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="업로드된 이미지", use_column_width=True)
    

# 오른쪽 상단 - JSON 출력
with col2:
    st.header("예측 결과")
    data = get_predict()
    st.json(data)

# 하단 - 텍스트 입력
st.header("정정 ")

check_box_input("name")
check_box_input("age")
check_box_input("city")
