"""
HTML 채점 시스템 - Flask 백엔드 API
OpenAI API 키를 안전하게 서버에서 관리하고 프론트엔드 요청을 프록시합니다.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import re
import json
from html import unescape
from dotenv import load_dotenv

# .env 파일 로드 (로컬 개발 환경용)
load_dotenv()

app = Flask(__name__)

# JSON 응답에서 한글이 제대로 표시되도록 설정
app.config['JSON_AS_ASCII'] = False

# CORS 설정 (프론트엔드에서 API 호출 가능하도록)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 환경 변수에서 OpenAI API 키 가져오기
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

if not OPENAI_API_KEY:
    print("⚠️ 경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다!")


def calculate_score(error_count, max_score):
    """
    오류 개수를 기반으로 점수를 일관되게 계산
    
    채점 기준 (더 관대하게):
    - 0개 오류: 만점
    - 1개 오류: -1점만 감점
    - 2개 오류: -2점 감점
    - 3-4개 오류: -3 감점
    - 5-7개 오류: -4 감점
    - 8-10개 오류: -5 감점
    - 11개 이상: -7 감점 (최소 50% 보장)
    """
    if error_count == 0:
        return max_score  # 만점
    elif error_count == 1:
        return max_score - 1  # 오류 1개: -1점만 (30점 → 29점, 40점 → 39점)
    elif error_count == 2:
        return max_score - 2  # 오류 2개: -2점 (30점 → 28점, 40점 → 38점)
    elif error_count <= 4:
        return max_score - 3  # 오류 2개: -3점 (30점 → 27점, 40점 → 37점)
    elif error_count <= 7:
        return max_score - 4  # 오류 2개: -4점 (30점 → 26점, 40점 → 36점)
    elif error_count <= 10:
        return max_score - 5  # 오류 2개: -5점 (30점 → 25점, 40점 → 35점)
    else:
        return max_score - 7  # 오류 2개: -7점 (30점 → 23점, 40점 → 33점)


@app.route('/')
def home():
    """루트 경로 - API 상태 확인"""
    return jsonify({
        'status': 'ok',
        'message': 'HTML 채점 시스템 API 서버',
        'api_key_configured': bool(OPENAI_API_KEY)
    })


@app.route('/api/verify-key', methods=['POST'])
def verify_key():
    """
    API 키 유효성 검증
    (더 이상 클라이언트가 직접 키를 입력하지 않으므로 서버 키 검증용)
    """
    if not OPENAI_API_KEY:
        return jsonify({
            'valid': False,
            'error': 'API 키가 서버에 설정되지 않았습니다.'
        }), 500
    
    try:
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
            timeout=10
        )
        
        return jsonify({
            'valid': response.status_code == 200,
            'status_code': response.status_code
        })
    except requests.RequestException as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500


def basic_word_check(text):
    """
    AI 호출 전 기본 맞춤법 체크 (확실한 오류만, 매우 빠름!)
    자주 틀리는 단어 패턴을 빠르게 체크하여 AI 호출을 최소화합니다.
    """
    errors = []
    
    # 확실한 맞춤법 오류 패턴 (빠른 체크, AI 호출 불필요)
    # 형식: (잘못된_표현, 올바른_표현, 오류_메시지)
    patterns = [
        # 모음 오류
        ('메운맛', '매운맛', '"메운맛" → "매운맛" (모음 오류)'),
        ('오새요', '오세요', '"오새요" → "오세요" (모음 오류)'),
        ('계새요', '계세요', '"계새요" → "계세요" (모음 오류)'),
        ('되요', '돼요', '"되요" → "돼요" (맞춤법 오류)'),
        
        # 자음 오류
        ('어떻해', '어떻게', '"어떻해" → "어떻게" (자음 오류)'),
        ('다체로운', '다채로운', '"다체로운" → "다채로운" (자음 누락)'),
        ('다체롭게', '다채롭게', '"다체롭게" → "다채롭게" (자음 누락)'),
        
        # 띄어쓰기
        ('궁금한점이', '궁금한 점이', '"궁금한점이" → "궁금한 점이" (띄어쓰기)'),
        ('할수있다', '할 수 있다', '"할수있다" → "할 수 있다" (띄어쓰기)'),
        ('할수있습니다', '할 수 있습니다', '"할수있습니다" → "할 수 있습니다" (띄어쓰기)'),
        
        # 기타 오타
        ('잇습니다', '있습니다', '"잇습니다" → "있습니다" (오타)'),
        ('읍니다', '습니다', '"읍니다" → "습니다" (맞춤법 오류)'),
    ]
    
    for wrong, _correct, error_msg in patterns:  # _correct로 명시적으로 미사용 표시
        if wrong in text:
            errors.append(error_msg)
    
    return errors


@app.route('/api/check-grammar', methods=['POST'])
def check_grammar():
    """
    문법 체크 API
    1. 먼저 기본 패턴 체크
    2. 그 다음 OpenAI API로 추가 검사
    """
    if not OPENAI_API_KEY:
        return jsonify({
            'error': 'API 키가 설정되지 않았습니다.'
        }), 500
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        category = data.get('category', 'grammar')
        
        if not text:
            return jsonify({'error': '텍스트가 비어있습니다.'}), 400
        
        # 카테고리별 배점 설정
        max_scores = {
            'grammar': 30,
            'word': 30,  # 프론트엔드와 통일 (words → word)
            'completeness': 40
        }
        max_score = max_scores.get(category, 30)
        
        # ✨ 단어 채점: 기본 패턴 체크 먼저 실행
        basic_errors = []
        if category == 'word':
            # HTML에서 텍스트 추출 (단어 채점용)
            from html import unescape
            import re
            clean_text = re.sub('<!--.*?-->', ' ', text, flags=re.DOTALL)  # HTML 주석 제거
            clean_text = re.sub('<[^>]+>', ' ', clean_text)  # HTML 태그 제거
            clean_text = unescape(clean_text)  # HTML 엔티티 디코드
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # 공백 정리
            
            basic_errors = basic_word_check(clean_text)
            
            # 기본 체크에서 오류 발견 시 즉시 반환 (AI 호출 불필요, 빠르고 정확!)
            if basic_errors:
                error_count = len(basic_errors)
                score = calculate_score(error_count, max_score)
                return jsonify({
                    'success': True,
                    'score': score,
                    'errorCount': error_count,
                    'errors': basic_errors,
                    'detail': f'[기본 체크]\n' + '\n'.join(basic_errors)
                })
        
        # 카테고리별 프롬프트 설정 (점수는 제외하고 오류만 찾게 함)
        prompts = {
            'grammar': f"""문법 구조 오류만 찾으세요.

