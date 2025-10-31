# 📝 HTML 채점 시스템

AI 기반 HTML 파일 자동 채점 시스템입니다. OpenAI GPT-4o-mini 모델을 활용하여 문법, 단어, 완성도를 자동으로 평가합니다.

## ✨ 주요 기능

- 📁 **HTML 파일 업로드**: 드래그 앤 드롭으로 간편하게 업로드
- 🌐 **URL 입력**: 웹 사이트 URL을 직접 입력하여 채점
- 🤖 **AI 자동 채점**: OpenAI API를 활용한 고급 문법/단어/완성도 검사
- 📊 **실시간 점수 표시**: 각 항목별 점수와 총점 실시간 계산
- 📱 **모바일 반응형**: PC, 태블릿, 모바일 모두 지원

## 🚀 배포 가이드

### ⚠️ 중요: Vercel은 Python을 제한적으로만 지원합니다!
Python Flask 앱은 **Railway** 또는 **Render**를 추천합니다.

---

## 📦 추천 배포 플랫폼

### 1️⃣ Render (무료! 추천!) ⭐⭐⭐⭐⭐

**장점:**
- ✅ **완전 무료** 플랜
- ✅ Flask 완벽 지원
- ✅ 자동 HTTPS 제공
- ✅ GitHub 자동 배포
- ✅ `render.yaml` 자동 인식

**단점:**
- ⚠️ 15분 비활성 후 슬립 (첫 요청 시 30초~1분 소요)

---

## 🚀 **Render 배포 방법 (5분 완성!)**

### **방법 1: render.yaml 사용 (자동 설정 - 가장 쉬움!)**

1. **https://render.com** 접속 후 GitHub로 로그인

2. **"New +"** → **"Blueprint"** 클릭

3. **GitHub 저장소 연결**
   - 저장소 선택: `html-grading-system`
   - Render가 자동으로 `render.yaml` 감지! ✅

4. **Environment Variables 설정:**
   ```
   OPENAI_API_KEY = sk-proj-your-actual-key
   ```
   
5. **"Apply"** 클릭 → 자동 배포 시작! 🎉

6. **배포 완료 후:**
   - URL: `https://html-grading-system.onrender.com`
   - `index.html` 파일 업데이트 필요 (아래 참고)

---

### **방법 2: 수동 설정**

1. **https://render.com** 접속

2. **"New +"** → **"Web Service"** 클릭

3. **GitHub 저장소 연결**

4. **설정 입력:**
   - **Name:** `html-grading-system`
   - **Region:** `Oregon (US West)` (가장 빠름)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api.index:app`
   
   ⚠️ **주의:** Render는 자동으로 `$PORT`를 설정하므로, `--bind 0.0.0.0:$PORT`는 선택사항입니다.
   
5. **Environment Variables 추가:**
   ```
   OPENAI_API_KEY = sk-proj-your-actual-key
   PYTHON_VERSION = 3.11.0
   ```

6. **"Create Web Service"** 클릭

---

### **⚠️ 배포 후 필수 작업!**

Render 배포 후 실제 URL을 받으면, `index.html` 파일을 업데이트해야 합니다:

```javascript
// index.html 965번째 줄
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : 'https://실제-받은-url.onrender.com';  // 여기를 실제 URL로 변경!
```

**예시:**
- Render가 준 URL: `https://html-grading-system-abc123.onrender.com`
- 위 코드에서 `https://html-grading-system.onrender.com` → `https://html-grading-system-abc123.onrender.com` 으로 변경

그 후 다시 커밋 & 푸시:
```bash
git add index.html
git commit -m "Update API URL to Render deployment"
git push origin main
```

Render가 자동으로 재배포합니다!

---

### 2️⃣ Railway (유료 크레딧) ⭐⭐⭐⭐

**장점:**
- ✅ Flask 완벽 지원
- ✅ 무료 크레딧: $5/월
- ✅ 슬립 없음 (항상 빠름)

**배포 방법:**
1. **https://railway.app** 접속
2. **"New Project"** → **"Deploy from GitHub repo"**
3. **Environment Variables:** `OPENAI_API_KEY` 설정
4. 자동 배포 완료!

---

## 🌐 **프론트엔드 호스팅 (선택사항)**

