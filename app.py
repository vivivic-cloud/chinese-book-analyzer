import streamlit as st
import streamlit.components.v1 as components
import subprocess
import os
import base64
import json
import re

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


APP_DIR = os.path.expanduser("~/chinese-book-analyzer")
OCR_SWIFT = os.path.join(APP_DIR, "ocr.swift")
TMP_IMG = os.path.join(APP_DIR, "uploads", "_current.jpg")
os.makedirs(os.path.dirname(TMP_IMG), exist_ok=True)

# 언어 → OCR 언어 코드 + 분석 프롬프트 설정
LANG_CONFIG = {
    "zh": {
        "ocr_langs": ["zh-Hans", "zh-Hant", "en-US"],
        "name": "중국어",
        "analysis_prompt": (
            "## 1. 원문\n(전체 텍스트)\n\n"
            "## 2. 한국어 번역\n\n"
            "## 3. 문장별 분석\n"
            "각 문장마다:\n"
            "- **원문**: 중국어\n"
            "- **발음**: 병음(Pinyin)\n"
            "- **번역**: 한국어\n"
            "- **주요 어휘**: 단어 - 병음 - 뜻\n"
            "- **문법 포인트**: 특이한 문법/표현"
        )
    },
    "ja": {
        "ocr_langs": ["ja-JP", "en-US"],
        "name": "일본어",
        "analysis_prompt": (
            "## 1. 원문\n(전체 텍스트)\n\n"
            "## 2. 한국어 번역\n\n"
            "## 3. 문장별 분석\n"
            "각 문장마다:\n"
            "- **원문**: 일본어\n"
            "- **발음**: 후리가나(로마자)\n"
            "- **번역**: 한국어\n"
            "- **주요 어휘**: 단어 - 읽기 - 뜻\n"
            "- **문법 포인트**: 특이한 문법/표현"
        )
    },
    "ko": {
        "ocr_langs": ["ko-KR", "en-US"],
        "name": "한국어",
        "analysis_prompt": (
            "## 1. 원문\n(전체 텍스트)\n\n"
            "## 2. 어휘 분석\n\n"
            "## 3. 문장별 분석\n"
            "각 문장마다:\n"
            "- **원문**: 한국어\n"
            "- **어휘**: 어려운 단어 - 뜻\n"
            "- **문법 포인트**: 특이한 문법/표현"
        )
    },
    "en": {
        "ocr_langs": ["en-US"],
        "name": "영어",
        "analysis_prompt": (
            "## 1. 원문\n(전체 텍스트)\n\n"
            "## 2. 한국어 번역\n\n"
            "## 3. 문장별 분석\n"
            "각 문장마다:\n"
            "- **원문**: 영어\n"
            "- **번역**: 한국어\n"
            "- **주요 어휘**: 단어 - 뜻\n"
            "- **문법 포인트**: 특이한 표현/숙어"
        )
    }
}


def detect_language(text: str) -> str:
    """Unicode 범위로 주요 언어 감지"""
    cjk = sum(1 for c in text if '一' <= c <= '鿿')
    hiragana = sum(1 for c in text if '぀' <= c <= 'ゟ')
    katakana = sum(1 for c in text if '゠' <= c <= 'ヿ')
    hangul = sum(1 for c in text if '가' <= c <= '퟿')
    total = max(len(text), 1)
    if hangul / total > 0.1:
        return "ko"
    if (hiragana + katakana) / total > 0.05:
        return "ja"
    if cjk / total > 0.1:
        return "zh"
    return "en"


def ocr_image(image_path: str, lang_code: str = None) -> tuple[str, str]:
    """Vision 프레임워크로 OCR 수행 → (추출텍스트, 감지언어코드)"""
    # 1차: 자동 감지로 전체 언어 시도
    langs = LANG_CONFIG.get(lang_code, {}).get("ocr_langs") or \
            ["zh-Hans", "zh-Hant", "ja-JP", "ko-KR", "en-US"]

    proc = subprocess.run(
        ["swift", OCR_SWIFT, image_path] + langs,
        capture_output=True, text=True, timeout=30
    )
    text = proc.stdout.strip()

    # 언어 감지
    detected = detect_language(text) if text else (lang_code or "zh")

    # 감지된 언어가 다르면 해당 언어 설정으로 재시도
    if detected != lang_code and detected in LANG_CONFIG:
        specific_langs = LANG_CONFIG[detected]["ocr_langs"]
        proc2 = subprocess.run(
            ["swift", OCR_SWIFT, image_path] + specific_langs,
            capture_output=True, text=True, timeout=30
        )
        if proc2.stdout.strip():
            text = proc2.stdout.strip()

    return text, detected


