#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 13:45:54 2025

@author: zhz
"""

# main_app.py
import streamlit as st

st.set_page_config(
    page_title="国企改革量化指标分析",
    layout="wide"
)

def protect_page():
    """
    显示一个密码输入表单。
    如果密码正确，函数返回 True，页面内容将显示。
    如果密码错误或未输入，函数返回 False，页面内容将被隐藏。
    """
    
    # 使用 st.form 来创建一个表单
    with st.form("password_form"):
        # 创建一个文本输入框，类型为密码
        password_input = st.text_input(
            "此页面受密码保护，请输入密码访问：", 
            type="password"
        )
        
        # 创建一个提交按钮
        submit_button = st.form_submit_button("确认")

        # 当用户点击“确认”按钮后
        if submit_button:
            # 检查输入的密码是否和预设的密码一致
            # st.secrets.get("password") 会安全地获取密码，如果不存在也不会报错
            if password_input == st.secrets.get("password"):
                # 如果密码正确，函数返回 True
                return True
            else:
                # 如果密码错误，显示错误信息，并返回 False
                st.error("密码不正确，请重试。")
                return False
        else:
            # 如果用户还未点击按钮，返回 False，不显示任何内容
            return False


# 使用 st.title 设置页面上的主标题
st.title("中央企业、地方国企改革深化提升行动重点量化指标")
# 在主页上添加一些引导性文字
st.write("---")
st.info("请在左侧的侧边栏中选择“中央企业”或“地方国企”页面进行查看。")