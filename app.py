#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 13:45:54 2025

@author: zhz
"""

# main_app.py
import streamlit as st

def check_password():
    """如果用户输入了正确的密码，返回 True"""

    def password_entered():
        """检查用户输入的密码是否正确"""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 第一次运行，显示密码输入框
        st.text_input(
            "请输入密码", type="password", on_change=password_entered, key="password"
        )
        st.write(" ") # 增加一些空白
        return False
    elif not st.session_state["password_correct"]:
        # 密码不正确，显示输入框和错误信息
        st.text_input(
            "请输入密码", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 密码不正确，请重试")
        return False
    else:
        # 密码正确
        return True

# --- 只有密码正确后，才运行下面的主应用 ---

if check_password():
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