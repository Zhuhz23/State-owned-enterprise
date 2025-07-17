#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 13:45:54 2025

@author: zhz
"""

# main_app.py
import streamlit as st

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

st.set_page_config(
    page_title="国企改革量化指标分析",
    layout="wide"
)

if check_password():
    # 设置网页配置，这个标题会显示在浏览器的标签页上
    st.sidebar.success("登录成功！请选择一个页面。")
    
    # 使用 st.title 设置页面上的主标题
    st.title("中央企业、地方国企改革深化提升行动重点量化指标")
    
    # 在主页上添加一些引导性文字
    st.write("---")
    st.info("请在左侧的侧边栏中选择“中央企业”或“地方国企”页面进行查看。")