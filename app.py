#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 13:45:54 2025

@author: zhz
"""

# main_app.py
import streamlit as st

# 设置网页配置，这个标题会显示在浏览器的标签页上
st.set_page_config(
    page_title="国企改革量化指标分析",
    layout="wide"
)

# 使用 st.title 设置页面上的主标题
st.title("中央企业、地方国企改革深化提升行动重点量化指标")

# 在主页上添加一些引导性文字
st.write("---")
st.info("请在左侧的侧边栏中选择“中央企业”或“地方国企”页面进行查看。")