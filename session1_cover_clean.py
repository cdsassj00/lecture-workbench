#!/usr/bin/env python3
"""
세션 1 표지+OPENING 종합 정리:
1) slide 0 본문 영역 전체를 깨끗하게 재작성 (사용자 의도 4가지 핵심)
2) 빈 placeholder 슬라이드 11개 (1-5, 8-13) 삭제
3) slide 6, 7 OPENING 거점/비유 표현 점검·정리
"""
import json, urllib.request, urllib.error, re, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CONF = json.load(open('_supabase.local.json', encoding='utf-8'))
URL = CONF['project_url']; SR = CONF['service_role_jwt']
H = {'apikey':SR, 'Authorization':f'Bearer {SR}'}
H_PATCH = {**H, 'Content-Type':'application/json', 'Prefer':'return=minimal'}

def http(method, url, body=None, headers=None):
    h = headers or H
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.read().decode('utf-8')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8')

# ============================================================
# 1) slide 0 본문 영역 — 깨끗한 단일 p 태그
# ============================================================
NEW_BODY_BLOCK = '''<p style="margin-top: 22px; font-size: 14.5px; color: var(--ink2); line-height: 1.85; max-width: 1050px">1차시는 네 가지를 다룹니다. <strong style="color:var(--ink)">첫째 AI 트렌드 오버뷰</strong> — Bard/PaLM → GPT → Agent 진화, NanoGPT로 Q·K·V 체감, 프롬프트→컨텍스트→하네스 진화. <strong style="color:var(--ink)">둘째 공공 미시적 혁신 실무 9가지 유형</strong> — 2차시부터 다룰 부서·기관 단위 AI 적용 패턴 9종 소개. <strong style="color:var(--ink)">셋째 2~8차시 과정 안내</strong> — 회차별 학습 토픽·도구·산출물 전반 살펴봄. <strong style="color:var(--ink)">넷째 환경 세팅</strong> — GitHub·Netlify·Supabase·Vercel 계정 가입 및 Git·Node.js·Python·VS Code·Claude Code·Codex·OpenCode·Antigravity 설치.</p>'''

def fix_slide_0():
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.0&select=html')
    h = json.loads(body)[0]['html']
    new = h
    # 본문 영역의 모든 <p>...<div>...<p></p> 잔재를 통째로 깨끗한 단일 p로 교체
    # h1 <h1>...</h1> 다음의 hl-bar(72x3) 이후부터 우측 metadata 박스 시작 전까지가 본문 영역
    # 패턴: <h1>...</h1><div ... hl-bar ...></div><div ... 부제 ...></div><p ...>...</p><div>...</div>...<p></p>
    # 부제 div는 보존, 그 다음 p 시작부터 첫 metadata `<div style="position:absolute; top:340px; right:80px;` 직전까지 통째 교체
    pattern = re.compile(
        r'(letter-spacing: -0\.01em">[^<]+</div>)'  # 부제 끝
        r'[\s\S]*?'                                  # 본문 영역 통째
        r'(\s*</div>\s*<div style="position:absolute; top:340px;)',  # metadata 시작
    )
    m = pattern.search(new)
    if m:
        new = pattern.sub(rf'\1\n    {NEW_BODY_BLOCK}\2', new)
    # 부제도 한 번 더 안전 치환
    new = new.replace(
        '공공 AI 거점리더의 기술 지형과 환경 세팅',
        'AI 트렌드 · 9가지 공공 혁신 유형 · 과정 안내 · 환경 세팅'
    )
    # 거점 미션 모든 잔재 한번 더 청소
    for old, repl in [('거점 미션 선언서','현업 적용 과제 카드'),
                      ('거점 미션 선언','현업 적용 과제'),
                      ('거점 미션','현업 적용 과제'),
                      ('거점미션 선언','현업 적용 과제'),
                      ('거점미션','현업 적용 과제')]:
        new = new.replace(old, repl)
    if new != h:
        code, body = http('PATCH', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.0',
            {'html': new}, H_PATCH)
        return 200 <= code < 300, len(h) - len(new)
    return False, 0

