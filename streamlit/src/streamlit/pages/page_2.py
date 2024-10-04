import streamlit as st
import pandas as pd
import numpy as np

# 임의의 데이터 생성 (5일 동안 3개의 열로 구성된 데이터)
dates = pd.date_range(start='2024-10-01', periods=5)
data = pd.DataFrame(
    np.random.randn(5, 3),  # 5일 동안 3개의 열에 랜덤한 값 생성
    index=dates,
    columns=['Category A', 'Category B', 'Category C']
)
st.header("Right Side")
st.write("This is the content of the right side.")
st.line_chart(data)
