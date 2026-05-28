#!/usr/bin/env python3
"""중국어 책 페이지 문장 분석기"""

import sys
import os
import base64
import subprocess
import anthropic

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '.api_key')


def get_api_key() -> str:
    # 환경변수 우선
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if key:
        return key

    # 저장된 키 파일
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            key = f.read().strip()
        if key:
            return key

    # 직접 입력
    print("Anthropic API 키를 입력하세요 (https://console.anthropic.com 에서 발급)")
    key = input("API Key: ").strip()
    if not key:
        print("API 키가 필요합니다.")
        sys.exit(1)

    save = input("다음에도 사용할 수 있게 저장할까요? (y/n): ").strip().lower()
    if save == 'y':
        with open(CONFIG_FILE, 'w') as f:
            f.write(key)
        print(f"저장됨: {CONFIG_FILE}")

    return key


def encode_image(image_path: str) -> tuple:
    ext = os.path.splitext(image_path)[1].lower()

    if ext in ['.heic', '.heif']:
        tmp_path = image_path + '_tmp.jpg'
        try:
            subprocess.run(
                ['sips', '-s', 'format', 'jpeg', image_path, '--out', tmp_path],
                capture_output=True, check=True
            )
            with open(tmp_path, 'rb') as f:
                data = base64.standard_b64encode(f.read()).decode('utf-8')
            return data, 'image/jpeg'
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
    }
    media_type = media_types.get(ext, 'image/jpeg')
    with open(image_path, 'rb') as f:
        data = base64.standard_b64encode(f.read()).decode('utf-8')
    return data, media_type


def analyze(image_path: str):
    if not os.path.exists(image_path):
        print(f"파일 없음: {image_path}")
        sys.exit(1)

    print(f"\n분석 중: {os.path.basename(image_path)}\n" + "=" * 60)

    image_data, media_type = encode_image(image_path)

    client = anthropic.Anthropic(api_key=get_api_key())
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

    print(response.content[0].text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 analyze.py <이미지 파일 경로>")
        print("예시:  python3 analyze.py '活着/Page1.HEIC'")
        sys.exit(1)

    analyze(sys.argv[1])