# ============================================================
# 2) 빈 placeholder 슬라이드 식별 & 삭제
# ============================================================
def is_placeholder(html):
    """본문 텍스트가 모두 placeholder('슬라이드 제목을 입력하세요' 등)인지 검사"""
    text = re.sub(r'<[^>]+>', ' ', html or '')
    text = re.sub(r'\s+', ' ', text).strip()
    # 의미 있는 콘텐츠 존재 여부 — '슬라이드 제목을 입력하세요' / '부제 또는 설명을 입력하세요.' 외에
    # 다른 내용이 있는지 (placeholder는 50자 이내의 standard 문구로만 구성됨)
    placeholder_phrases = [
        '슬라이드 제목을 입력하세요',
        '부제 또는 설명을 입력하세요',
        'SECTION · TOPIC',
        'AI 챔피언 고급 과정',
        'SESSION 01',
        'PART C · 컨텍스트',
        'LECTURE COVER',
        'Session 01',
        'MODULE',
        '01 · AI 에이전트',
        '시대의 개막과',
        '공공 구현 지형도',
        'PAGE',
    ]
    cleaned = text
    for p in placeholder_phrases:
        cleaned = cleaned.replace(p, '')
    cleaned = re.sub(r'[\d\s\/·\-]+', '', cleaned)
    return len(cleaned) < 30  # 30자 이상의 의미 있는 텍스트가 없으면 placeholder

def delete_placeholders():
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=lt.14&select=slide_idx,html&order=slide_idx')
    slides = json.loads(body)
    to_delete = []
    for s in slides:
        if s['slide_idx'] == 0: continue  # 표지 보존
        if s['slide_idx'] in (6, 7): continue  # OPENING 보존
        if is_placeholder(s['html']):
            to_delete.append(s['slide_idx'])
    print(f'  placeholder 후보: {to_delete}')
    deleted = 0
    for idx in to_delete:
        code, body = http('DELETE', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.{idx}', None, H_PATCH)
        if 200 <= code < 300:
            deleted += 1
    return deleted, to_delete

# ============================================================
# 3) slide 6, 7 점검 (OPENING)
# ============================================================
def clean_opening():
    """slide 6 (OPENING · 거점리더)·7 (OPENING · 8회차 커리큘럼) 비유 표현 정리"""
    fixed = 0
    for idx in (6, 7):
        code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.{idx}&select=html')
        rows = json.loads(body)
        if not rows: continue
        h = rows[0]['html']
        new = h
        # 거점미션 잔재 제거 (거점리더는 과정명이라 보존)
        for old, repl in [('거점 미션 선언서','현업 적용 과제 카드'),
                          ('거점 미션 선언','현업 적용 과제'),
                          ('거점 미션','현업 적용 과제'),
                          ('거점미션 선언','현업 적용 과제'),
                          ('거점미션','현업 적용 과제')]:
            new = new.replace(old, repl)
        if new != h:
            code, body = http('PATCH', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.{idx}',
                {'html': new}, H_PATCH)
            if 200 <= code < 300: fixed += 1
    return fixed

# ============================================================
# 메인
# ============================================================
def main():
    print('=== 세션 1 표지·OPENING 종합 정리 ===\n')
    # 백업
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=lt.14&select=slide_idx,html&order=slide_idx')
    bk = json.loads(body)
    bk_path = f'session1_cover_backup_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    with open(bk_path, 'w', encoding='utf-8') as f:
        json.dump(bk, f, ensure_ascii=False)
    print(f'1) 백업: {bk_path}\n')

    print('2) 표지(slide 0) 본문 영역 깔끔히 재작성:')
    ok, diff = fix_slide_0()
    print(f'   {"✓" if ok else "✗"} (글자수 변화 {diff:+d})\n')

    print('3) 빈 placeholder 슬라이드 일괄 삭제:')
    n, lst = delete_placeholders()
    print(f'   삭제됨: {n}개 (slide_idx {lst})\n')

    print('4) OPENING (slide 6, 7) 거점미션 잔재 정리:')
    n = clean_opening()
    print(f'   업데이트: {n}개\n')

    # 최종 상태
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&select=slide_idx&order=slide_idx.desc&limit=3')
    rows = json.loads(body)
    code2, body2 = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&select=slide_idx', None, {'apikey':SR,'Authorization':f'Bearer {SR}','Range-Unit':'items','Prefer':'count=exact'})
    print(f'5) 최종: 세션 1 마지막 3개 idx = {[r["slide_idx"] for r in rows]} / 총 {len(json.loads(body2))}장')

if __name__ == '__main__':
    main()
