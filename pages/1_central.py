
# pages/1_中央企业.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data(sheet_name):
    file_path = "1_data.xlsx"
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        df['数值'] = df['数值'].astype(str).str.replace('%', '', regex=False)
        df['数值'] = pd.to_numeric(df['数值'], errors='coerce')
        df.dropna(subset=['数值'], inplace=True)

        df['年份'] = df['年份'].astype(int)
        df['季度'] = df['季度'].astype(int)
        #df['指标序号'] = df['指标序号'].astype(int)
        return df
    except FileNotFoundError:
        st.error(f"错误：数据文件 '{file_path}' 未找到。请确保它和 pages 文件夹在同一级目录。")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"读取Excel文件时出错: {e}")
        return pd.DataFrame()

def get_filtered_data(df, indicator, start_year, start_quarter, end_year, end_quarter):
    df['时间点'] = df['年份'] + df['季度'] / 10.0
    start_point = start_year + start_quarter / 10.0
    end_point = end_year + end_quarter / 10.0
    filtered = df[
        (df['指标名称'] == indicator) &
        (df['时间点'] >= start_point) &
        (df['时间点'] <= end_point)
    ]
    return filtered.copy()

df_central = load_data(sheet_name='中央')

if df_central.empty:
    st.stop()

st.header("一、优化国有经济布局结构，加快建设现代化产业体系")
with st.container(border=True):
    st.write("此处未来用于放置相关图表和分析...")

