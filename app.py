import streamlit as st
import subprocess
import os
import tempfile

st.set_page_config(page_title="중국어 문장 분석기", page_icon="📖", layout="wide")
st.title("📖 중국어 책 페이지 분석기")


def heic_to_jpg(file_bytes, filename):
    ext = os.path.splitext(filename)[1].lower()
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(file_bytes)
        src = f.name

    if ext in ['.heic', '.heif']:
        dst = src + '.jpg'
        subprocess.run(['sips', '-s', 'format', 'jpeg', src, '--out', dst], capture_output=True)
        os.unlink(src)
        return dst, True
    return src, False


def analyze_image(tmp_path):
    env = dict(os.environ)
    env.pop('CLAUDECODE', None)

    prompt = (
        f"이 책 페이지의 중국어 텍스트를 분석해주세요.\n\n"
        f"## 1. 원문\n(페이지 텍스트 전체)\n\n"
        f"## 2. 한국어 번역\n(전체 번역)\n\n"
        f"## 3. 문장별 분석\n"
        f"각 문장마다:\n"
        f"- **원문**: 중국어\n"
        f"- **발음**: 병음(Pinyin)\n"
        f"- **번역**: 한국어\n"
        f"- **주요 어휘**: 단어 - 병음 - 뜻\n"
        f"- **문법 포인트**: 특이한 문법/표현 설명\n\n"
        f": @{tmp_path}"
    )

    proc = subprocess.run(
        ['claude', '--print', prompt],
        capture_output=True, text=True, env=env, timeout=120
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[:500] or "분석 실패")
    return proc.stdout.strip()


# 파일 업로드
uploaded = st.file_uploader("책 페이지 이미지를 올려주세요",
                             type=['heic', 'heif', 'jpg', 'jpeg', 'png', 'webp'])

if uploaded:
    file_bytes = uploaded.read()
    col1, col2 = st.columns([1, 2])

    tmp_path, is_converted = heic_to_jpg(file_bytes, uploaded.name)

    with col1:
        st.image(tmp_path, caption=uploaded.name, use_container_width=True)

    with col2:
        if st.button("🔍 분석하기", type="primary", use_container_width=True):
            with st.spinner("분석 중..."):
                try:
                    result = analyze_image(tmp_path)
                    st.markdown(result)
                except Exception as e:
                    st.error(f"오류: {e}")

    # 분석 끝난 뒤 임시 파일 정리 (세션이 끝날 때가 아니라 계속 쓸 수 있게 유지)
    # os.unlink(tmp_path)  # 재분석을 위해 유지