백엔드(Flask API)는 Render에 배포하고, 프론트엔드(`index.html`)는 별도로 호스팅할 수 있습니다:

### **Option 1: GitHub Pages (무료, 가장 쉬움)**

```bash
# 프론트엔드만 별도 브랜치 생성
git checkout -b gh-pages
git add index.html
git commit -m "Deploy frontend to GitHub Pages"
git push origin gh-pages

# GitHub 저장소 → Settings → Pages → Source: gh-pages
```

**URL:** `https://YOUR_USERNAME.github.io/html-grading-system/`

### **Option 2: Vercel (무료, 정적 파일)**

1. **https://vercel.com** 접속
2. **Import Project** → GitHub 저장소
3. 자동 배포 완료!

**URL:** `https://your-project.vercel.app`

### **Option 3: 백엔드와 함께 호스팅 (간단)**

Render에서 백엔드와 함께 `index.html`도 제공:

`api/index.py`에 라우트 추가:
```python
@app.route('/')
def home():
    return app.send_static_file('index.html')
```

---

## 📁 **GitHub 저장소 생성**

```bash
# 현재 디렉토리에서 Git 초기화
git init

# 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: HTML 채점 시스템 (Render 배포)"

# GitHub 저장소와 연결 (본인의 저장소 URL로 변경)
git remote add origin https://github.com/YOUR_USERNAME/html-grading-system.git

# 푸시
git branch -M main
git push -u origin main
```

---

## 🛠️ 로컬 개발 (빠른 시작)

### ⚡ **5분 안에 실행하기**

#### **1단계: API 키 준비**

1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. "Create new secret key" 클릭하여 API 키 발급
3. 발급된 키 복사 (예: `sk-proj-...`)

#### **2단계: 환경 설정**

```bash
# 📁 프로젝트 폴더로 이동
cd score

# 📦 Python 라이브러리 설치
pip install -r requirements.txt
```

**설치되는 라이브러리:**
- `Flask` - 웹 서버
- `flask-cors` - CORS 처리
- `requests` - HTTP 요청
- `python-dotenv` - 환경 변수 로드

#### **3단계: API 키 설정**

**Windows:**
```bash
copy env.example .env
notepad .env
```

**macOS/Linux:**
```bash
cp env.example .env
nano .env
```

**.env 파일 내용:**
```env
OPENAI_API_KEY=sk-proj-여기에-실제-API-키-붙여넣기
```

💡 **중요**: `.env` 파일은 Git에 업로드되지 않습니다 (`.gitignore`에 포함됨)

#### **4단계: Flask 서버 실행**

```bash
# 서버 시작
python api/index.py
```

✅ **성공 메시지:**
```
* Serving Flask app 'index'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

❌ **경고가 나온다면:**
```
⚠️ 경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다!
```
→ `.env` 파일을 다시 확인하세요!

#### **5단계: 브라우저에서 열기**

**방법 1: 직접 파일 열기 (간단)**
- `index.html` 파일을 브라우저로 드래그 앤 드롭
- 또는 더블클릭

**방법 2: HTTP 서버 사용 (권장)**

**새 터미널 창**을 열고:
```bash
# Python 내장 서버 실행
python -m http.server 8000
```

그 다음 브라우저에서:
```
http://localhost:8000/index.html
```

---

### 🎯 **동작 확인**

1. ✅ Flask 서버: `http://127.0.0.1:5000` (백엔드)
2. ✅ 프론트엔드: `http://localhost:8000/index.html` (화면)
3. ✅ 우측 상단에 "✅ AI 채점 활성화됨" 표시
4. ✅ HTML 파일 업로드 → 채점 버튼 클릭 → AI 분석 시작!

---

### 🐛 **문제 해결**

#### **1. "ModuleNotFoundError: No module named 'flask'"**
```bash
# 해결: 라이브러리 재설치
pip install -r requirements.txt
```

#### **2. "OPENAI_API_KEY 환경 변수가 설정되지 않았습니다"**
```bash
# 해결: .env 파일 확인
# Windows
notepad .env

# macOS/Linux
cat .env
```

내용이 이렇게 되어 있는지 확인:
```
OPENAI_API_KEY=sk-proj-실제키...
```

#### **3. "Address already in use (포트 5000 사용 중)"**
```bash
# 해결: 다른 Flask 서버 종료 후 재시작
# 또는 포트 변경
python api/index.py  # 코드에서 포트를 5001로 변경
```

