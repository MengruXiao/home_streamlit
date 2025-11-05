import streamlit as st
import pandas as pd


def except_sql_fun(df, table_name_basic, table_name_compare, where_basic='', where_compare=''):

    column_names = df["column_name"].tolist()
    column_names_all = (',\n    '.join(column_names))
    
    # 构建基础表的WHERE子句
    where_clause_basic = f'\nwhere {where_basic}' if where_basic.strip() else ''
    # 构建对比表的WHERE子句
    where_clause_compare = f'\nwhere {where_compare}' if where_compare.strip() else ''
     
    except_sql1 = f'''
select 
    {column_names_all}    
from  {table_name_basic}{where_clause_basic}

EXCEPT

select 
    {column_names_all}    
from  {table_name_compare}{where_clause_compare};

     '''

    except_sql2 = f'''
select 
    {column_names_all}    
from  {table_name_compare}{where_clause_compare}

EXCEPT

select 
    {column_names_all}    
from  {table_name_basic}{where_clause_basic};

     '''
    sql = except_sql1+'\n'+'\n'+except_sql2

    return sql


st.title('except对比语句快速创建')

# 添加批量处理模式选择
processing_mode = st.radio('选择处理模式', ['单表对比', '批量对比'], horizontal=True)

if processing_mode == '单表对比':
    text_input1 = st.text_area('输入您的基础表DDL', '')
    text_input2 = st.text_area('输入对比表名(默认两表的ddl一样)', '')
    text_input3 = st.text_area('输入需要忽略的字段(多个字段用逗号分隔，例如: field1,field2,field3)', '')
    text_input4 = st.text_area('输入基础表的WHERE条件(可选，不需要写WHERE关键字)', '', 
                               help='例如: version_no = \'2025Q2V2\' and date > \'2024-01-01\'')
    text_input5 = st.text_area('输入对比表的WHERE条件(可选，不需要写WHERE关键字)', '',
                               help='例如: version_no = \'2025Q2V2\' and date > \'2024-01-01\'')
else:
    st.info('批量模式说明：每行输入一对表名，格式为 "基础表DDL|对比表名"，可选添加WHERE条件 "|基础表WHERE|对比表WHERE"')
    batch_input = st.text_area('批量输入表对（每行一对）', 
                               height=200,
                               help='格式示例：\nCREATE TABLE schema.table1...|schema.table2\nCREATE TABLE schema.table3...|schema.table4|version_no=\'2025Q2V2\'|version_no=\'2025Q2V2\'')
    text_input3 = st.text_area('输入需要忽略的字段(多个字段用逗号分隔，对所有表生效)', '')

def process_single_table(ddl_text, compare_table, ignore_fields, where_basic='', where_compare=''):
    """处理单个表对"""
    lines = ddl_text.splitlines()
    
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
    
    if not columns:
        return None, '没有找到有效的字段定义'
    
    df = pd.DataFrame(columns, columns=['column_name', 'type'])
    
    # 过滤掉需要忽略的字段
    if ignore_fields:
        df = df[~df['column_name'].isin(ignore_fields)]
    
    if len(df) == 0:
        return None, '过滤后没有剩余字段，请检查忽略字段列表'
    
    table_name_basic = lines[0].split(' ')[2]
    sql = except_sql_fun(df, table_name_basic, compare_table, where_basic, where_compare)
    
    return sql, None


if st.button('处理并导出'):
    if processing_mode == '单表对比':
        if text_input1 and text_input2:
            # 处理需要忽略的字段
            ignore_fields = []
            if text_input3:
                ignore_fields = [field.strip() for field in text_input3.split(',') if field.strip()]
                st.info(f'将忽略以下字段: {", ".join(ignore_fields)}')
            
            where_basic = text_input4.strip() if 'text_input4' in locals() else ''
            where_compare = text_input5.strip() if 'text_input5' in locals() else ''
            
            # 显示应用的WHERE条件
            if where_basic:
                st.info(f'基础表WHERE条件: {where_basic}')
            if where_compare:
                st.info(f'对比表WHERE条件: {where_compare}')
            
            sql, error = process_single_table(text_input1, text_input2, ignore_fields, where_basic, where_compare)
            
            if sql:
                st.write('生成的except语句为:')
                st.code(sql, language='sql')
            else:
                st.warning(error)
        else:
            st.warning('两个框都要输入')
    
    else:  # 批量对比模式
        if batch_input:
            # 处理需要忽略的字段
            ignore_fields = []
            if text_input3:
                ignore_fields = [field.strip() for field in text_input3.split(',') if field.strip()]
                st.info(f'将忽略以下字段: {", ".join(ignore_fields)}')
            
            lines = batch_input.strip().split('\n')
            all_sqls = []
            success_count = 0
            error_count = 0
            
            st.write(f'开始批量处理 {len(lines)} 对表...')
            
            for idx, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) < 2:
                    st.warning(f'第{idx}行格式错误，跳过: {line}')
                    error_count += 1
                    continue
                
                ddl_text = parts[0].strip()
                compare_table = parts[1].strip()
                where_basic = parts[2].strip() if len(parts) > 2 else ''
                where_compare = parts[3].strip() if len(parts) > 3 else ''
                
                with st.expander(f'处理第{idx}对: {compare_table}'):
                    if where_basic:
                        st.info(f'基础表WHERE条件: {where_basic}')
                    if where_compare:
                        st.info(f'对比表WHERE条件: {where_compare}')
                    
                    sql, error = process_single_table(ddl_text, compare_table, ignore_fields, where_basic, where_compare)
                    
                    if sql:
                        st.code(sql, language='sql')
                        all_sqls.append(f'-- 表对 {idx}: {compare_table}\n{sql}')
                        success_count += 1
                    else:
                        st.error(f'错误: {error}')
                        error_count += 1
            
            if all_sqls:
                st.success(f'批量处理完成！成功: {success_count}, 失败: {error_count}')
                st.write('### 所有生成的SQL语句:')
                combined_sql = '\n\n' + '\n\n'.join(all_sqls)
                st.code(combined_sql, language='sql')
                
                # 提供下载按钮
                st.download_button(
                    label='下载所有SQL语句',
                    data=combined_sql,
                    file_name='batch_except_sql.sql',
                    mime='text/plain'
                )
            else:
                st.error('没有成功生成任何SQL语句')
        else:
            st.warning('请输入批量表对信息')

else:
    if processing_mode == '单表对比':
        st.warning('请先输入ddl')
    else:
        st.warning('请输入批量表对信息')


