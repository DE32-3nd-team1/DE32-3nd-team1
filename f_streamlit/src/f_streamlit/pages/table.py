import streamlit as st
import pandas as pd
import requests

def check_box_input(which : str):
    # 체크박스 생성
    is_checked = st.checkbox(f"{which}")

    # 체크박스 상태에 따라 메시지 출력
    if is_checked:
        st.write(f"{which} is checked!")
        user_text = st.text_input(f"{which} : ")

# FastAPI에서 데이터프레임 가져오기
response = requests.get("http://127.0.0.1:8002/show_predicts/")
print(response)
data = response.json()

df = pd.DataFrame(data)

# DataFrame을 Streamlit에 표시
st.header("표에서 특정 행 선택하기")
st.dataframe(df)

# 선택할 행 선택하기 (인덱스 선택)
selected_row_index = st.selectbox("행을 선택하세요:", df.index)
st.write(df.loc[selected_row_index]['이름'])

# 선택된 행 데이터 출력
if selected_row_index is not None:
    st.subheader(f"선택된 행 (인덱스: {selected_row_index})")
    st.write(df.loc[selected_row_index])
