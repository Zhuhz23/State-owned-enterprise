
# pages/1_中央企业.py
import streamlit as st
import pandas as pd
import plotly.express as px

 

st.set_page_config(layout="wide")
    

def check_password():
    """如果用户已登录，返回 True，否则显示密码输入并返回 False"""
    
    # 如果 session state 中 "password_correct" 不存在或为 False，则显示密码输入
    if not st.session_state.get("password_correct", False):
        # 在一个表单中显示密码输入，这样可以防止每次输入字符时页面都刷新
        with st.form("Credentials"):
            st.text_input("请输入密码", type="password", key="password")
            submitted = st.form_submit_button("确认")
            
            # 如果用户点击了确认按钮
            if submitted:
                # 检查密码是否与 st.secrets 中的密码匹配
                if st.session_state["password"] == st.secrets["password"]:
                    # 如果匹配，将 password_correct 设为 True
                    st.session_state["password_correct"] = True
                    # 删除 session state 中的密码，更安全
                    del st.session_state["password"]
                    # 强制重新运行脚本，以显示主应用内容
                    st.rerun()
                else:
                    # 如果不匹配，显示错误信息
                    st.error("😕 密码不正确，请重试")
        # 因为还没登录，所以返回 False
        return False
    else:
        # 如果已经登录，返回 True
        return True


if check_password():
    
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
    
    st.header("中央企业指标分析仪表盘")
    
    
    
    # --- 1. 全局指标筛选器 ---
    with st.container(border=True):
        st.subheader("分析指标选择")
        
        # 在整个数据集上创建显示名称
        df_central['指标显示名称'] = df_central['指标名称'] + ' --- ' + df_central['指标序号'].astype(str)
        indicator_display_options = sorted(df_central['指标显示名称'].unique())
        
        search_term = st.text_input("指标关键词搜索：", placeholder="先输入关键词搜索，再筛选下方列表")
        
        if search_term:
            filtered_options = [opt for opt in indicator_display_options if search_term.lower() in opt.lower()]
            index_to_use = 0
        else:
            filtered_options = indicator_display_options
            default_indicator = "截至本填报期末，本企业研发人员占比（%），指标68/指标4 --- 3(68/4)"
            try:
                index_to_use = filtered_options.index(default_indicator)
            except ValueError:
                index_to_use = 0
                
        selected_display_name = st.selectbox(
            "请从筛选结果中选择您需要分析的指标：",
            options=filtered_options,
            index=index_to_use,
            label_visibility="collapsed"
        )
    
    if not selected_display_name:
        st.warning("请选择一个指标以开始分析。")
        st.stop()
        
              
    # --- 2. 根据所选指标，准备数据和后续筛选器 ---
    original_indicator = selected_display_name.split(' --- ')[0]
    df_indicator_data = df_central[df_central['指标名称'] == original_indicator].copy()
    
    selected_chapter = df_indicator_data['所属章节'].iloc[0] if not df_indicator_data.empty else "未知章节"
    unit_series = df_indicator_data['单位'].dropna()
    unit = unit_series.iloc[0] if not unit_series.empty else ''
    axis_title = f"数值 ({unit})" if unit else "数值"
    
    
    # --- 3. 全局时间筛选器 ---
    with st.container(border=True):
        st.subheader("时间范围筛选")
        left_filter_col, right_filter_col = st.columns(2)
    
        # 准备时间选项
        year_options = sorted(df_indicator_data['年份'].unique(), reverse=True)
        quarter_options = sorted(df_indicator_data['季度'].unique())
        
        with left_filter_col:
            st.markdown("**面板数据时间点**")
            panel_year = st.selectbox("选择年份", options=year_options, key="panel_year")
            panel_quarter = st.selectbox("选择季度", options=quarter_options, key="panel_quarter")
    
        with right_filter_col:
            st.markdown("**时间序列范围**")
            range_col1, range_col2 = st.columns(2)
            with range_col1:
                start_year = st.selectbox("起始年份", options=year_options, index=len(year_options)-1, key="start_year")
                start_quarter = st.selectbox("起始季度", options=quarter_options, index=0, key="start_quarter")
            with range_col2:
                end_year = st.selectbox("终止年份", options=year_options, index=0, key="end_year")
                # --- 核心修正：index不再写死 ---
                end_quarter_index = len(quarter_options) - 1
                end_quarter = st.selectbox("终止季度", options=quarter_options, index=end_quarter_index, key="end_quarter")
    
     
    
    
    # --- 4. 仪表盘展示 ---
    with st.container(border=True):
        # 准备数据
        panel_data = df_indicator_data[
            (df_indicator_data['年份'] == panel_year) &
            (df_indicator_data['季度'] == panel_quarter)
        ].nlargest(10, '数值')
    
        top_10_companies = panel_data['企业名称'].tolist()
        color_sequence = px.colors.qualitative.Plotly
        color_map = {company: color_sequence[i % len(color_sequence)] for i, company in enumerate(top_10_companies)}
    
        time_series_filtered_df = get_filtered_data(df_indicator_data, original_indicator, start_year, start_quarter, end_year, end_quarter)
        time_series_data = time_series_filtered_df[time_series_filtered_df['企业名称'].isin(top_10_companies)].copy()
        if not time_series_data.empty:
            time_series_data.sort_values(by=['年份', '季度'], inplace=True)
            time_series_data['时间'] = time_series_data['年份'].astype(str) + '-Q' + time_series_data['季度'].astype(str)
    
        
        st.markdown(f"#### 所属章节：**{selected_chapter}**")
        st.markdown(f"#### 当前分析指标：**{selected_display_name}**")
    
        # 创建仪表盘
        left_col, right_col = st.columns(2, gap="large")
    
        with left_col:
            st.subheader("面板数据：Top 10 企业排序")
            if panel_data.empty:
                st.warning("当前筛选条件下无数据。")
            else:
                fig_bar = px.bar(
                    panel_data, x='数值', y='企业名称', orientation='h',
                    title=f'{panel_year}年Q{panel_quarter} - Top 10', text='数值',
                    color='企业名称', color_discrete_map=color_map
                )
                fig_bar.update_layout(yaxis_title="企业名称", xaxis_title=axis_title, showlegend=False)
                fig_bar.update_yaxes(categoryorder='total ascending')
                fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_bar.update_traces(hovertemplate='<b>%{y}</b><br>数值: %{x:.1f}<extra></extra>')
                st.plotly_chart(fig_bar, use_container_width=True)
    
        with right_col:
            st.subheader("时间序列数据：Top 10 企业趋势")
            if time_series_data.empty:
                st.warning("在选定时间范围内，Top 10 企业无数据。")
            else:
                fig_line = px.line(
                    time_series_data, x='时间', y='数值', color='企业名称', markers=True,
                    title=f'Top 10 企业趋势 ({start_year}Q{start_quarter} - {end_year}Q{end_quarter})',
                    color_discrete_map=color_map
                )
                fig_line.update_layout(xaxis_title="时间", yaxis_title=axis_title, legend_title="企业名称")
                fig_line.update_traces(hovertemplate='时间: %{x}<br>数值: %{y:.1f}<extra></extra>')
                st.plotly_chart(fig_line, use_container_width=True)
