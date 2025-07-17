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

def check_password():
    """返回 True 如果用户已登录, 否则返回 False."""
    
    # 检查 session_state 中 "password_correct" 的值
    # 如果它不存在, st.session_state.get() 会返回 None, 也是 False
    if st.session_state.get("password_correct", False):
        return True

    # 如果没有登录, 显示密码输入表单
    with st.form("Credentials"):
        st.text_input("请输入密码", type="password", key="password")
        submitted = st.form_submit_button("确认")
        if submitted:
            # 检查密码是否正确
            if st.session_state["password"] == st.secrets["password"]:
                st.session_state["password_correct"] = True
                # 不要忘记删除密码, 保证安全
                del st.session_state["password"]  
                # 重新运行脚本, 以便进入已登录状态
                st.rerun()
            else:
                st.error("😕 密码不正确")
    return False

if not check_password():
    st.stop()
    
st.sidebar.title("欢迎!")
st.sidebar.hr()
if st.sidebar.button("登出"):
    st.session_state["password_correct"] = False
    st.rerun()

# 设置网页配置，这个标题会显示在浏览器的标签页上

# 使用 st.title 设置页面上的主标题
st.title("中央企业、地方国企改革深化提升行动重点量化指标")

# 在主页上添加一些引导性文字
st.write("---")
st.info("请在左侧的侧边栏中选择“中央企业”或“地方国企”页面进行查看。")