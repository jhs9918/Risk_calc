import requests
import base64
import os
import streamlit as st

def commit_to_github(local_file="saved_positions.json"):
    # secrets from streamlit cloud
    token = st.secrets["GITHUB_TOKEN"]
    username = st.secrets["GITHUB_USERNAME"]
    repo = st.secrets["GITHUB_REPO"]
    path = st.secrets["GITHUB_FILE_PATH"]
    branch = st.secrets.get("GITHUB_BRANCH", "main")

    api_url = f"https://api.github.com/repos/{username}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    # 현재 파일 SHA 가져오기
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        sha = res.json()["sha"]
    else:
        st.error(f"❌ SHA 가져오기 실패: {res.status_code}")
        return False

    # 파일 base64 인코딩
    with open(local_file, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    payload = {
        "message": "💾 자동 커밋: 가상 포지션 업데이트",
        "content": content,
        "branch": branch,
        "sha": sha
    }

    # 업로드 요청
    res = requests.put(api_url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        st.success("✅ GitHub 자동 커밋 성공!")
        return True
    else:
        st.error(f"❌ GitHub 커밋 실패: {res.status_code}")
        st.code(res.text)
        return False
