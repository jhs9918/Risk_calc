# public_dashboard.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# CSV 파일 경로
LOG_FILE = "risk_log.csv"

# 수익률 계산 함수
def calculate_return(profit, invest):
    try:
        return round((profit / invest) * 100, 2)
    except ZeroDivisionError:
        return 0.0

# CSV 불러오기
def load_data():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=[
            "날짜", "진입 가격", "손절 가격", "레버리지", "리스크 비율", "손익($)", "투자금($)"
        ])
    df = pd.read_csv(LOG_FILE)
    df["날짜"] = pd.to_datetime(df["날짜"])
    return df

# 스트림릿 페이지 설정
st.set_page_config(page_title="리스크 수익률 대시보드", page_icon="📈", layout="wide")
st.title("📈 리스크 수익률 대시보드 (공개용)")

# 데이터 불러오기
df = load_data()
if df.empty:
    st.warning("기록된 거래 내역이 없습니다.")
    st.stop()

# 수익률 계산 컬럼 추가
df["수익률 (%)"] = df.apply(lambda row: calculate_return(row["손익($)"], row["투자금($)"]), axis=1)

# 일일 수익률
today = datetime.now().date()
daily_df = df[df["날짜"].dt.date == today]
daily_return = daily_df["수익률 (%)"].mean() if not daily_df.empty else 0.0

# 최근 30일 수익률
recent_30 = df[df["날짜"] >= datetime.now() - timedelta(days=30)]
monthly_return = recent_30["수익률 (%)"].mean() if not recent_30.empty else 0.0

# 수익률 카드 표시
col1, col2 = st.columns(2)
col1.metric("오늘 수익률 평균", f"{daily_return:.2f}%")
col2.metric("최근 30일 평균 수익률", f"{monthly_return:.2f}%")

# 수익률 차트
st.subheader("📊 수익률 추이")
st.line_chart(df.set_index("날짜")["수익률 (%)"].tail(100))

# 최근 거래 요약
st.subheader("📋 최근 거래 기록")
st.dataframe(df.sort_values(by="날짜", ascending=False).head(10))
