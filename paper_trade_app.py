import streamlit as st
import json
import os
import base64
import requests
from calculator import calculate_stop_loss_price
from asset_manager import get_paper_asset, update_paper_asset

# 바이낸스 선물 티커 목록 가져오기 (자동완성용)
@st.cache_data(ttl=3600)
def get_binance_futures_symbols():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    res = requests.get(url)
    data = res.json()
    symbols = [s["symbol"] for s in data["symbols"] if s["contractType"] == "PERPETUAL" and s["quoteAsset"] == "USDT"]
    return sorted(symbols)

# GitHub 자동 푸시
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

# 파일 경로
POSITIONS_FILE = "saved_positions.json"

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "r") as f:
            return json.load(f)
    return []

def save_positions(data):
    with open(POSITIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    with open(POSITIONS_FILE, "r") as f:
        push_to_github(f.read())

# 기본 설정
st.set_page_config(page_title="📘 가상 리스크 계산기", layout="wide")
st.title("📘 Hadol’s 가상 리스크 계산기 (Paper Trading)")

total_asset = get_paper_asset()
st.sidebar.markdown(f"💰 **총 자산: ${total_asset:,.2f}**")

positions = load_positions()
selected_id = st.sidebar.selectbox("📂 저장된 계약 선택", ["새 계약 입력"] + [p["id"] for p in positions])

# 새 계약 입력
if selected_id == "새 계약 입력":
    st.subheader("🆕 새 계약 입력")
    futures_symbols = get_binance_futures_symbols()
    symbol = st.selectbox("종목 선택 (자동완성)", options=futures_symbols, index=futures_symbols.index("BTCUSDT") if "BTCUSDT" in futures_symbols else 0)

    entry_price = st.number_input("진입 가격 ($)", value=27000.0, format="%.6f")
    leverage = st.number_input("레버리지", 1, 125, 10)
    direction = st.radio("포지션 방향", ["LONG", "SHORT"])
    position_usd = st.number_input("포지션 금액 ($)", value=500.0, format="%.2f")
    position_amt = position_usd / entry_price

    risk_ratio = st.slider("리스크 비율 (%)", 0.1, 10.0, 2.0) / 100
    risk_result = calculate_stop_loss_price(total_asset, position_amt, leverage, risk_ratio, entry_price)
    suggested_stop = risk_result["손절 가격"]

    stop_price_method = st.radio("손절가 방식", ["자동", "직접"])
    if stop_price_method == "자동":
        stop_price = suggested_stop
    else:
        stop_price = st.number_input("직접 손절 가격 입력 ($)", value=suggested_stop, format="%.6f")
        loss_amt = (entry_price - stop_price) * position_amt if direction == "LONG" else (stop_price - entry_price) * position_amt
        risk_pct = (loss_amt / total_asset) * 100 if total_asset > 0 else 0
        st.info(f"⚠️ 손실 예상: ${loss_amt:.2f} → 자산 대비 {risk_pct:.2f}%")

    if st.button("💾 계약 저장"):
        new_id = f"{symbol}_{entry_price}_{position_usd}_{direction}"
        new_position = {
            "id": new_id,
            "symbol": symbol,
            "entry_price": entry_price,
            "leverage": leverage,
            "position_usd": position_usd,
            "position_amt": position_amt,
            "stop_price": stop_price,
            "direction": direction,
            "realized_profit": 0,
            "status": "open"
        }
        positions.append(new_position)
        save_positions(positions)
        st.success(f"✅ 계약 저장 완료: {new_id}")

# 이하 기존 계약 보기 및 조작 코드는 동일 (줄임)
