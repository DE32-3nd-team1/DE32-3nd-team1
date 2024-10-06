import streamlit as st
import pandas as pd
import numpy as np

# 데이터 생성: 날짜와 랜덤 데이터를 가진 데이터프레임
dates = pd.date_range(start="2024-01-01", periods=100)
data = pd.DataFrame(np.random.randn(100, 3), index=dates, columns=["Column A", "Column B", "Column C"])

# 데이터프레임 출력
st.write("Generated DataFrame:", data)

# 꺾은선 그래프 그리기
st.line_chart(data)
