#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, subprocess, re, webbrowser, threading

CLAUDE = os.path.expanduser('~/.local/bin/claude')
DIR = os.path.dirname(os.path.abspath(__file__))

PROMPT = """이미지의 텍스트를 분석하여 반드시 아래 JSON 형식으로만 응답하세요.
마크다운, 설명 없이 순수 JSON만 출력하세요.

{
  "language": "zh|ja|ko|en",
  "ocr": "이미지에서 추출한 전체 원문",
  "sentences": [
    {
      "id": 1,
      "original": "원문 문장",
      "translation": "한국어 번역",
      "tokens": [
        {"text":"단어","pinyin":"병음(중국어)","reading":"읽기(일본어)","meaning":"한국어 뜻","grammar":"품사/문법"}
      ]
    }
  ]
}

tokens는 의미 단위(단어·숙어·문법요소·문장부호)로 분리."""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self._serve(os.path.join(DIR, 'local.html'), 'text/html; charset=utf-8')
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path == '/analyze':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            try:
                result = self._run_claude(body.get('image', ''))
                self._json(200, result)
            except Exception as e:
                self._json(500, {'error': str(e)})

    def _serve(self, path, mime):
        try:
            with open(path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', len(data))
            self.end_headers()
            self.wfile.write(data)
        except:
            self.send_response(500); self.end_headers()

    def _json(self, status, obj):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def _run_claude(self, img_b64):
        payload = json.dumps({
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
                    {"type": "text", "text": PROMPT}
                ]
            }
        })
        env = os.environ.copy()
        env.pop('CLAUDECODE', None)

        proc = subprocess.run(
            [CLAUDE, '--print', '--verbose',
             '--input-format', 'stream-json',
             '--output-format', 'stream-json'],
            input=payload, capture_output=True, text=True, env=env
        )

        text = None
        for line in proc.stdout.splitlines():
            try:
                obj = json.loads(line)
                if obj.get('type') == 'assistant':
                    for block in obj.get('message', {}).get('content', []):
                        if block.get('type') == 'text':
                            text = block['text']
            except Exception:
                pass

        if not text:
            stderr = proc.stderr[:400] if proc.stderr else ''
            raise Exception(f'Claude 응답 없음. claude 로그인 확인: {stderr}')

        m = re.search(r'\{[\s\S]*\}', text)
        if not m:
            raise Exception('JSON 파싱 실패')
        return json.loads(m.group())


if __name__ == '__main__':
    port = 8888
    server = HTTPServer(('localhost', port), Handler)
    url = f'http://localhost:{port}'
    print(f'✓ 서버 시작: {url}')
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n종료')
