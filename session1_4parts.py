#!/usr/bin/env python3
"""
세션 1 → 4 PART 구조로 재정비:
  PART A · AI 트렌드 (프롬프트→컨텍스트→하네스 흐름 중심)
  PART B · 9가지 공공 혁신 유형
  PART C · 2~8차시 과정 안내
  PART D · 환경 세팅

작업:
1) 표지 본문 — PART A 강조 (프롬프트부터 하네스까지의 흐름)
2) 메타포·캔버스·선언서 슬라이드 일괄 삭제
3) PART 라벨 통합 — 기존 다양한 sub-label들을 4종으로
"""
import json, urllib.request, urllib.error, re, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CONF = json.load(open('_supabase.local.json', encoding='utf-8'))
URL = CONF['project_url']; SR = CONF['service_role_jwt']
H = {'apikey':SR,'Authorization':f'Bearer {SR}'}
H_PATCH = {**H,'Content-Type':'application/json','Prefer':'return=minimal'}

def http(method, url, body=None, headers=None):
    h = headers or H
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.read().decode('utf-8')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8')

# ============================================================
# 1) 표지 본문 — PART A 강조 (프롬프트→하네스 흐름)
# ============================================================
NEW_COVER_BODY = '''<p style="margin-top: 22px; font-size: 14.5px; color: var(--ink2); line-height: 1.85; max-width: 1050px">1차시는 네 가지를 다룹니다. <strong style="color:var(--ink)">PART A · AI 트렌드</strong> — 프롬프트→컨텍스트→<strong style="color:var(--ink)">하네스</strong>로 이어지는 흐름을 중심에 두고, NanoGPT로 Q·K·V 체감과 프론티어 모델 5종(GPT·Claude·Gemini·Grok·OSS)을 함께 살핍니다. <strong style="color:var(--ink)">PART B · 공공 미시적 혁신 9가지 유형</strong> — 2차시부터 다룰 부서·기관 단위 AI 적용 패턴 9종 소개. <strong style="color:var(--ink)">PART C · 2~8차시 과정 안내</strong> — 회차별 학습 토픽·도구·산출물 전반 살펴봄. <strong style="color:var(--ink)">PART D · 환경 세팅</strong> — GitHub·Netlify·Supabase·Vercel 계정 가입 및 Git·Node.js·Python·VS Code·Claude Code·Codex·OpenCode·Antigravity 설치.</p>'''

def fix_cover():
    n_done = 0
    for idx in (0, 1):  # slide 0 + slide 1 (표지 사본)
        code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.{idx}&select=html')
        rows = json.loads(body)
        if not rows: continue
        h = rows[0]['html']
        # 부제: 부제 div 안 텍스트 — letter-spacing: -0.01em" 끝 후
        new = h
        # 본문 p 영역 통째 교체 (margin-top:22px 시작 ~ metadata 시작 직전)
        pattern = re.compile(
            r'(letter-spacing: -0\.01em">[^<]+</div>)'
            r'[\s\S]*?'
            r'(\s*</div>\s*<div style="position:absolute; top:340px;)',
        )
        if pattern.search(new):
            new = pattern.sub(rf'\1\n    {NEW_COVER_BODY}\2', new)
        # 부제 텍스트 갱신
        new = new.replace('공공 AI 거점리더의 기술 지형과 환경 세팅', 'AI 트렌드 · 9가지 혁신 유형 · 과정 안내 · 환경 세팅')
        new = new.replace('AI 트렌드 · 9가지 공공 혁신 유형 · 과정 안내 · 환경 세팅', 'AI 트렌드 · 9가지 혁신 유형 · 과정 안내 · 환경 세팅')
        if new != h:
            code, body = http('PATCH', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.{idx}',
                {'html': new}, H_PATCH)
            if 200 <= code < 300:
                n_done += 1
                print(f'  slide {idx} ✓')
    return n_done