중요: 실제로 존재하는 오류만! 없으면 {{"errorCount": 0, "errors": []}}

찾을 것: "을를"처럼 조사 중복, "했어요었어요"처럼 어미 중복
무시: 단어 반복

텍스트: {text}

JSON: {{"errorCount": 숫자, "errors": ["설명"]}}

주의: 텍스트에 없는 오류를 만들지 마세요!""",
            
            'word': f"""맞춤법과 띄어쓰기 오류만 찾으세요.

중요: 실제로 존재하는 오류만! 없으면 {{"errorCount": 0, "errors": []}}

올바른 표현 (오류 아님!):
- "매운맛" ✓ (정확함)
- "고추나라" ✓ (정확함)
- "오세요" ✓ (정확함)

찾을 오류:
- "메운맛" → "매운맛" (잘못된 표현)
- "오새요" → "오세요" (잘못된 표현)
- "되요" → "돼요" (잘못된 표현)

무시: 단어 반복

텍스트: {text}

JSON: {{"errorCount": 숫자, "errors": ["설명"]}}

⚠️ "매운맛"은 올바른 표현입니다. 오류로 판단하지 마세요!""",
            
            'completeness': f"""HTML 기본 구조 확인.

확인: <html>, <head>, <body>, <title> 존재? 태그 닫힘?
무시: DOCTYPE, alt, 시맨틱태그

HTML: {text}

JSON: {{"errorCount": 숫자, "errors": ["설명"]}}"""
        }
        
        prompt = prompts.get(category, prompts['grammar'])
        
        # OpenAI API 호출
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': '당신은 정확한 한국어 검사 AI입니다. 실제로 존재하는 오류만 보고하세요. 없으면 오류 0개로 응답하세요.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0,  # 환각 방지 (결정론적)
                'max_tokens': 500
            },
            timeout=15
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': f'OpenAI API 오류: {response.status_code}',
                'details': response.text
            }), 500
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # JSON 파싱 시도
        import json
        try:
            # 마크다운 코드 블록 제거
            if '```json' in ai_response:
                ai_response = ai_response.split('```json')[1].split('```')[0].strip()
            elif '```' in ai_response:
                ai_response = ai_response.split('```')[1].split('```')[0].strip()
            
            parsed_result = json.loads(ai_response)
            error_count = parsed_result.get('errorCount', 0)
            errors = parsed_result.get('errors', [])
            
            # 서버에서 명확한 점수 계산 (오류 개수 기반)
            score = calculate_score(error_count, max_score)
            
            return jsonify({
                'success': True,
                'score': score,
                'errorCount': error_count,
                'errors': errors,
                'detail': '\n'.join(errors) if errors else '오류 없음'
            })
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 텍스트 그대로 반환
            # 파싱 실패는 1개 오류로 간주하고 점수 계산
            fallback_score = calculate_score(1, max_score)
            return jsonify({
                'success': True,
                'score': fallback_score,
                'errorCount': 1,
                'errors': [ai_response],
                'detail': ai_response
            })
    
    except requests.RequestException as e:
        return jsonify({
            'error': f'API 요청 실패: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'서버 오류: {str(e)}'
        }), 500


# Vercel은 app을 직접 실행하지 않고 WSGI로 처리
# 로컬 테스트용
if __name__ == '__main__':
    app.run(debug=True, port=5000)

