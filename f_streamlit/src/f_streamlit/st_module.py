import streamlit as st

def save_uploaded_file(directory, file):
    # 1. 디렉토리가 있는지 확인하여, 없으면 먼저, 디렉토리부터 만든다.    if not os.path.exists(directory) :
    os.makedirs(directory)

    # 2. 디렉토리가 있으니, 파일을 저장한다.
    with open(os.path.join(directory, file.name), 'wb') as f:
        f.write(file.getbuffer())

    # 3. 파일 저장이 성공했으니, 화면에 성공했다고 보여주면서 리턴
    return st.success('{} 에 {} 파일이 저장되었습니다.'.format(directory, file.name))

def get_predict():
    json_data = {
        "name": "John",
        "age": 30,
        "city": "New York"
    }
    return json_data

def check_box_input(which : str):
    # 체크박스 생성
    is_checked = st.checkbox(f"{which}", key=f"check_submit_{which}")

    # 체크박스 상태에 따라 메시지 출력
    if is_checked:
        user_text = st.text_input(f"{which}")
        return user_text

def json2dataframe(json):
    df = pd.dataframe(json)
    return df
 
