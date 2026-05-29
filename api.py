#!/usr/bin/env python3
"""
중국어분석기 — 클라우드 백엔드 (Render.com)
Gemini Vision으로 OCR + 분석, TTS는 gTTS 사용
"""
import os, re, json, base64, io
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import google.generativeai as genai

# ── 초기화 ────────────────────────────────────────────────
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

ANALYSIS_PROMPT = """이 이미지는 책 페이지입니다.
텍스트를 OCR로 추출하고 분석하여 반드시 아래 JSON 형식으로만 응답하세요.
마크다운, 설명 없이 순수 JSON만 출력하세요.

{
  "language": "zh|ja|ko|en",
  "ocr": "원문 전체",
  "sentences": [
    {
      "id": 1,
      "original": "원문 문장",
      "translation": "한국어 번역",
      "tokens": [
        {"text":"단어","pinyin":"병음(중국어)","reading":"읽기(일본어)","meaning":"한국어 뜻","grammar":"품사"}
      ]
    }
  ]
}

tokens는 의미 단위(단어·숙어·문법요소)로 분리. 문장부호 제외."""


# ── 분석 엔드포인트 ───────────────────────────────────────
@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return Response(status=200)
    if not GEMINI_KEY:
        return jsonify({"error": "서버에 GEMINI_API_KEY가 설정되지 않았습니다"}), 500
    try:
        data = request.get_json()
        img_b64 = data.get("image", "")
        img_bytes = base64.b64decode(img_b64)
        response = model.generate_content(
            [{"mime_type": "image/jpeg", "data": base64.b64encode(img_bytes).decode()},
             ANALYSIS_PROMPT],
            generation_config={"temperature": 0.1, "max_output_tokens": 4096}
        )
        text = response.text
        m = re.search(r'\{[\s\S]*\}', text)
        if not m:
            return jsonify({"error": "JSON 파싱 실패: " + text[:120]}), 500
        return jsonify(json.loads(m.group()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── TTS 엔드포인트 ────────────────────────────────────────
LANG_MAP = {"zh": "zh-CN", "ja": "ja", "ko": "ko", "en": "en"}

@app.route("/tts", methods=["GET"])
def tts():
    try:
        from gtts import gTTS
        text = request.args.get("text", "").strip()
        lang = request.args.get("lang", "zh")
        if not text:
            return Response(status=400)
        buf = io.BytesIO()
        gTTS(text=text, lang=LANG_MAP.get(lang, "zh-CN"), slow=False).write_to_fp(buf)
        buf.seek(0)
        return Response(buf.read(), mimetype="audio/mpeg",
                        headers={"Cache-Control": "no-cache"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── 헬스체크 ─────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "key_set": bool(GEMINI_KEY)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
