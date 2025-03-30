import streamlit as st
import json
import os
from calculator import calculate_stop_loss_price
from logger import log_paper_trade
from asset_manager import get_paper_asset, update_paper_asset

import base64
import requests

# GitHub 자동 커밋 함수
def push_to_github(content):
    token = st.secrets["GITHUB_TOKEN"]
    username = st.secrets["GITHUB_USERNAME"]
    repo = st.secrets["GITHUB_REPO"]
    branch = st.secrets["GITHUB_BRANCH"]
    target_file = st.secrets["TARGET_FILE"]

    api_url = f"https://api.github.com/repos/{username}/{repo}/contents/{target_file}"
    res = requests.get(api_url, headers={"Authorization": f"token {token}"})
    sha = res.json().get("sha", None)

    encoded_content = base64.b64encode(content.encode()).decode()
    payload = {
        "message": "📌 Auto-update saved_positions.json from Streamlit",
        "content": encoded_content,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    res = requests.put(api_url, json=payload, headers={"Authorization": f"token {token}"})
    if res.status_code in [200, 201]:
        st.success("✅ GitHub에 자동 커밋 완료!")
    else:
        st.error(f"❌ GitHub 커밋 실패: {res.status_code}")
        st.json(res.json())

# Streamlit 설정
st.set_page_config(page_title="Hadol’s 가상 리스크 계산기", page_icon="📘", layout="wide")

st.title("📘 Hadol’s 가상 리스크 계산기 (Paper Trading)")
total_asset = get_paper_asset()
st.sidebar.subheader(f"💰 가상 총 자산: ${total_asset:,}")

# 사용자 입력
symbol = st.text_input("종목 티커", value="BTCUSDT")
entry_price = st.number_input("진입 가격 ($)", value=27000.0)
leverage = st.number_input("레버리지", 1, 125, 10)
position_usd = st.number_input("포지션 금액 ($)", value=500.0)
position_amt = position_usd / entry_price

risk_ratio = st.slider("리스크 비율 (%)", 0.1, 10.0, 2.0) / 100
risk_result = calculate_stop_loss_price(total_asset, position_amt, leverage, risk_ratio, entry_price)
suggested_stop = risk_result["손절 가격"]

use_auto = st.radio("리스크 기준 손절가 사용?", ["예", "아니오"])
stop_price = suggested_stop if use_auto == "예" else (
    entry_price * (1 - st.number_input("손절 퍼센트 (%)", value=3.0) / 100)
    if st.radio("직접 입력 방식", ["퍼센트", "가격"]) == "퍼센트"
    else st.number_input("직접 손절 가격 입력 ($)", value=suggested_stop)
)

st.write(f"최종 손절 가격: ${stop_price:.2f}")

col1, col2, col3 = st.columns(3)
col1.metric("손절 가격", f"${stop_price:,.2f}")
col2.metric("리스크 비율", f"{risk_ratio*100:.2f}%")
col3.metric("총 자산", f"${total_asset:,}")

# 계약 저장
new_position = {
    "id": f"{symbol}_{entry_price}_{position_usd}",
    "symbol": symbol,
    "entry_price": entry_price,
    "leverage": leverage,
    "position_usd": position_usd,
    "position_amt": position_amt,
    "stop_price": stop_price,
    "realized_profit": 0,
    "status": "open"
}

if st.button("💾 계약 저장"):
    file_path = "saved_positions.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            saved = json.load(f)
    else:
        saved = []
    saved.append(new_position)
    with open(file_path, "w") as f:
        json.dump(saved, f, indent=2)
    with open(file_path, "r") as f:
        push_to_github(f.read())

# 백업 다운로드
if os.path.exists("saved_positions.json"):
    with open("saved_positions.json", "rb") as f:
        st.download_button("📥 계약 JSON 백업 다운로드", f, "saved_positions.json", mime="application/json")
