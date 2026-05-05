#!/usr/bin/env python3
"""
과정 명칭 일괄 변경 스크립트
- 정식: AI 챔피언 고급 과정
- 부제: AI 데이터분석 전문인재 과정
- 표기: AI 챔피언 고급 과정 (AI 데이터분석 전문인재 과정)
- 공간 제약 시: AI 챔피언 고급 과정 (단축형)

대상:
1) 정적 파일 (index.html, curriculum.html, session-XX, Edge Function)
2) Supabase DB (slides 테이블 278행, session_meta 테이블)
"""
import json, os, sys, io, urllib.request, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))
CONF = json.load(open(os.path.join(BASE, '_supabase.local.json'), encoding='utf-8'))
URL = CONF['project_url']
SR  = CONF['service_role_jwt']

# 치환 규칙 — 가장 긴 패턴부터 (그래야 부분 매칭이 짧은 규칙으로 잘리지 않음)
LONG  = 'AI 챔피언 고급 과정 (AI 데이터분석 전문인재 과정)'
SHORT = 'AI 챔피언 고급 과정'  # hbar-r 같은 좁은 영역용

RULES = [
    # 가장 긴 풀 명칭
    ('2026 행정안전부 AI·데이터기반행정 전문인재 양성과정', LONG),
    ('행정안전부 AI·데이터기반행정 전문인재 양성과정',      LONG),
    ('8주 행정안전부 AI·데이터기반행정 전문인재 양성과정',  LONG),
    ('2026 AI·데이터기반행정 전문인재 양성과정',            LONG),
    # 커리큘럼 표지의 두 줄 분리 표기
    ('AI · 데이터기반행정<br>전문인재 양성과정', 'AI 챔피언 고급 과정<br>AI 데이터분석 전문인재 과정'),
    ('AI·데이터기반행정<br>전문인재 양성과정',   'AI 챔피언 고급 과정<br>AI 데이터분석 전문인재 과정'),
    # hbar-r에 광범위 사용 — 짧게
    ('AI·데이터기반행정 전문인재 양성과정', SHORT),
    ('공공 AI 전문인재 양성과정',           SHORT),
    # 변형
    ('AI·데이터기반행정 전문인재',  SHORT),
    ('AI데이터기반행정 전문인재 양성과정', SHORT),
    ('행정안전부·NIA · 2026 전문인재 양성과정', LONG),
    # 파일명용 변형
    ('AI데이터기반행정 전문인재 양성과정_', 'AI챔피언고급과정_'),
    # 마지막 안전망
    ('전문인재 양성과정', SHORT),
]

def apply_rules(text):
    if not text:
        return text
    for old, new in RULES:
        text = text.replace(old, new)
    return text

def update_files():
    targets = [
        'index.html', 'curriculum.html',
        'session-01-complete.html', 'session-02-complete.html',
        'session-03-complete.html', 'session-04-complete.html',
        'session-05-complete.html', 'session-06-complete.html',
        'session-07-complete.html', 'session-08-complete.html',
        'supabase/functions/rewrite-text/index.ts',
    ]
    changed = []
    for f in targets:
        p = os.path.join(BASE, f.replace('/', os.sep))
        if not os.path.exists(p):
            print(f'  [skip] not found: {f}')
            continue
        with open(p, encoding='utf-8') as fp:
            orig = fp.read()
        updated = apply_rules(orig)
        if updated != orig:
            with open(p, 'w', encoding='utf-8') as fp:
                fp.write(updated)
            n = sum(orig.count(o) for o, _ in RULES if o in orig)
            print(f'  [file] {f}: {n} replacements')
            changed.append(f)
        else:
            print(f'  [file] {f}: no change')
    return changed

def http_req(method, url, headers, body=None):
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')

def update_db():
    H = {'apikey': SR, 'Authorization': f'Bearer {SR}', 'Content-Type': 'application/json'}
    # 1. slides 모두 가져오기
    code, body = http_req('GET', f'{URL}/rest/v1/slides?select=session_num,slide_idx,html', H)
    if code >= 300:
        print(f'  [db] slides fetch FAIL ({code}): {body[:200]}')
        return
    slides = json.loads(body)
    print(f'  [db] fetched {len(slides)} slides')
    H_PATCH = {**H, 'Prefer': 'return=minimal'}
    updated, skipped, failed = 0, 0, 0
    for s in slides:
        new_html = apply_rules(s['html'])
        if new_html == s['html']:
            skipped += 1
            continue
        url = f'{URL}/rest/v1/slides?session_num=eq.{s["session_num"]}&slide_idx=eq.{s["slide_idx"]}'
        code, body = http_req('PATCH', url, H_PATCH, {'html': new_html})
        if 200 <= code < 300:
            updated += 1
        else:
            failed += 1
            if failed <= 3:
                print(f'    [fail] s{s["session_num"]}-{s["slide_idx"]} ({code}): {body[:150]}')
    print(f'  [db] slides → updated={updated}, unchanged={skipped}, failed={failed}')
    # 2. session_meta
    code, body = http_req('GET', f'{URL}/rest/v1/session_meta?select=session_num,title,css', H)
    if code < 300:
        metas = json.loads(body)
        m_updated = 0
        for m in metas:
            new_title = apply_rules(m.get('title') or '')
            new_css = apply_rules(m.get('css') or '')
            if new_title == (m.get('title') or '') and new_css == (m.get('css') or ''):
                continue
            url = f'{URL}/rest/v1/session_meta?session_num=eq.{m["session_num"]}'
            code2, body2 = http_req('PATCH', url, H_PATCH, {'title': new_title, 'css': new_css})
            if 200 <= code2 < 300:
                m_updated += 1
        print(f'  [db] session_meta → updated={m_updated}')

if __name__ == '__main__':
    print('=== STATIC FILES ===')
    update_files()
    print('\n=== SUPABASE DB ===')
    update_db()
    print('\nDONE.')
