# pages/2_地方国企.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# 兼容新版Numpy的补丁
if not hasattr(np, 'bool8'):
    np.bool8 = np.bool_

st.set_page_config(layout="wide")

# --- 数据加载与处理函数 ---
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

# --- 主页面逻辑 ---
df_local = load_data(sheet_name='地方')
china_geojson = get_china_geojson()

if df_local.empty:
    st.stop()

headers = [
    "基本情况统计", "零、总体要求", "一、优化国有经济布局结构，加快建设现代化产业体系",
    "二、完善国有企业科技创新机制，加快实现高水平自立自强", "三、强化国有企业对重点领域保障，支撑国家战略安全",
    "四、以市场化方式推进整合重组，提升国有资本配置效率", "五、推动中国特色国有企业现代公司治理和市场化经营机制制度化长效化",
    "六、健全以管资本为主的国资监管体制", "七、营造更加市场化法治化国际化的公平竞争环境",
    "八、全面加强国有企业党的领导和党的建设", "九、组织保障"
]

for header_text in headers:
    st.header(header_text)
    
    if header_text == "一、优化国有经济布局结构，加快建设现代化产业体系":
        with st.container(border=True):
            chapter_name = "一、优化国有经济布局结构，加快建设现代化产业体系"
            df_chapter = df_local[df_local['所属章节'] == chapter_name].copy()

            if df_chapter.empty:
                st.warning(f"数据文件中未找到章节 '{chapter_name}' 的相关数据。")
                continue

            # --- 指标筛选 ---
            st.subheader("分析指标选择")
            indicator_options = sorted(df_chapter['指标名称'].unique())
            default_indicator = "截至本填报期末，本年度监管企业前瞻性战略性新兴产业营业收入占比（指标7/指标4）"
            try:
                default_index = indicator_options.index(default_indicator)
            except ValueError:
                default_index = 0
            selected_indicator = st.selectbox(
                "请选择或输入关键词搜索指标：",
                options=indicator_options, index=default_index, key=f"indicator_select_{header_text}"
            )
            
            # 获取动态单位
            unit_series = df_chapter[df_chapter['指标名称'] == selected_indicator]['单位'].dropna()
            unit = unit_series.iloc[0] if not unit_series.empty else ''
            axis_title = f"数值 ({unit})" if unit else "数值"
            
            # --- 季度筛选器 ---
            st.subheader("季度筛选器")
            year_options = sorted(df_chapter['年份'].unique(), reverse=True)
            quarter_options = sorted(df_chapter['季度'].unique())
            filter_col1, filter_col2 = st.columns([1, 4])
            with filter_col1:
                panel_year = st.selectbox("选择年份", options=year_options, key=f"panel_year_{header_text}")
            with filter_col2:
                panel_quarter = st.selectbox("选择季度", options=quarter_options, key=f"panel_quarter_{header_text}")
            
            st.write("---")

            # --- 数据筛选 ---
            panel_data = df_chapter[
                (df_chapter['指标名称'] == selected_indicator) &
                (df_chapter['年份'] == panel_year) &
                (df_chapter['季度'] == panel_quarter)
            ]

            # --- 仪表盘布局 ---
            left_col, right_col = st.columns([2, 1], gap="large")

            # --- 左侧地图 ---
            with left_col:
                st.subheader("各地区数据地图")
                
                if panel_data.empty or not china_geojson:
                    st.warning("当前筛选条件下无数据或无法加载地图，无法生成图表。")
                else:
                    df_for_map = panel_data.copy()
                    
                    has_xinjiang = '新疆维吾尔自治区' in df_for_map['省份'].values
                    has_bingtuan = '新疆生产建设兵团' in df_for_map['省份'].values

                    if has_xinjiang and has_bingtuan:
                        xinjiang_value = df_for_map.loc[df_for_map['省份'] == '新疆维吾尔自治区', '数值'].iloc[0]
                        bingtuan_value = df_for_map.loc[df_for_map['省份'] == '新疆生产建设兵团', '数值'].iloc[0]
                        total_value = xinjiang_value + bingtuan_value
                        df_for_map.loc[df_for_map['省份'] == '新疆维吾尔自治区', '数值'] = total_value
                    
                    df_for_map = df_for_map[df_for_map['省份'] != '新疆生产建设兵团']

                    fig = px.choropleth(
                        df_for_map,
                        geojson=china_geojson,
                        locations='省份',
                        featureidkey="properties.name",
                        color='数值',
                        color_continuous_scale="Viridis",
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
                    
                    # 格式化输出
                    top_10_data['排名'] = range(1, len(top_10_data) + 1)
                    top_10_data['数值'] = top_10_data['数值'].map('{:,.1f}'.format)
                    
                    # 选择并重排要显示的列
                    display_df = top_10_data[['排名', '省份', '数值']]
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True # 隐藏原始索引
                    )
                    
            st.info("""
                    **数据说明**:  
                    1. 不包括港澳台地区  
                    2. 由于标准地图文件中“新疆”为一个整体地理单元，我们在地图上展示的“新疆维吾尔自治区”颜色所代表的数值是 **自治区与兵团两者的总和**。
                    """)


    else:
        with st.container(border=True):
            st.write("此处未来用于放置相关图表和分析...")