def save_image(file_bytes: bytes, filename: str) -> str:
    """업로드 파일을 JPEG로 변환해 저장"""
    ext = os.path.splitext(filename)[1].lower()
    raw_path = TMP_IMG.replace('.jpg', ext)
    with open(raw_path, 'wb') as f:
        f.write(file_bytes)
    if ext in ['.heic', '.heif']:
        subprocess.run(['sips', '-s', 'format', 'jpeg', raw_path, '--out', TMP_IMG],
                       capture_output=True)
    else:
        import shutil
        shutil.copy(raw_path, TMP_IMG)
    return TMP_IMG


def analyze(ocr_text: str, lang_code: str) -> dict:
    """OCR 텍스트 → Claude 분석 → JSON 반환"""
    cfg = LANG_CONFIG.get(lang_code, LANG_CONFIG["zh"])

    if lang_code == "zh":
        token_example = '{"text":"真正","pinyin":"zhēnzhèng","meaning":"진정한, 참된","grammar":"부사/형용사"}'
        token_fields = '"text","pinyin","meaning","grammar"'
    elif lang_code == "ja":
        token_example = '{"text":"永遠","reading":"えいえん","meaning":"영원","grammar":"명사"}'
        token_fields = '"text","reading","meaning","grammar"'
    else:
        token_example = '{"text":"however","meaning":"그러나","grammar":"접속부사"}'
        token_fields = '"text","meaning","grammar"'

    prompt = f"""다음 {cfg['name']} 텍스트를 분석하여 아래 JSON 형식으로만 응답하세요.
마크다운, 설명, 코드블록 없이 순수 JSON만 출력하세요.

{{
  "sentences": [
    {{
      "id": 1,
      "original": "원문 문장",
      "translation": "한국어 번역",
      "tokens": [
        {token_example}
      ]
    }}
  ]
}}

규칙:
- tokens는 의미 단위(단어·숙어·문법요소)로 분리
- 문장부호는 별도 토큰으로 포함
- {token_fields} 필드 포함

텍스트:
{ocr_text}"""

    msg = json.dumps({
        "type": "user",
        "message": {"role": "user", "content": [{"type": "text", "text": prompt}]}
    })
    env = dict(os.environ)
    env.pop('CLAUDECODE', None)
    claude_bin = os.path.expanduser('~/.local/bin/claude')
    proc = subprocess.run(
        [claude_bin, '--print', '--verbose',
         '--input-format', 'stream-json',
         '--output-format', 'stream-json'],
        input=msg, capture_output=True, text=True, env=env, timeout=180
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[:400] or f"Claude 실행 실패 (code {proc.returncode})")

    raw = None
    for line in proc.stdout.splitlines():
        try:
            obj = json.loads(line)
            if obj.get('type') == 'assistant':
                for block in obj.get('message', {}).get('content', []):
                    if block.get('type') == 'text':
                        raw = block['text']
        except Exception:
            pass

    if not raw:
        raise RuntimeError("응답 없음")

    # JSON 추출 (코드블록 제거)
    text = raw.strip()
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        text = m.group(0)
    return json.loads(text)