st.header("二、完善国有企业科技创新机制，加快实现高水平自立自强")
with st.container(border=True):
    # --- 1. 按章节筛选数据 ---
    chapter_name = "三、完善国有企业科技创新机制加快实现高水平自立自强"
    df_chapter = df_central[df_central['所属章节'] == chapter_name].copy()  
    # 如果该章节无数据，则提示
    if df_chapter.empty:
        st.warning(f"数据文件中未找到章节 '{chapter_name}' 的相关数据。")
        st.stop()

    # --- 2. 创建包含序号的指标显示名称 ---
    df_chapter['指标显示名称'] = df_chapter['指标名称'] + ' --- ' + df_chapter['指标序号'].astype(str)
    st.subheader("分析指标选择")
    # --- 3. 实现关键词搜索和指标选择 ---
    indicator_display_options = sorted(df_chapter['指标显示名称'].unique())
    # 关键词搜索框
    search_term = st.text_input("指标关键词搜索：", placeholder="输入关键词筛选下方列表")
    # 根据搜索词筛选选项
    if search_term:
        filtered_options = [opt for opt in indicator_display_options if search_term.lower() in opt.lower()]
        # 在搜索模式下，默认选中第一个匹配项
        index_to_use = 0
    else:
        # 在非搜索模式下，使用完整的列表，并设置您指定的默认值
        filtered_options = indicator_display_options
        default_indicator = "截至本填报期末，本企业研发人员占比（%），指标68/指标4 --- 3(68/4)"
        try:
            index_to_use = filtered_options.index(default_indicator)
        except ValueError:
            # 如果默认指标在数据中不存在，安全地回退到第一个
            index_to_use = 0
    selected_display_name = st.selectbox(
        "请从筛选结果中选择您需要分析的指标：",
        options=filtered_options,
        index=index_to_use,
        label_visibility="collapsed"
    )
    if not selected_display_name:
        st.warning("根据您的搜索，未找到匹配的指标。请调整关键词或清空搜索框。")
        st.stop()
    original_indicator = selected_display_name.split(' --- ')[0]
    
    # --- 新增：获取当前指标的单位 ---
    # 筛选出当前指标的所有行，并获取第一个非空的“单位”值
    unit_series = df_chapter[df_chapter['指标名称'] == original_indicator]['单位'].dropna()
    unit = unit_series.iloc[0] if not unit_series.empty else ''
    axis_title = f"数值 ({unit})" if unit else "数值" # 如果单位为空，则不显示括号
    
    
    st.markdown(f"#### 当前分析指标：**{selected_display_name}**")
    st.write("---")

    left_col, right_col = st.columns(2, gap="large")
    year_options = sorted(df_chapter['年份'].unique(), reverse=True)
    quarter_options = sorted(df_chapter['季度'].unique())
    
    with left_col:
        st.subheader("面板数据：Top 10 企业排序")     
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            panel_year = st.selectbox("选择年份", options=year_options, key="panel_year")
        with filter_col2:
            panel_quarter = st.selectbox("选择季度", options=quarter_options, key="panel_quarter")
    
    # --- 修正：将 panel_data 和 top_10_companies 的定义移到列布局之外 ---
    panel_data = df_chapter[
        (df_chapter['指标名称'] == original_indicator) &
        (df_chapter['年份'] == panel_year) &
        (df_chapter['季度'] == panel_quarter)
    ].nlargest(10, '数值').sort_values('数值', ascending=True)
    
    # --- 新增：为Top 10企业创建颜色映射 ---
    top_10_companies = panel_data['企业名称'].tolist()
    color_sequence = px.colors.qualitative.Plotly
    color_map = {company: color_sequence[i % len(color_sequence)] for i, company in enumerate(top_10_companies)}


    with left_col:

        fig_bar = px.bar(
            panel_data,
            x='数值',
            y='企业名称',
            orientation='h',
            title=f'{panel_year}年Q{panel_quarter} - Top 10',
            text='数值',
            color='企业名称',              # <-- 新增：指定按企业名称分配颜色
            color_discrete_map=color_map   # <-- 新增：应用颜色映射
        )
        # --- 修改：使用动态坐标轴标题 ---
        fig_bar.update_layout(
            yaxis_title="企业名称", 
            xaxis_title=axis_title,
            showlegend=False # 条形图通常不需要图例
        )
        fig_bar.update_yaxes(categoryorder='total ascending')
        fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside') # 单位已在标题中，此处只显示数值
        fig_bar.update_traces(hovertemplate='<b>%{y}</b><br>数值: %{x:.1f}<extra></extra>')
        st.plotly_chart(fig_bar, use_container_width=True)

    with right_col:
        st.subheader("时间序列数据：Top 10 企业趋势")
        
        range_col1, range_col2, range_col3, range_col4 = st.columns(4)
        
        default_start_year = 2024
        default_start_q = 4
        default_end_year = 2025
        default_end_q = 1

        start_year_idx = year_options.index(default_start_year) if default_start_year in year_options else 0
        start_q_idx = quarter_options.index(default_start_q) if default_start_q in quarter_options else 0
        end_year_idx = year_options.index(default_end_year) if default_end_year in year_options else 0
        end_q_idx = quarter_options.index(default_end_q) if default_end_q in quarter_options else 0

        with range_col1:
            start_year = st.selectbox("起始年份", options=year_options, index=start_year_idx, key="start_year")
        with range_col2:
            start_quarter = st.selectbox("起始季度", options=quarter_options, index=start_q_idx, key="start_quarter")
        with range_col3:
            end_year = st.selectbox("终止年份", options=year_options, index=end_year_idx, key="end_year")
        with range_col4:
            end_quarter = st.selectbox("终止季度", options=quarter_options, index=end_q_idx, key="end_quarter")

        time_series_filtered_df = get_filtered_data(df_chapter, original_indicator, start_year, start_quarter, end_year, end_quarter)
        
        time_series_data = time_series_filtered_df[time_series_filtered_df['企业名称'].isin(top_10_companies)].copy()
        
        # --- 4. 新增：在绘图前按时间排序数据 ---
        time_series_data.sort_values(by=['年份', '季度'], inplace=True)
        
        time_series_data['时间'] = time_series_data['年份'].astype(str) + '-Q' + time_series_data['季度'].astype(str)
        
        fig_line = px.line(
            time_series_data,
            x='时间',
            y='数值',
            color='企业名称',
            markers=True,
            title=f'Top 10 企业趋势 ({start_year}Q{start_quarter} - {end_year}Q{end_quarter})',
            color_discrete_map=color_map # <-- 新增：应用颜色映射
        )
        # --- 修改：使用动态坐标轴标题 ---
        fig_line.update_layout(xaxis_title="时间", yaxis_title=axis_title, legend_title="企业名称")
        fig_line.update_traces(hovertemplate='时间: %{x}<br>数值: %{y:.1f}<extra></extra>')
        st.plotly_chart(fig_line, use_container_width=True)

st.header("九、组织保障")
with st.container(border=True):
    st.write("此处未来用于放置相关图表和分析...")
