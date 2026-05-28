# 중국어 책 페이지 문장 분석기

책 페이지 사진(HEIC, JPG, PNG 등)을 업로드하면 Claude AI가 중국어 문장을 분석해줍니다.

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

```bash
python3 analyze.py <이미지 파일 경로>
```

예시:

```bash
python3 analyze.py Page1.HEIC
python3 analyze.py 活着/Page1.HEIC
```

처음 실행 시 [Anthropic API 키](https://console.anthropic.com) 입력을 요청합니다.  
또는 환경변수로 미리 설정할 수 있습니다:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 분석 결과

- **원문**: 페이지 전체 중국어 텍스트
- **한국어 번역**: 전체 번역
- **문장별 분석**: 병음, 번역, 주요 어휘, 문법 포인트

## 지원 형식

HEIC, JPG, JPEG, PNG, WebP