def render_interactive(data: dict, lang_code: str) -> str:
    space = "true" if lang_code in ("ko", "en") else "false"
    data_json = json.dumps(data, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:transparent;font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;color:#c8c8c8;padding:4px 0 60px}}
.sentence{{display:flex;gap:20px;padding:28px 0;border-bottom:1px solid #222}}
.sentence:last-child{{border-bottom:none}}
.num{{font-size:10px;letter-spacing:.14em;color:#2e2e2e;min-width:22px;padding-top:6px;text-align:right;flex-shrink:0}}
.body{{flex:1;min-width:0}}
.original{{font-size:18px;line-height:2.2;color:#d4d4d4;margin-bottom:10px;word-break:break-all}}
.translation{{font-size:12px;color:#3a3a3a;line-height:1.7;letter-spacing:.02em}}
.token{{cursor:pointer;display:inline;border-bottom:1px solid transparent;transition:color .1s,border-color .1s;padding:0 1px}}
.token:hover{{color:#fff;border-bottom-color:#555}}
.token.active{{color:#fff;border-bottom-color:#888}}
#popup{{position:fixed;background:#1c1c1c;border:1px solid #2a2a2a;padding:20px 22px;min-width:250px;max-width:320px;z-index:9999;display:none;box-shadow:0 16px 48px rgba(0,0,0,.8)}}
.p-close{{position:absolute;top:10px;right:14px;cursor:pointer;color:#333;font-size:12px;line-height:1}}
.p-close:hover{{color:#666}}
.p-word{{font-size:26px;font-weight:300;color:#fff;margin-bottom:3px;letter-spacing:.04em}}
.p-reading{{font-size:12px;color:#555;letter-spacing:.1em;margin-bottom:14px;font-style:italic}}
.p-meaning{{font-size:14px;color:#b0b0b0;line-height:1.7;margin-bottom:10px}}
.p-grammar{{font-size:10px;color:#3a3a3a;letter-spacing:.12em;text-transform:uppercase}}
</style></head><body>
<div id="popup">
  <span class="p-close" onclick="closePopup()">✕</span>
  <div class="p-word" id="pw"></div>
  <div class="p-reading" id="pr"></div>
  <div class="p-meaning" id="pm"></div>
  <div class="p-grammar" id="pg"></div>
</div>
<div id="content"></div>
<script>
const DATA={data_json};
const spaceTokens={space};
const popup=document.getElementById('popup');
let active=null;

function closePopup(){{
  popup.style.display='none';
  if(active){{active.classList.remove('active');active=null;}}
}}

function showPopup(tok,el){{
  if(active)active.classList.remove('active');
  active=el;el.classList.add('active');
  document.getElementById('pw').textContent=tok.text||'';
  document.getElementById('pr').textContent=tok.pinyin||tok.reading||'';
  document.getElementById('pm').textContent=tok.meaning||'';
  document.getElementById('pg').textContent=tok.grammar||'';
  popup.style.display='block';
  const r=el.getBoundingClientRect();
  const pw=320,ph=180;
  let x=r.left,y=r.bottom+8;
  if(x+pw>window.innerWidth-8)x=window.innerWidth-pw-8;
  if(y+ph>window.innerHeight)y=r.top-ph-8;
  if(y<0)y=8;
  popup.style.left=Math.max(4,x)+'px';
  popup.style.top=y+'px';
}}

document.addEventListener('click',function(e){{
  if(!popup.contains(e.target)&&!e.target.classList.contains('token'))closePopup();
}});

const content=document.getElementById('content');
(DATA.sentences||[]).forEach(s=>{{
  const wrap=document.createElement('div');
  wrap.className='sentence';
  const num=document.createElement('div');
  num.className='num';num.textContent=s.id;
  const body=document.createElement('div');
  body.className='body';
  const orig=document.createElement('div');
  orig.className='original';
  (s.tokens||[]).forEach((tok,i)=>{{
    const span=document.createElement('span');
    span.className='token';
    span.textContent=tok.text;
    span.addEventListener('click',function(e){{e.stopPropagation();showPopup(tok,this);}});
    orig.appendChild(span);
    if(spaceTokens&&i<s.tokens.length-1)orig.appendChild(document.createTextNode(' '));
  }});
  const trans=document.createElement('div');
  trans.className='translation';trans.textContent=s.translation||'';
  body.appendChild(orig);body.appendChild(trans);
  wrap.appendChild(num);wrap.appendChild(body);
  content.appendChild(wrap);
}});
</script></body></html>"""


LANG_LABELS = {"zh": "🇨🇳 중국어", "ja": "🇯🇵 일본어", "ko": "🇰🇷 한국어", "en": "🇺🇸 영어"}

if uploaded:
    file_bytes = uploaded.read()
    img_path = save_image(file_bytes, uploaded.name)

    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.image(img_path, use_container_width=True)

    with col2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        name = os.path.splitext(uploaded.name)[0]
        st.markdown(f"<div style='font-size:12px;color:#4a4a4a;letter-spacing:0.08em;margin-bottom:16px'>{name}</div>",
                    unsafe_allow_html=True)

        if st.button("분 석"):
            with st.spinner("OCR 중..."):
                ocr_text, lang_code = ocr_image(img_path)

            if not ocr_text.strip():
                st.error("텍스트를 인식하지 못했습니다.")
            else:
                lang_label = LANG_LABELS.get(lang_code, lang_code)
                st.markdown(
                    f"<div style='font-size:10px;letter-spacing:0.12em;color:#3a3a3a;margin-bottom:8px'>"
                    f"{lang_label} · Vision OCR</div>",
                    unsafe_allow_html=True
                )
                with st.expander("OCR 원문", expanded=False):
                    st.code(ocr_text, language=None)

                with st.spinner("분석 중..."):
                    try:
                        result = analyze(ocr_text, lang_code)
                    except Exception as e:
                        st.error(str(e))
                        result = None

                if result:
                    st.markdown('<hr class="tw-rule" style="margin:24px 0">', unsafe_allow_html=True)
                    n = len(result.get("sentences", []))
                    html = render_interactive(result, lang_code)
                    components.html(html, height=max(500, n * 170) + 200, scrolling=True)


# ── 하단 ──────────────────────────────────────────
st.markdown('<hr class="tw-rule" style="margin-top:60px">', unsafe_allow_html=True)
st.markdown("""
<div class="tw-footer">
  <span>중국어.분석기</span>
  <span>powered by Claude</span>
</div>
""", unsafe_allow_html=True)
