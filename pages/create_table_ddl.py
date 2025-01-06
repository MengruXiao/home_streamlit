import streamlit as st
import pandas as pd
import io
from pathlib import Path


COLS_NUM = 4
MAX_TEMP_FILES = 10
more_TEST_EXCEL = Path("static/ddl_模板.xlsx")



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


def parse_excel(file):
    try:
        df = pd.read_excel(file, header=None)
        if df.empty:
            raise ValueError("Excel文件为空")
            
        tables = []
        current_table = None

        for index, row in df.iterrows():
            # 跳过完全为空的行
            if row.isna().all():
                if current_table and current_table['columns']:  # 如果遇到空行且当前表有内容，保存当前表
                    tables.append(current_table)
                    current_table = None
                continue

            first_cell = str(row[0]).strip() if not pd.isna(row[0]) else ""
            
            if first_cell.startswith('目标表:'):
                # 如果已经有一个表在处理中，先保存它
                if current_table and current_table['columns']:
                    tables.append(current_table)
                
                table_name = first_cell.split(":")[1].strip()
                if not table_name:
                    raise ValueError(f"第{index + 1}行的表名为空")
                current_table = {'table_name': table_name, 'columns': []}
            elif current_table is not None and first_cell:
                column_name = first_cell
                column_type = str(row[1]).strip() if not pd.isna(row[1]) else ""
                if not column_type:
                    raise ValueError(f"第{index + 1}行的字段类型为空")
                current_table['columns'].append((column_name, column_type))

        # 确保最后一个表也被添加
        if current_table and current_table['columns']:
            tables.append(current_table)
            
        if not tables:
            raise ValueError("未找到有效的表结构定义")
            
        return tables
    except Exception as e:
        st.error(f"解析Excel文件时出错: {str(e)}")
        return None

def generate_sql(tables):
    if not tables:
        return []
        
    sql_statements = []
    for table in tables:
        # 添加表名注释
        sql = f"-- 创建表 {table['table_name']}\n"
        columns = ',\n'.join([f"    {col} {typ}" for col, typ in table['columns']])
        sql += f"CREATE TABLE {table['table_name']} (\n{columns}\n);\n"
        sql_statements.append(sql)
    return sql_statements

def main():
    st.title("Excel to SQL Create Table Statements")
    st.write("请上传一个Excel文件，文件格式要求：")
    st.write("- 第一行为表名（以'目标表:'开头）")
    st.write("- 从第二行开始：左边第一列是字段名，第二列为字段类型")
    st.write("- 支持在一个sheet页里出现多张表的配置,表与表之间空行间隔,至少一行空行")
    download_button("多张模板下载", more_TEST_EXCEL, 'xlsx')
    file = st.file_uploader("上传Excel文件", type=["xlsx"])

    if file is not None:
        tables = parse_excel(file)
        if tables:
            sql_statements = generate_sql(tables)
            
            if sql_statements:
                st.header("生成的SQL语句")
                for sql in sql_statements:
                    st.code(sql, language='sql')

                sql_content = '\n'.join(sql_statements)
                
                st.download_button(
                    label="下载SQL文件",
                    data=sql_content,
                    file_name="create_tables.sql",
                    mime="text/plain",
                    help="点击下载生成的SQL文件"
                )
            else:
                st.warning("没有生成任何SQL语句")








if __name__ == "__main__":
    main()