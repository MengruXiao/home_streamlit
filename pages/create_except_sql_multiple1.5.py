import streamlit as st
import pandas as pd
from pathlib import Path

COLS_NUM = 4
MAX_TEMP_FILES = 10
TEST_EXCEL = Path("static/示例ddl.sql")

def download_button(button_name:str, file_path: Path, file_type: str) -> None:
    try:
        with open(file_path, "rb") as file:
            file_bytes = file.read()
        if file_type in ['xlsx','zip','json','txt','sql']:
            if file_type == 'xlsx':
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file_type == 'zip':
                mime_type = "application/zip"
            elif file_type == 'json':
                mime_type = "application/json"
            elif file_type in ['txt', 'sql']:
                mime_type = "text/plain"
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
download_button("模板下载", TEST_EXCEL, 'sql')

# 添加批量处理模式选择
processing_mode = st.radio('选择处理模式', ['单表对比', '批量对比（文本输入）', '批量对比（文件上传）'], horizontal=True)

if processing_mode == '单表对比':
    text_input1 = st.text_area('输入您的基础表DDL', '')
    text_input2 = st.text_area('输入对比表名(默认两表的ddl一样)', '')
    text_input3 = st.text_area('输入需要忽略的字段(多个字段用逗号分隔，例如: field1,field2,field3)', '')
    text_input4 = st.text_area('输入基础表的WHERE条件(可选，不需要写WHERE关键字)', '', 
                               help='例如: version_no = \'2025Q2V2\' and date > \'2024-01-01\'')
    text_input5 = st.text_area('输入对比表的WHERE条件(可选，不需要写WHERE关键字)', '',
                               help='例如: version_no = \'2025Q2V2\' and date > \'2024-01-01\'')
elif processing_mode == '批量对比（文本输入）':
    st.info('📝 批量模式说明：支持两种输入格式')
    st.markdown('''
    **格式1（推荐）：** 使用分号 `;` 分隔多个DDL，系统自动生成对比表名
    - 直接粘贴多个完整的DDL语句，用 `;` 分隔
    - 例如：`CREATE TABLE schema.table1 (...);CREATE TABLE schema.table2 (...);`
    
    **格式2：** 每行一对，使用管道符 `|` 分隔
    - 格式：`DDL|对比表名|基础表WHERE|对比表WHERE`
    - 例如：`CREATE TABLE schema.table1...|schema.table1_compare`
    ''')
    
    batch_input = st.text_area('批量输入DDL（支持分号或管道符分隔）', 
                               height=300,
                               help='推荐：直接粘贴多个DDL，用分号分隔。也支持每行一对的管道符格式。')
    
    col1, col2 = st.columns(2)
    with col1:
        compare_suffix_batch = st.text_input(
            '对比表后缀（用于分号分隔模式）', 
            '_compare',
            help='使用分号分隔DDL时，自动为每个表添加此后缀生成对比表名'
        )
    with col2:
        text_input3 = st.text_area('输入需要忽略的字段(多个字段用逗号分隔，对所有表生效)', '', height=100)
    
    # WHERE条件设置
    st.subheader('WHERE条件设置（可选，用于分号分隔模式）')
    col3, col4 = st.columns(2)
    with col3:
        batch_where_basic = st.text_area(
            '全局基础表WHERE条件', 
            '',
            help='将应用到所有基础表'
        )
    with col4:
        batch_where_compare = st.text_area(
            '全局对比表WHERE条件', 
            '',
            help='将应用到所有对比表'
        )
else:  # 批量对比（文件上传）
    st.info('📁 批量上传DDL文件模式：支持两种文件格式')
    st.markdown('''
    - **单个DDL文件**：每个文件包含一个CREATE TABLE语句
    - **批量DDL文件**：单个文件包含多个DDL，用分号 `;` 分隔
    ''')
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_files = st.file_uploader(
            "上传基础表DDL文件（可多选）", 
            type=['sql', 'txt'],
            accept_multiple_files=True,
            help='支持上传多个DDL文件。文件内可以包含单个DDL或用分号分隔的多个DDL'
        )
    with col2:
        compare_suffix = st.text_input(
            '对比表后缀或替换规则', 
            '_compare',
            help='例如：输入 "_compare" 则 table1 对比 table1_compare'
        )
    
    text_input3 = st.text_area('输入需要忽略的字段(多个字段用逗号分隔，对所有表生效)', '')
    
    # WHERE条件设置
    st.subheader('WHERE条件设置（可选）')
    col3, col4 = st.columns(2)
    with col3:
        global_where_basic = st.text_area(
            '全局基础表WHERE条件', 
            '',
            help='将应用到所有基础表，例如: version_no = \'2025Q2V2\''
        )
    with col4:
        global_where_compare = st.text_area(
            '全局对比表WHERE条件', 
            '',
            help='将应用到所有对比表，例如: version_no = \'2025Q2V2\''
        )

