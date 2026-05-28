import streamlit as st
import subprocess
import os

st.set_page_config(page_title="중국어.분석기", page_icon=None, layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
  background: #1a1a1a !important;
  color: #c8c8c8 !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Streamlit 기본 크롬 제거 */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

section.main > div { padding-top: 0 !important; }
.block-container {
  max-width: 800px !important;
  padding: 0 40px !important;
}

/* ── 헤더 ── */
.tw-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px 0 28px;
  font-size: 14px;
  letter-spacing: 0.01em;
}
.tw-logo { color: #c8c8c8; }
.tw-logo b { font-weight: 600; color: #fff; }

/* ── 구분선 ── */
.tw-rule {
  border: none;
  border-top: 1px solid #2e2e2e;
  margin: 0;
}

/* ── 메타 라벨 ── */
.tw-meta {
  display: flex;
  justify-content: flex-end;
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #4a4a4a;
  padding: 12px 0 24px;
}

/* ── 파일 업로더 ── */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] > div,
section[data-testid="stFileUploaderDropzone"] {
  background: #1e1e1e !important;
  border: 1px dashed #2e2e2e !important;
  border-radius: 0 !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploaderDropzone"] > div:hover {
  border-color: #444 !important;
  background: #222 !important;
}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] p {
  color: #3a3a3a !important;
  font-size: 12px !important;
  letter-spacing: 0.06em !important;
}
[data-testid="stFileUploaderDropzone"] svg {
  fill: #333 !important;
  stroke: #333 !important;
}
/* Browse files 버튼 */
[data-testid="stFileUploaderDropzone"] button,
[data-testid="baseButton-secondary"] {
  background: transparent !important;
  border: 1px solid #2e2e2e !important;
  color: #444 !important;
  border-radius: 0 !important;
  font-size: 10px !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  box-shadow: none !important;
}

/* ── 이미지 ── */
[data-testid="stImage"] img {
  border: 1px solid #2a2a2a !important;
  display: block;
}

/* ── 분석 버튼 ── */
.stButton > button {
  background: transparent !important;
  border: 1px solid #333 !important;
  color: #888 !important;
  border-radius: 0 !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 10px !important;
  font-weight: 400 !important;
  letter-spacing: 0.16em !important;
  text-transform: uppercase !important;
  padding: 10px 24px !important;
  transition: border-color 0.15s, color 0.15s !important;
  width: auto !important;
}
.stButton > button:hover {
  border-color: #666 !important;
  color: #ccc !important;
  background: transparent !important;
}
.stButton > button:active {
  background: #242424 !important;
}

/* ── 스피너 ── */
.stSpinner { color: #444 !important; }
.stSpinner > div > div { border-top-color: #555 !important; }

/* ── 결과 마크다운 ── */
.stMarkdown h2 {
  font-size: 10px !important;
  font-weight: 400 !important;
  letter-spacing: 0.16em !important;
  text-transform: uppercase !important;
  color: #4a4a4a !important;
  margin-top: 40px !important;
  margin-bottom: 14px !important;
  border: none !important;
  padding: 0 !important;
}
.stMarkdown h3 {
  font-size: 13px !important;
  font-weight: 500 !important;
  color: #e0e0e0 !important;
  margin-top: 28px !important;
  margin-bottom: 8px !important;
}
.stMarkdown p {
  font-size: 15px !important;
  line-height: 1.9 !important;
  color: #b0b0b0 !important;
  margin-bottom: 10px !important;
}
.stMarkdown strong { color: #e0e0e0 !important; }
.stMarkdown li {
  font-size: 14px !important;
  line-height: 1.8 !important;
  color: #a0a0a0 !important;
  margin-bottom: 4px !important;
}
.stMarkdown hr { border-color: #2e2e2e !important; margin: 32px 0 !important; }

/* ── 에러 ── */
.stAlert { background: #1f1414 !important; border: 1px solid #3d2020 !important; border-radius: 0 !important; }

/* ── 하단 바 ── */
.tw-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  font-size: 11px;
  color: #3a3a3a;
  letter-spacing: 0.06em;
  margin-top: 60px;
}
</style>
""", unsafe_allow_html=True)


# ── 헤더 ──────────────────────────────────────────
st.markdown("""
<div class="tw-header">
  <div class="tw-logo">중국어<b>.분석기</b></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="tw-rule">', unsafe_allow_html=True)
st.markdown('<div class="tw-meta">페이지 분석 ▶</div>', unsafe_allow_html=True)


# ── 파일 업로드 ────────────────────────────────────
uploaded = st.file_uploader(
    "이미지를 드래그하거나 클릭해서 올려주세요",
    type=['heic', 'heif', 'jpg', 'jpeg', 'png', 'webp'],
    label_visibility="collapsed"
)


UPLOAD_DIR = os.path.expanduser("~/chinese-book-analyzer/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def to_jpg(file_bytes, filename):
    ext = os.path.splitext(filename)[1].lower()
    src = os.path.join(UPLOAD_DIR, "current" + ext)
    with open(src, 'wb') as f:
        f.write(file_bytes)
    if ext in ['.heic', '.heif']:
        dst = os.path.join(UPLOAD_DIR, "current.jpg")
        subprocess.run(['sips', '-s', 'format', 'jpeg', src, '--out', dst], capture_output=True)
        return dst
    return src


def analyze(tmp_path):
    env = dict(os.environ)
    env.pop('CLAUDECODE', None)
    prompt = (
        "이 책 페이지의 중국어 텍스트를 분석해주세요.\n\n"
        "## 1. 원문\n(페이지 텍스트 전체)\n\n"
        "## 2. 한국어 번역\n(전체 번역)\n\n"
        "## 3. 문장별 분석\n"
        "각 문장마다:\n"
        "- **원문**: 중국어\n"
        "- **발음**: 병음(Pinyin)\n"
        "- **번역**: 한국어\n"
        "- **주요 어휘**: 단어 - 병음 - 뜻\n"
        "- **문법 포인트**: 특이한 문법/표현 설명\n\n"
        f": @{tmp_path}"
    )
    proc = subprocess.run(
        ['claude', '--print', prompt],
        capture_output=True, text=True, env=env, timeout=120
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[:400] or "분석 실패")
    return proc.stdout.strip()


if uploaded:
    tmp_path = to_jpg(uploaded.read(), uploaded.name)

    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.image(tmp_path, use_container_width=True)

    with col2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        name = os.path.splitext(uploaded.name)[0]
        st.markdown(f"<div style='font-size:12px;color:#4a4a4a;letter-spacing:0.08em;margin-bottom:20px'>{name}</div>", unsafe_allow_html=True)

        if st.button("분 석"):
            with st.spinner(""):
                try:
                    result = analyze(tmp_path)
                    st.markdown("---")
                    st.markdown(result)
                except Exception as e:
                    st.error(str(e))


# ── 하단 ──────────────────────────────────────────
st.markdown('<hr class="tw-rule" style="margin-top:60px">', unsafe_allow_html=True)
st.markdown("""
<div class="tw-footer">
  <span>중국어.분석기</span>
  <span>powered by Claude</span>
</div>
""", unsafe_allow_html=True)
