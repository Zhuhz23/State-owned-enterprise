#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 22:55:10 2025

@author: zhz
"""

# pages/2_地方国企.py (已重构为函数式结构)
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# 兼容新版Numpy的补丁
if not hasattr(np, 'bool8'):
    np.bool8 = np.bool_

st.set_page_config(layout="wide")

# --- 数据加载函数 ---
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
        return df
    except FileNotFoundError:
        st.error(f"错误：数据文件 '{file_path}' 未找到。")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"读取Excel文件时出错: {e}")
        return pd.DataFrame()

@st.cache_data
def get_china_geojson():
    """从网络加载GeoJSON文件"""
    url = "https://raw.githubusercontent.com/longwosion/geojson-map-china/master/china.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"无法加载GeoJSON文件: {e}")
        return None

# --- 可复用的仪表盘创建函数 ---
def create_dashboard(panel_data, unit, geojson_data, panel_year, panel_quarter, selected_indicator, selected_chapter):
    """
    为给定的章节数据创建一个完整的仪表盘。
    
    参数:
    df_chapter (pd.DataFrame): 已经按章节筛选过的数据。
    chapter_title (str): 当前章节的标题，用于生成唯一的组件key。
    geojson_data: 用于绘制地图的GeoJSON数据。
    """

    # --- 仪表盘布局 ---
    axis_title = f"数值 ({unit})" if unit else "数值"
    left_col, right_col = st.columns([2, 1], gap="large")

    # --- 左侧地图 ---
    with left_col:
        st.subheader(f"数据地图：{selected_chapter}")
        
        if panel_data.empty or not geojson_data:
            st.warning("当前筛选条件下无数据或无法加载地图，无法生成图表。")
        else:
            # ... [地图数据准备和绘图逻辑与之前相同] ...
            # 此处省略地图绘图代码，以保持简洁
            df_for_map = panel_data.copy()
            if unit != '%':
                has_xinjiang = '新疆维吾尔自治区' in df_for_map['省份'].values
                has_bingtuan = '新疆生产建设兵团' in df_for_map['省份'].values
                if has_xinjiang and has_bingtuan:
                    xinjiang_value = df_for_map.loc[df_for_map['省份'] == '新疆维吾尔自治区', '数值'].iloc[0]
                    bingtuan_value = df_for_map.loc[df_for_map['省份'] == '新疆生产建设兵团', '数值'].iloc[0]
                    df_for_map.loc[df_for_map['省份'] == '新疆维吾尔自治区', '数值'] = xinjiang_value + bingtuan_value
            df_for_map = df_for_map[df_for_map['省份'] != '新疆生产建设兵团']
            
            fig = px.choropleth(
                df_for_map,
                geojson=geojson_data,
                locations='省份',
                featureidkey="properties.name",
                color='数值',
                color_continuous_scale="spectral",
                #color_continuous_scale="rdylbu",
                title=f"{panel_year}年Q{panel_quarter} - {selected_indicator}"
            )
            fig.update_coloraxes(colorbar_title=axis_title)
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0, "t":40, "l":0, "b":0})
            fig.update_traces(hovertemplate='<b>%{location}</b><br>数值: %{z:.1f}<extra></extra>')
            st.plotly_chart(fig, use_container_width=True)

    # --- 右侧Top 10排名 ---
    with right_col:
        st.subheader("省份排名")
        top_num = 31+1#1是兵团
        
        if panel_data.empty:
            st.warning("无数据可供排名。")
        else:
            top_10_data = panel_data.nlargest(top_num, '数值').copy()
            top_10_data['排名'] = range(1, len(top_10_data) + 1)
            top_10_data['数值'] = top_10_data['数值'].map('{:,.1f}'.format)
            display_df = top_10_data[['排名', '省份', '数值']]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        
    info_message = "**数据说明**:\n\n1. 不包括港澳台地区"
    if unit != '%':
        info_message += "\n2. 由于标准地图文件中“新疆”为一个整体地理单元，我们在地图上展示的“新疆维吾尔自治区”颜色所代表的数值是 **自治区与兵团两者的总和**。"
    st.info(info_message)







# --- 主页面逻辑 ---
df_local = load_data(sheet_name='地方')
china_geojson = get_china_geojson()

if df_local.empty:
    st.stop()
    
# --- 新增：默认指标字典 ---
DEFAULT_INDICATORS_LOCAL = {
    "基本情况统计": "截至本填报期末，监管企业营业收入（亿元）",
    "零、总体要求": "截至本填报期末，本年度省级国资委及监管企业组织开展学习宣贯国有企业改革深化提升行动的专题会议及集中培训次数",
    "一、优化国有经济布局结构，加快建设现代化产业体系": "截至本填报期末，本年度监管企业前瞻性战略性新兴产业营业收入占比（指标7/指标4）",
    "二、完善国有企业科技创新机制，加快实现高水平自立自强": "截至本填报期末，本年度监管企业（全口径）研发投入强度（指标26/指标4）",
    "三、强化国有企业对重点领域保障，支撑国家战略安全": "截至本填报期末，省级国资委针对国务院领导同志提出的十一大问题，开展专项清理整治的次数",
    "四、以市场化方式推进整合重组，提升国有资本配置效率": "2023年以来，监管企业开展战略性重组的次（组）数",
    "五、推动中国特色国有企业现代公司治理和市场化经营机制制度化长效化": "今年以来，一级企业通过竞争上岗方式新聘任的管理人员总人数占比（指标87/指标86）",
    "六、健全以管资本为主的国资监管体制": "截至本填报期末，经营性国有资产集中统一监管比例",
    "七、营造更加市场化法治化国际化的公平竞争环境": "截至本填报期末，各级子企业中，混合所有制企业户数（穿透式口径）占比（指标129/指标2）",
    "八、全面加强国有企业党的领导和党的建设": "截至本填报期末，一级企业中已开展党建工作责任制考核的户数占比(指标135/指标1)",
    "九、组织保障": "截至本填报期末，本地区国有企业改革深化提升行动整体任务完成百分比（自我评估值）"
}

headers = [
    "基本情况统计", "零、总体要求", "一、优化国有经济布局结构，加快建设现代化产业体系",
    "二、完善国有企业科技创新机制，加快实现高水平自立自强", "三、强化国有企业对重点领域保障，支撑国家战略安全",
    "四、以市场化方式推进整合重组，提升国有资本配置效率", "五、推动中国特色国有企业现代公司治理和市场化经营机制制度化长效化",
    "六、健全以管资本为主的国资监管体制", "七、营造更加市场化法治化国际化的公平竞争环境",
    "八、全面加强国有企业党的领导和党的建设", "九、组织保障"
]

# --- 新增：页面顶部的章节筛选器 ---
st.header("地方国有企业改革深化提升行动重点量化指标仪表盘")
with st.container(border=True):
    # --- 第一行筛选器：章节和指标 ---
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        
        chapter_options = headers
        default_chapter = "基本情况统计"
        default_idx_chapter = chapter_options.index(default_chapter) if default_chapter in chapter_options else 0
        selected_chapter = st.selectbox("章节选择", options=chapter_options, index=default_idx_chapter)

    # 根据选择的章节，准备后续筛选器的选项
    df_chapter = df_local[df_local['所属章节'] == selected_chapter].copy()

    with col2:
        if df_chapter.empty:
            st.selectbox("指标选择", options=["当前章节无可用指标"], disabled=True)
        else:
            # 1. 创建 "指标序号 --- 指标名称" 格式的显示名称
            df_chapter['指标显示名称'] = df_chapter['指标序号'].astype(str) + ' --- ' + df_chapter['指标名称']
            indicator_options = sorted(df_chapter['指标显示名称'].unique())
            
            # 2. 根据新的格式来查找默认值
            default_indicator_name = DEFAULT_INDICATORS_LOCAL.get(selected_chapter)
            default_index = 0
            if default_indicator_name:
                default_row = df_chapter[df_chapter['指标名称'] == default_indicator_name]
                if not default_row.empty:
                    default_indicator_number = default_row['指标序号'].iloc[0]
                    default_display_name = f"{default_indicator_number} --- {default_indicator_name}"
                    if default_display_name in indicator_options:
                        default_index = indicator_options.index(default_display_name)
            
            selected_display_name = st.selectbox(
                "指标选择", 
                options=indicator_options, # 3. 使用新的选项列表
                index=default_index
            )
            # 4. 从新的格式中解析出原始指标名称
            if selected_display_name:
                selected_indicator = selected_display_name.split(' --- ')[1]
            else:
                selected_indicator = None # 如果列表为空，则无选择

    # --- 第二行筛选器：年份和季度 ---
    with col3:
        if df_chapter.empty:
            st.selectbox("年份", options=["-"], disabled=True)
        else:
            year_options = sorted(df_chapter['年份'].unique(), reverse=True)
            panel_year = st.selectbox("年份", options=year_options)
    with col4:
        if df_chapter.empty:
            st.selectbox("季度", options=["-"], disabled=True)
        else:
            quarter_options = sorted(df_chapter['季度'].unique())
            panel_quarter = st.selectbox("季度", options=quarter_options)

#st.write("---")


# --- 2. 在主逻辑中准备好所有需要传递的参数 ---
#st.header(f"仪表盘分析：{selected_chapter}")

if df_chapter.empty:
    with st.container(border=True):
        st.warning("当前所选章节无可用数据。")
else:
    # 筛选用于仪表盘的最终数据
    panel_data = df_chapter[
        (df_chapter['指标名称'] == selected_indicator) &
        (df_chapter['年份'] == panel_year) &
        (df_chapter['季度'] == panel_quarter)
    ]
    # 获取单位
    unit_series = df_chapter[df_chapter['指标名称'] == selected_indicator]['单位'].dropna()
    unit = unit_series.iloc[0] if not unit_series.empty else ''

    # --- 3. 严格按照指定的参数顺序进行函数调用 ---
    create_dashboard(
        panel_data=panel_data, 
        unit=unit, 
        geojson_data=china_geojson, 
        panel_year=panel_year, 
        panel_quarter=panel_quarter, 
        selected_indicator=selected_indicator,
        selected_chapter=selected_chapter,
        
    )
