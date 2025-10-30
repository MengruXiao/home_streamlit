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
                    st.write('生成的except语句为:')
                    df = pd.DataFrame(columns, columns=['column_name','type'])
                    # st.dataframe(df)
                    table_name_basic = lines[0].split(' ')[2]
                    table_name_compare = text_input2
                    sql = except_sql_fun(df, table_name_basic,table_name_compare)
                    st.code(sql, language='sql')                          
                        

                else:
                    st.warning('没有找到有效的字段定义。')

        else:

            st.warning('两个框都要输入')

else:
    st.warning('请先输入ddl')


