import streamlit as st
from datetime import date, datetime
import json

def save_uploaded_file(directory, file) :
    # 1. 디렉토리가 있는지 확인하여, 없으면 먼저, 디렉토리부터 만든다.
    if not os.path.exists(directory) :
        os.makedirs(directory)

    # 2. 디렉토리가 있으니, 파일을 저장한다.
    with open(os.path.join(directory, file.name), 'wb') as f:
        f.write(file.getbuffer())

    # 3. 파일 저장이 성공했으니, 화면에 성공했다고 보여주면서 리턴
    return st.success('{} 에 {} 파일이 저장되었습니다.'.format(directory, file.name))

def get_predict():
    sample_data = {
        "name": "John",
        "age": 30,
        "city": "New York"
    }
    return json_data

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
user_text = st.text_area("여기에 텍스트를 입력하세요")
if user_text:
    st.write(f"입력된 텍스트: {user_text}")
