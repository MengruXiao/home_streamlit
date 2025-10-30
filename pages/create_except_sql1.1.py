import streamlit as st
import pandas as pd


def except_sql_fun(df, table_name_basic,table_name_compare):

    column_names = df["column_name"].tolist()
    column_names_all = (',\n    '.join(column_names))
     
    except_sql1 = f'''
select 
    {column_names_all}    
from  {table_name_basic} 

EXCEPT

select 
    {column_names_all}    
from  {table_name_compare};

     '''

    except_sql2 = f'''
select 
    {column_names_all}    
from  {table_name_compare} 

EXCEPT

select 
    {column_names_all}    
from  {table_name_basic};

     '''
    sql = except_sql1+'\n'+'\n'+except_sql2

    return sql


st.title('except对比语句快速创建')

text_input1 = st.text_area('输入您的基础表DDL', '')
text_input2 = st.text_area('输入对比表名(默认两表的ddl一样)', '')
text_input3 = st.text_area('输入需要忽略的字段(多个字段用逗号分隔，例如: field1,field2,field3)', '')

if st.button('处理并导出'):
        
        if text_input1 and text_input2:
                
                lines = text_input1.splitlines()

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
                    # 处理需要忽略的字段
                    ignore_fields = []
                    if text_input3:
                        # 去除空格并分割字段
                        ignore_fields = [field.strip() for field in text_input3.split(',') if field.strip()]
                        st.info(f'将忽略以下字段: {", ".join(ignore_fields)}')
                    
                    df = pd.DataFrame(columns, columns=['column_name','type'])
                    
                    # 过滤掉需要忽略的字段
                    if ignore_fields:
                        df = df[~df['column_name'].isin(ignore_fields)]
                        st.write(f'原始字段数: {len(columns)}, 过滤后字段数: {len(df)}')
                    
                    if len(df) > 0:
                        st.write('生成的except语句为:')
                        table_name_basic = lines[0].split(' ')[2]
                        table_name_compare = text_input2
                        sql = except_sql_fun(df, table_name_basic,table_name_compare)
                        st.code(sql, language='sql')
                    else:
                        st.warning('过滤后没有剩余字段，请检查忽略字段列表。')
                        

                else:
                    st.warning('没有找到有效的字段定义。')

        else:

            st.warning('两个框都要输入')

else:
    st.warning('请先输入ddl')


