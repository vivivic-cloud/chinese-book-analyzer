import streamlit as st
import base64
import subprocess
import os
import json
import tempfile
import anthropic

st.set_page_config(page_title="중국어 문장 분석기", page_icon="📖", layout="wide")
st.title("📖 중국어 책 페이지 분석기")


def get_client():
    # Claude Code 키체인에서 OAuth 토큰 자동 읽기
    result = subprocess.run(
        ['security', 'find-generic-password', '-s', 'Claude Code-credentials', '-w'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        creds = json.loads(result.stdout.strip())
        token = creds.get('claudeAiOauth', {}).get('accessToken', '')
        if token:
            return anthropic.Anthropic(
                auth_token=token,
                base_url="https://api.anthropic.com",
            )
    st.error("Claude Code 로그인 정보를 찾을 수 없습니다. Claude Code를 먼저 실행해주세요.")
    st.stop()


def encode_image(file_bytes, filename):
    ext = os.path.splitext(filename)[1].lower()

    if ext in ['.heic', '.heif']:
        with tempfile.NamedTemporaryFile(suffix='.heic', delete=False) as tmp_in:
            tmp_in.write(file_bytes)
            tmp_in_path = tmp_in.name
        tmp_out_path = tmp_in_path + '.jpg'
        try:
            subprocess.run(
                ['sips', '-s', 'format', 'jpeg', tmp_in_path, '--out', tmp_out_path],
                capture_output=True, check=True
            )
            with open(tmp_out_path, 'rb') as f:
                data = base64.standard_b64encode(f.read()).decode('utf-8')
            return data, 'image/jpeg'
        finally:
            os.unlink(tmp_in_path)
            if os.path.exists(tmp_out_path):
                os.unlink(tmp_out_path)

    media_types = {
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.png': 'image/png', '.webp': 'image/webp',
    }
    return base64.standard_b64encode(file_bytes).decode('utf-8'), media_types.get(ext, 'image/jpeg')


# 파일 업로드
uploaded = st.file_uploader("책 페이지 이미지를 올려주세요",
                             type=['heic', 'heif', 'jpg', 'jpeg', 'png', 'webp'])

if uploaded:
    col1, col2 = st.columns([1, 2])

    with col1:
        file_bytes = uploaded.read()
        ext = os.path.splitext(uploaded.name)[1].lower()

        if ext in ['.heic', '.heif']:
            with tempfile.NamedTemporaryFile(suffix='.heic', delete=False) as tmp_in:
                tmp_in.write(file_bytes)
                tmp_in_path = tmp_in.name
            tmp_out_path = tmp_in_path + '_preview.jpg'
            subprocess.run(['sips', '-s', 'format', 'jpeg', tmp_in_path, '--out', tmp_out_path],
                           capture_output=True)
            st.image(tmp_out_path, caption=uploaded.name, use_container_width=True)
            os.unlink(tmp_in_path)
            os.unlink(tmp_out_path)
        else:
            st.image(file_bytes, caption=uploaded.name, use_container_width=True)

    with col2:
        if st.button("🔍 분석하기", type="primary", use_container_width=True):
            with st.spinner("분석 중..."):
                try:
                    image_data, media_type = encode_image(file_bytes, uploaded.name)
                    client = get_client()
                    response = client.messages.create(
                        model="claude-opus-4-7",
                        max_tokens=4096,
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": image_data,
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": """이 책 페이지의 중국어 텍스트를 분석해주세요.

## 1. 원문
(페이지 텍스트 전체)

## 2. 한국어 번역
(전체 번역)

## 3. 문장별 분석
각 문장마다:
- **원문**: 중국어
- **발음**: 병음(Pinyin)
- **번역**: 한국어
- **주요 어휘**: 단어 - 병음 - 뜻
- **문법 포인트**: 특이한 문법/표현 설명"""
                                }
                            ]
                        }]
                    )
                    st.markdown(response.content[0].text)
                except Exception as e:
                    st.error(f"오류: {e}")