def process_single_table(ddl_text, compare_table, ignore_fields, where_basic='', where_compare=''):
    """处理单个表对"""
    lines = ddl_text.splitlines()
    
    # 清理空行
    lines = [line for line in lines if line.strip()]
    
    if not lines:
        return None, 'DDL内容为空'
    
    columns = []
    table_name_basic = None
    
    # 解析表名
    first_line = lines[0].strip()
    if 'CREATE TABLE' in first_line.upper():
        # 提取表名 - 处理可能的多种格式
        parts = first_line.split()
        for i, part in enumerate(parts):
            if part.upper() == 'TABLE' and i + 1 < len(parts):
                table_name_basic = parts[i + 1].rstrip('(').strip()
                break
    
    if not table_name_basic:
        return None, '无法从DDL中提取表名'
    
    # 解析字段
    for line in lines[1:]:
        line_stripped = line.strip()
        
        # 跳过结束括号和其他非字段定义行
        if line_stripped.startswith(')') or line_stripped.startswith('DISTSTYLE') or \
           line_stripped.startswith('SORTKEY') or not line_stripped:
            continue
            
        # 处理逗号
        if ", " in line_stripped:
            line_stripped = line_stripped.replace(', ', ',')
        
        # 移除末尾的逗号
        if line_stripped.endswith(','):
            line_stripped = line_stripped[:-1]
        
        parts = line_stripped.split()
        if len(parts) >= 2:
            column_name = parts[0].strip()
            
            # 跳过约束关键字
            if column_name.upper() in ['PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK', 'CONSTRAINT']:
                continue
            
            # 处理数据类型
            if parts[1] == 'character':
                type_name = parts[2].replace('varying', 'varchar')
            elif parts[1] == 'timestamp':
                type_name = 'datetime'
            elif parts[1] == 'integer':
                type_name = 'int'
            else:
                type_name = parts[1]
            
            columns.append((column_name, type_name))
    
    if not columns:
        return None, '没有找到有效的字段定义'
    
    df = pd.DataFrame(columns, columns=['column_name', 'type'])
    
    # 过滤掉需要忽略的字段
    if ignore_fields:
        df = df[~df['column_name'].isin(ignore_fields)]
    
    if len(df) == 0:
        return None, '过滤后没有剩余字段，请检查忽略字段列表'
    
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
    
    elif processing_mode == '批量对比（文本输入）':  # 批量文本输入模式
        if batch_input:
            # 处理需要忽略的字段
            ignore_fields = []
            if text_input3:
                ignore_fields = [field.strip() for field in text_input3.split(',') if field.strip()]
                st.info(f'将忽略以下字段: {", ".join(ignore_fields)}')
            
            # 判断输入格式：是否包含分号（DDL分隔符）
            if ';' in batch_input and '|' not in batch_input:
                # 格式1：使用分号分隔多个DDL
                st.info('🔍 检测到分号分隔的DDL格式')
                
                # 获取全局WHERE条件
                where_basic_global = batch_where_basic.strip() if 'batch_where_basic' in locals() else ''
                where_compare_global = batch_where_compare.strip() if 'batch_where_compare' in locals() else ''
                
                if where_basic_global:
                    st.info(f'全局基础表WHERE条件: {where_basic_global}')
                if where_compare_global:
                    st.info(f'全局对比表WHERE条件: {where_compare_global}')
                
                # 按分号分割DDL，并清理空白
                ddl_list = []
                for ddl in batch_input.split(';'):
                    ddl = ddl.strip()
                    if ddl and 'CREATE TABLE' in ddl.upper():
                        ddl_list.append(ddl)
                
                all_sqls = []
                success_count = 0
                error_count = 0
                
                st.write(f'开始批量处理 {len(ddl_list)} 个DDL...')
                
                for idx, ddl_text in enumerate(ddl_list, 1):
                    # 从DDL中提取表名
                    base_table_name = None
                    for line in ddl_text.splitlines():
                        if 'CREATE TABLE' in line.upper():
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part.upper() == 'TABLE' and i + 1 < len(parts):
                                    base_table_name = parts[i + 1].rstrip('(').strip()
                                    break
                            break
                    
                    if not base_table_name:
                        st.warning(f'第{idx}个DDL: 无法提取表名，跳过')
                        error_count += 1
                        continue
                    
                    # 生成对比表名
                    suffix = compare_suffix_batch if 'compare_suffix_batch' in locals() and compare_suffix_batch else '_compare'
                    if '.' in base_table_name:
                        schema, table = base_table_name.rsplit('.', 1)
                        compare_table = f'{schema}.{table}{suffix}'
                    else:
                        compare_table = f'{base_table_name}{suffix}'
                    
                    with st.expander(f'📋 处理第{idx}个DDL: {base_table_name}'):
                        st.write(f'基础表: `{base_table_name}`')
                        st.write(f'对比表: `{compare_table}`')
                        
                        sql, error = process_single_table(
                            ddl_text, 
                            compare_table, 
                            ignore_fields, 
                            where_basic_global, 
                            where_compare_global
                        )
                        
                        if sql:
                            st.code(sql, language='sql')
                            all_sqls.append(f'-- DDL {idx}: {base_table_name} vs {compare_table}\n{sql}')
                            success_count += 1
                        else:
                            st.error(f'错误: {error}')
                            error_count += 1
                
                if all_sqls:
                    st.success(f'✅ 批量处理完成！成功: {success_count}, 失败: {error_count}')
                    st.write('### 所有生成的SQL语句:')
                    combined_sql = '\n\n' + '\n\n'.join(all_sqls)
                    st.code(combined_sql, language='sql')
                    
                    # 提供下载按钮
                    st.download_button(
                        label='📥 下载所有SQL语句',
                        data=combined_sql,
                        file_name='batch_except_sql_semicolon.sql',
                        mime='text/plain'                    )
                else:
                    st.error('❌ 没有成功生成任何SQL语句')
            
            else:
                # 格式2：使用管道符分隔（原有格式）
                st.info('🔍 检测到管道符分隔格式')
                
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
                        st.warning(f'第{idx}行格式错误，跳过: {line[:50]}...')
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
                    st.success(f'✅ 批量处理完成！成功: {success_count}, 失败: {error_count}')
                    st.write('### 所有生成的SQL语句:')
                    combined_sql = '\n\n' + '\n\n'.join(all_sqls)
                    st.code(combined_sql, language='sql')
                    
                    # 提供下载按钮
                    st.download_button(
                        label='📥 下载所有SQL语句',
                        data=combined_sql,
                        file_name='batch_except_sql.sql',
                        mime='text/plain'
                    )
                else:
                    st.error('❌ 没有成功生成任何SQL语句')
        else:
            st.warning('请输入批量表对信息')
    
    else:  # 批量文件上传模式
        if uploaded_files:
            # 处理需要忽略的字段
            ignore_fields = []
            if text_input3:
                ignore_fields = [field.strip() for field in text_input3.split(',') if field.strip()]
                st.info(f'将忽略以下字段: {", ".join(ignore_fields)}')
            
            # 显示全局WHERE条件
            where_basic_global = global_where_basic.strip() if 'global_where_basic' in locals() else ''
            where_compare_global = global_where_compare.strip() if 'global_where_compare' in locals() else ''
            
            if where_basic_global:
                st.info(f'全局基础表WHERE条件: {where_basic_global}')
            if where_compare_global:
                st.info(f'全局对比表WHERE条件: {where_compare_global}')
            
            all_sqls = []
            success_count = 0
            error_count = 0
            total_ddl_count = 0
            
            st.write(f'开始处理 {len(uploaded_files)} 个文件...')
            
            for file_idx, uploaded_file in enumerate(uploaded_files, 1):
                # 读取文件内容
                try:
                    ddl_content = uploaded_file.read().decode('utf-8')
                except Exception as e:
                    st.error(f'文件 {uploaded_file.name} 读取失败: {str(e)}')
                    error_count += 1
                    continue
                
                # 检查文件中是否包含多个DDL（用分号分隔）
                if ';' in ddl_content:
                    # 文件包含多个DDL，按分号分割
                    ddl_list = []
                    for ddl in ddl_content.split(';'):
                        ddl = ddl.strip()
                        if ddl and 'CREATE TABLE' in ddl.upper():
                            ddl_list.append(ddl)
                    
                    if len(ddl_list) > 1:
                        st.info(f'📋 文件 `{uploaded_file.name}` 包含 {len(ddl_list)} 个DDL语句')
                    
                    # 处理文件中的每个DDL
                    for ddl_idx, ddl_text in enumerate(ddl_list, 1):
                        total_ddl_count += 1
                        
                        # 从DDL中提取表名
                        base_table_name = None
                        for line in ddl_text.splitlines():
                            if 'CREATE TABLE' in line.upper():
                                parts = line.split()
                                for i, part in enumerate(parts):
                                    if part.upper() == 'TABLE' and i + 1 < len(parts):
                                        base_table_name = parts[i + 1].rstrip('(').strip()
                                        break
                                break
                        
                        if not base_table_name:
                            st.warning(f'文件 {uploaded_file.name} 第{ddl_idx}个DDL: 无法提取表名，跳过')
                            error_count += 1
                            continue
                        
                        # 生成对比表名
                        if compare_suffix:
                            if '.' in base_table_name:
                                schema, table = base_table_name.rsplit('.', 1)
                                compare_table = f'{schema}.{table}{compare_suffix}'
                            else:
                                compare_table = f'{base_table_name}{compare_suffix}'
                        else:
                            compare_table = base_table_name + '_compare'
                        
                        # 为多DDL文件创建独立的expander
                        expander_title = f'📄 文件{file_idx}: {uploaded_file.name} - DDL{ddl_idx}: {base_table_name}'
                        with st.expander(expander_title):
                            st.write(f'基础表: `{base_table_name}`')
                            st.write(f'对比表: `{compare_table}`')
                            
                            sql, error = process_single_table(
                                ddl_text, 
                                compare_table, 
                                ignore_fields, 
                                where_basic_global, 
                                where_compare_global
                            )
                            
                            if sql:
                                st.code(sql, language='sql')
                                all_sqls.append(f'-- 文件: {uploaded_file.name} (DDL #{ddl_idx})\n-- 基础表: {base_table_name}\n-- 对比表: {compare_table}\n{sql}')
                                success_count += 1
                            else:
                                st.error(f'错误: {error}')
                                error_count += 1
                
                else:
                    # 文件只包含单个DDL
                    total_ddl_count += 1
                    
                    # 从DDL中提取表名
                    ddl_lines = ddl_content.strip().splitlines()
                    base_table_name = None
                    for line in ddl_lines:
                        if 'CREATE TABLE' in line.upper():
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part.upper() == 'TABLE' and i + 1 < len(parts):
                                    base_table_name = parts[i + 1].rstrip('(').strip()
                                    break
                            break
                    
                    if not base_table_name:
                        st.warning(f'文件 {uploaded_file.name}: 无法提取表名，跳过')
                        error_count += 1
                        continue
                    
                    # 生成对比表名
                    if compare_suffix:
                        if '.' in base_table_name:
                            schema, table = base_table_name.rsplit('.', 1)
                            compare_table = f'{schema}.{table}{compare_suffix}'
                        else:
                            compare_table = f'{base_table_name}{compare_suffix}'
                    else:
                        compare_table = base_table_name + '_compare'
                    
                    with st.expander(f'📄 文件 {file_idx}/{len(uploaded_files)}: {uploaded_file.name}'):
                        st.write(f'基础表: `{base_table_name}`')
                        st.write(f'对比表: `{compare_table}`')
                        
                        sql, error = process_single_table(
                            ddl_content, 
                            compare_table, 
                            ignore_fields, 
                            where_basic_global, 
                            where_compare_global
                        )
                        
                        if sql:
                            st.code(sql, language='sql')
                            all_sqls.append(f'-- 文件: {uploaded_file.name}\n-- 基础表: {base_table_name}\n-- 对比表: {compare_table}\n{sql}')
                            success_count += 1
                        else:
                            st.error(f'错误: {error}')
                            error_count += 1
            
            if all_sqls:
                st.success(f'✅ 批量处理完成！总计处理 {total_ddl_count} 个DDL，成功: {success_count}, 失败: {error_count}')
                st.write('### 所有生成的SQL语句:')
                combined_sql = '\n\n' + '\n\n'.join(all_sqls)
                st.code(combined_sql, language='sql')
                
                # 提供下载按钮
                st.download_button(
                    label='📥 下载所有SQL语句',
                    data=combined_sql,
                    file_name='batch_except_sql_from_files.sql',
                    mime='text/plain'
                )
            else:
                st.error('❌ 没有成功生成任何SQL语句')
        else:
            st.warning('⚠️ 请上传至少一个DDL文件')

else:
    if processing_mode == '单表对比':
        st.warning('请先输入ddl')
    elif processing_mode == '批量对比（文本输入）':
        st.warning('请输入批量表对信息')
    else:
        st.warning('请上传DDL文件')


