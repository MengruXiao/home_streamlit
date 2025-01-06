import streamlit as st
import pandas as pd
import json
from pathlib import Path


COLS_NUM = 4
MAX_TEMP_FILES = 10
single_TEST_EXCEL = Path("static/接单张模板.xlsx")
more_TEST_EXCEL = Path("static/接多张模板.xlsx")


def download_button(button_name:str, file_path: Path, file_type: str) -> None:
    try:
        with open(file_path, "rb") as file:
            file_bytes = file.read()
        if file_type in ['xlsx','zip','json']:
            if file_type == 'xlsx':
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file_type == 'zip':
                mime_type = "application/zip"
            elif file_type == 'json':
                mime_type = "application/json"
            else:
                st.error(f"file_type: {file_type}. Unsupported file type.")
                mime_type = "text/plain"
            st.download_button(
                label=button_name,
                data=file_bytes,
                file_name=file_path.name,
                mime=mime_type
            )
        else:
            st.error(f"file_type: {file_type}. Unsupported file type.")
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")

def main():

    st.title("id类型的接数mapping_用于非SCI")

    st.markdown(
        """
        1)上传的xlsx里得自己配上系统字段,id不用配
        2)配多张就在一个sheet页里往下写就好
        """
    )

    download_button("单张模板下载", single_TEST_EXCEL, 'xlsx')
    download_button("多张模板下载", more_TEST_EXCEL, 'xlsx')

    # 文件上传
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")


    if uploaded_file is not None:
        # 转换为 JSON
        df = pd.read_excel(uploaded_file, sheet_name='Sheet1')
        df['derive_desc'] = df['derive_desc'].fillna('None')

        json_data = df.to_dict(orient='records')



        start_id = st.number_input("Input Start Number:  :rainbow[[id]]", value=1,
                                   placeholder="Type a number...", step=1)

        for index, item in enumerate(json_data, start=start_id):
                item["id"] = str(index)




        # 下载 JSON 文件
        json_str = json.dumps(json_data, indent=4)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="output.json",
            mime="application/json"
        )

        # 显示 JSON 数据
        st.json(json_data)


if __name__ == "__main__":
    main()