#### **4. "Failed to fetch / 서버 연결 실패"**
- Flask 서버가 실행 중인지 확인
- `http://127.0.0.1:5000` 접속해서 JSON 응답 확인
- 방화벽이 5000 포트를 차단하는지 확인

#### **5. "한글이 깨져 보임"**
→ 이미 수정됨! (`app.config['JSON_AS_ASCII'] = False`)

---

### 🔄 **개발 워크플로우**

```bash
# 1. Flask 서버 실행 (터미널 1)
python api/index.py

# 2. 파일 수정 (index.html, api/index.py)
# ... 코드 수정 ...

# 3. 서버 재시작 (Flask는 auto-reload 지원)
# Ctrl+C → python api/index.py

# 4. 브라우저 새로고침
# Ctrl+R 또는 F5
```

---

### 📦 **가상 환경 사용 (선택사항, 권장)**

프로젝트별로 독립된 Python 환경을 만들려면:

```bash
# 가상 환경 생성
python -m venv venv

# 활성화
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# 이제 pip install 실행
pip install -r requirements.txt

# 작업 완료 후 비활성화
deactivate
```

## 📂 프로젝트 구조

```
score/
├── api/
│   └── index.py          # Flask 백엔드 API
├── index.html            # 프론트엔드 메인 페이지
├── requirements.txt      # Python 의존성
├── vercel.json           # Vercel 배포 설정
├── .gitignore            # Git 제외 파일
├── env.example           # 환경 변수 템플릿
└── README.md             # 이 파일
```

## 🔐 보안 주의사항

1. ⚠️ **API 키를 절대 GitHub에 업로드하지 마세요!**
   - `.env` 파일은 `.gitignore`에 포함되어 있습니다
   - 실수로 커밋하지 않도록 주의하세요

2. ⚠️ **Vercel 환경 변수 사용**
   - API 키는 Vercel 대시보드의 환경 변수에만 저장
   - 코드에 직접 하드코딩하지 마세요

3. ⚠️ **API 사용량 모니터링**
   - [OpenAI Usage Dashboard](https://platform.openai.com/usage)에서 사용량 확인
   - 예상치 못한 요금이 발생하지 않도록 주의

## 🎯 사용 방법

### HTML 파일 업로드 방식

1. "📁 HTML 파일 업로드" 선택
2. 파일을 드래그 앤 드롭 또는 클릭하여 선택
3. 우측의 채점 항목 선택 (문법/단어/완성도)
4. 자동으로 AI 채점 실행

### URL 입력 방식

1. "🌐 URL 입력" 선택
2. 웹사이트 URL 입력 (예: https://farm.runmoa.ai)
3. "로드" 버튼 클릭
4. 우측의 채점 항목 선택

## 📊 채점 기준

- **문법의 정확성** (30점): 띄어쓰기, 조사, 어미, 맞춤법 검사
- **단어의 정확성** (30점): 오타, 부적절한 단어, 영한 혼용 검사
- **상세페이지 완성도** (40점): HTML 구조, 필수 태그, 시맨틱 태그 검사

## 🐛 문제 해결

### API 키 오류

```
❌ 서버에 API 키가 설정되지 않았습니다
```

**해결 방법**: Vercel 환경 변수에 `OPENAI_API_KEY`가 제대로 설정되었는지 확인

### CORS 오류

```
❌ CORS 정책으로 HTML을 가져올 수 없습니다
```

**해결 방법**: URL 입력 방식 사용 시 일부 사이트는 CORS 정책으로 접근 불가. 이 경우 HTML 파일을 다운로드하여 파일 업로드 방식 사용

### 서버 연결 실패

**로컬 개발 시**:
1. Flask 서버가 실행 중인지 확인 (`python api/index.py`)
2. `http://localhost:5000`으로 접근 가능한지 테스트

**Vercel 배포 후**:
1. Vercel 대시보드에서 배포 로그 확인
2. 환경 변수가 제대로 설정되었는지 확인

## 📝 라이선스

MIT License

## 👨‍💻 개발자

이 프로젝트에 대한 질문이나 제안이 있으시면 이슈를 등록해주세요!

---

**Made with ❤️ and AI**

