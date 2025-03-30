import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="📊 가상매매 성능 분석", layout="wide")
st.title("📊 Hadol’s 가상매매 분석 대시보드")

# GitHub 정보 불러오기
token = st.secrets["GITHUB_TOKEN"]
username = st.secrets["GITHUB_USERNAME"]
repo = st.secrets["GITHUB_REPO"]
branch = st.secrets["GITHUB_BRANCH"]
target_file = st.secrets["TARGET_FILE"]

api_url = f"https://api.github.com/repos/{username}/{repo}/contents/{target_file}"
res = requests.get(api_url, headers={"Authorization": f"token {token}"})

if res.status_code != 200:
    st.error("❌ GitHub에서 데이터 불러오기 실패")
    st.stop()

import base64
import json

content = base64.b64decode(res.json()["content"]).decode()
positions = json.loads(content)

if not positions:
    st.warning("저장된 계약이 없습니다.")
    st.stop()

df = pd.DataFrame(positions)
df["realized_profit"] = df["realized_profit"].fillna(0)
df["status"] = df["status"].fillna("open")

# 요약
st.metric("총 계약 수", len(df))
st.metric("총 수익 ($)", df[df["realized_profit"] > 0]["realized_profit"].sum())
st.metric("총 손실 ($)", df[df["realized_profit"] < 0]["realized_profit"].sum())
st.metric("순이익 ($)", df["realized_profit"].sum())

# 테이블
st.subheader("📋 계약 내역")
st.dataframe(df[["id", "symbol", "entry_price", "stop_price", "position_usd", "realized_profit", "status"]])
