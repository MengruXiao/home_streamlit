import streamlit as st
import pandas as pd



def delete_and_insert_sql_fun(df,table_name):

    staging_table_name = table_name.split(".")[0] + '.staging_' + table_name.split(".")[1]

    column_names = df["column_name"].tolist()
    column_names_all = (',\n    '.join(column_names))


    # filtered_df = df[df['type'] != 'varchar(1000)']
    insert_sql = f'''
insert into {table_name} 
(
    {column_names_all}    
)
select

     '''

    filtered_df_dict = dict(zip(df["column_name"], df["type"]))

    for column_name, type in filtered_df_dict.items():

        if not type.startswith('varchar'):
            insert_sql += f"cast({column_name} as {type}),\n    "
        else:
            insert_sql += f"{column_name},\n    "

    insert_sql = insert_sql[:-6] + f"\nfrom {staging_table_name};"



    delete_sql = f'''delete from {table_name} \nwhere id in (select id from {table_name.split(".")[0]}.staging_{table_name.split(".")[1]});'''


    sql = delete_sql+'\n'+'\n'+insert_sql



    return sql





st.title('table_ddl_提取字段及其类型')

# 目前只支持redshift的ddl, snowflake或者mssql或者其他的后续再说
# 选择功能
function = st.selectbox('选择sql类型', ['redshift', 'snowflake'])

# 添加一个输入框和一个粘贴按钮
text_input = st.text_area('输入您的 DDL 语句', '')

if st.button('处理并导出'):

    if text_input:
        # 读取文件内容
        lines = text_input.splitlines()

        if function == 'redshift':
            columns = []
            for line in lines[1:]:
                if line.strip().startswith(')'):
                    break
                if ", " in line:
                    line = line.replace(', ', ',')
                parts = line.strip().split(' ')
                if len(parts) >= 2:
                    column_name = parts[0]
                    if parts[1] == 'character':
                        type = parts[2].replace('varying', 'varchar')
                    elif parts[1] == 'timestamp':
                        type = 'datetime'
                    elif parts[1] == 'integer':
                        type = 'int'
                    else:
                        type = parts[1]
                    columns.append((column_name, type))

            if columns:
                st.write('提取的字段及其类型:')
                df = pd.DataFrame(columns, columns=['column_name','type'])
                st.dataframe(df)
                table_name = lines[0].split(' ')[2]
                sql = delete_and_insert_sql_fun(df, table_name)
                st.code(sql, language='sql')


            else:
                st.warning('没有找到有效的字段定义。')


        else:

            st.warning('前面的道路以后再来探索吧~')

else:
    st.warning('请先输入ddl')