# ============================================================
# 2) 메타포·캔버스·선언서 슬라이드 일괄 삭제
# ============================================================
# 사용자 의도: '캔버스 6칸·선언서 진화·외부망↔내부망·확산 4단계' 등 비유·메타포 표현 제거
# slide_idx 53-60, 63-65 — 현업 적용 과제 카드/워크숍/공용 아카이브/아키텍처 캔버스/외부망/6칸/확산/숙제/빠른 파악/템플릿
# 단 61(2~5회차 예고), 62(6~8회차 예고)는 PART C 콘텐츠로 보존
TO_DELETE = [53, 54, 55, 56, 57, 58, 59, 60, 63, 64, 65]

def delete_metaphor_slides():
    deleted = 0
    for idx in TO_DELETE:
        code, body = http('DELETE', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.{idx}', None, H_PATCH)
        if 200 <= code < 300:
            deleted += 1
    return deleted

# ============================================================
# 3) PART 라벨 통합 — 4가지로
# ============================================================
LABEL_MAP = {
    # PART A (AI 트렌드 — 프롬프트→하네스)
    'PART A · AI 트렌드 오버뷰':        'PART A · AI 트렌드',
    'PART A · NanoGPT — Q·K·V 체감':  'PART A · AI 트렌드',
    'PART A · 프론티어 모델 비교':       'PART A · AI 트렌드',
    'PART A · 프롬프트→컨텍스트→하네스':  'PART A · AI 트렌드',
    # PART B (9가지)
    'PART B · 공공 미시적 혁신 9유형':   'PART B · 9가지 공공 혁신 유형',
    # PART C (2~8차시 과정 안내) — 기존 "다음 회차 준비"·"CLOSING" 라벨 통합
    '다음 회차 준비':                    'PART C · 2~8차시 과정 안내',
    'CLOSING · 8회차 흐름':             'PART C · 2~8차시 과정 안내',
    'CLOSING · 도구 스택':              'PART C · 2~8차시 과정 안내',
    # PART D (환경 세팅)
    'PART C · 환경 세팅':               'PART D · 환경 세팅',
}

def relabel_parts():
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&select=slide_idx,html&order=slide_idx')
    slides = json.loads(body)
    changed = 0
    for s in slides:
        h = s['html'] or ''
        new = h
        for old_lbl, new_lbl in LABEL_MAP.items():
            pattern = re.compile(
                r'(<div class="hbar-l"[^>]*>)' + re.escape(old_lbl) + r'(</div>)'
            )
            if pattern.search(new):
                new = pattern.sub(rf'\1{new_lbl}\2', new)
        if new != h:
            code2, body2 = http('PATCH', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.{s["slide_idx"]}',
                {'html': new}, H_PATCH)
            if 200 <= code2 < 300: changed += 1
    return changed

# ============================================================
# 메인
# ============================================================
def main():
    print('=== 세션 1 → 4 PART 구조 재정비 ===\n')

    # 백업
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&select=slide_idx,html&order=slide_idx')
    bk = json.loads(body)
    bk_path = f'session1_4parts_backup_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    with open(bk_path, 'w', encoding='utf-8') as f:
        json.dump(bk, f, ensure_ascii=False)
    print(f'1) 백업: {bk_path} ({len(bk)} slides)\n')

    print('2) 표지 본문 → PART A 프롬프트→하네스 강조:')
    n = fix_cover()
    print(f'   업데이트: {n}/2장\n')

    print('3) 메타포·선언서·캔버스 슬라이드 일괄 삭제:')
    n = delete_metaphor_slides()
    print(f'   삭제: {n}/{len(TO_DELETE)}개 ({TO_DELETE})\n')

    print('4) PART 라벨 4가지로 통합:')
    n = relabel_parts()
    print(f'   업데이트: {n}장\n')

    # 최종 확인
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&select=slide_idx,html&order=slide_idx')
    slides = json.loads(body)
    print(f'5) 최종: 총 {len(slides)}장')
    # PART 라벨 분포
    label_count = {}
    for s in slides:
        m = re.search(r'<div class="hbar-l"[^>]*>([^<]+)</div>', s['html'])
        if m:
            lbl = m.group(1).strip()
            label_count[lbl] = label_count.get(lbl, 0) + 1
    print('\n   PART 라벨 분포:')
    for lbl, cnt in sorted(label_count.items(), key=lambda x: x[0]):
        print(f'     [{cnt:2d}] {lbl}')

if __name__ == '__main__':
    main()
