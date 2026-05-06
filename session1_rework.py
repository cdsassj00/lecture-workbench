#!/usr/bin/env python3
"""
세션 1 일괄 재구성:
1) 표지(slide_idx 0) — 4가지 핵심 본문으로 갱신
2) PART 라벨 통합 — 현재 A/B/C/D → PART A · AI 트렌드 오버뷰
                    현재 E → PART B · 공공 미시적 혁신 9유형
                    현재 F → PART C · 환경 세팅
                    현재 G → 다음 회차 준비
3) "거점 미션 / 거점미션 / 거점미션 선언" 단어 일괄 제거
   ("거점리더"는 과정명이므로 보존)
"""
import json, urllib.request, urllib.error, re, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CONF = json.load(open('_supabase.local.json', encoding='utf-8'))
URL = CONF['project_url']; SR = CONF['service_role_jwt']
H = {'apikey':SR, 'Authorization':f'Bearer {SR}', 'Content-Type':'application/json'}

# ============================================================
# 1) 표지 본문 새 텍스트
# ============================================================
NEW_COVER_BODY = '''<p style="margin-top: 22px; font-size: 14.5px; color: var(--ink2); line-height: 1.85; max-width: 1050px">1차시는 네 가지를 다룹니다. <strong style="color:var(--ink)">첫째 AI 트렌드 오버뷰</strong> — Bard/PaLM → GPT → Agent 진화, NanoGPT로 Q·K·V 체감, 프롬프트→컨텍스트→<strong style="color:var(--ink)">하네스</strong> 진화. <strong style="color:var(--ink)">둘째 공공 미시적 혁신 실무 9가지 유형</strong> — 2차시부터 다룰 부서·기관 단위 AI 적용 패턴 9종. <strong style="color:var(--ink)">셋째 2~8차시 과정 안내</strong> — 회차별 학습 내용·산출물·연결 흐름. <strong style="color:var(--ink)">넷째 환경 세팅</strong> — GitHub·Netlify·Supabase·Vercel 계정, Git·Node.js·Python·Antigravity·Codex·Claude Code·OpenCode 설치까지.</p>'''

# 사용자 제공 4가지 핵심을 표지에 명시 — 부제도 갱신
NEW_SUBTITLE = 'AI 트렌드 · 9가지 공공 혁신 유형 · 과정 안내 · 환경 세팅'

# 회차 라벨 (구 "거점리더 환경 세팅" → 단순화)
NEW_SESSION_LABEL = 'SESSION 01 · 4H · 환경 세팅'

# ============================================================
# 2) PART 라벨 매핑
# ============================================================
PART_RELABEL = {
    # 현재 라벨 → 새 라벨
    'PART A · NLP 기반기술':        'PART A · AI 트렌드 오버뷰',
    'PART A · AI·NLP 진화사':       'PART A · AI 트렌드 오버뷰',
    'PART B · MicroGPT':           'PART A · NanoGPT — Q·K·V 체감',
    'PART B · Attention':          'PART A · NanoGPT — Q·K·V 체감',
    'PART B · Q·K·V':              'PART A · NanoGPT — Q·K·V 체감',
    'PART B · 멀티헤드':              'PART A · NanoGPT — Q·K·V 체감',
    'PART D · 프론티어 지형':           'PART A · 프론티어 모델 비교',
    'PART D · GPT':                'PART A · 프론티어 모델 비교',
    'PART D · Claude':             'PART A · 프론티어 모델 비교',
    'PART D · Gemini':             'PART A · 프론티어 모델 비교',
    'PART D · Grok':               'PART A · 프론티어 모델 비교',
    'PART D · 오픈소스':              'PART A · 프론티어 모델 비교',
    'PART D · 5종 비교표':            'PART A · 프론티어 모델 비교',
    'PART C · 컨텍스트':              'PART A · 프롬프트→컨텍스트→하네스',
    'PART C · 프롬프트 진화':           'PART A · 프롬프트→컨텍스트→하네스',
    'PART C · 하네스':              'PART A · 프롬프트→컨텍스트→하네스',
    'PART E · 9가지 구현 유형':         'PART B · 공공 미시적 혁신 9유형',
    'PART E · 유형 01':             'PART B · 공공 미시적 혁신 9유형',
    'PART E · 유형 02':             'PART B · 공공 미시적 혁신 9유형',
    'PART E · 유형 03':             'PART B · 공공 미시적 혁신 9유형',
    'PART E · 유형 04':             'PART B · 공공 미시적 혁신 9유형',
    'PART E · 유형 05':             'PART B · 공공 미시적 혁신 9유형',
    'PART E · 유형 06':             'PART B · 공공 미시적 혁신 9유형',
    'PART E · 유형 08':             'PART B · 공공 미시적 혁신 9유형',
    'PART E · 유형 09':             'PART B · 공공 미시적 혁신 9유형',
    'PART E · 9유형 복습':            'PART B · 공공 미시적 혁신 9유형',
    'PART F · 환경 세팅':             'PART C · 환경 세팅',
    'PART F · Git · GitHub':       'PART C · 환경 세팅',
    'PART F · WSL · Node · Python':'PART C · 환경 세팅',
    'PART F · VS Code':            'PART C · 환경 세팅',
    'PART F · Vercel · Netlify':   'PART C · 환경 세팅',
    'PART F · Power BI':           'PART C · 환경 세팅',
    'PART F · 환경 점검':             'PART C · 환경 세팅',
    'PART G · 거점 미션':              '다음 회차 준비',
    'PART G · 좋은 미션':             '다음 회차 준비',
    'PART G · 선언서 워크숍':           '다음 회차 준비',
    'PART G · 공용 아카이브':           '다음 회차 준비',
    'PART G · 아키텍처 캔버스':          '다음 회차 준비',
    'PART G · 외부망↔내부망':           '다음 회차 준비',
    'PART G · 6칸 한눈':             '다음 회차 준비',
    'PART G · 확산 4단계':            '다음 회차 준비',
    'PART G · 2~5회차 예고':          '다음 회차 준비',
    'PART G · 6~8회차 예고':          '다음 회차 준비',
    'PART G · 2회차 전 숙제':          '다음 회차 준비',
    'PART G · 빠른 파악 루틴':           '다음 회차 준비',
    'PART G · 선언서 템플릿':           '다음 회차 준비',
    'PART G · 8회차 진화':            '다음 회차 준비',
}

# ============================================================
# 3) "거점미션" 단어 제거 — 텍스트 일괄 치환
# (거점리더는 과정명이므로 보존)
# ============================================================
TEXT_REPLACE = [
    ('거점 미션 선언서',  '현업 적용 과제 카드'),
    ('거점미션 선언서',   '현업 적용 과제 카드'),
    ('거점 미션 선언',    '현업 적용 과제'),
    ('거점미션 선언',     '현업 적용 과제'),
    ('거점 미션',         '현업 적용 과제'),
    ('거점미션',          '현업 적용 과제'),
]

# ============================================================
# HTTP 헬퍼
# ============================================================
def http(method, url, body=None, headers=None):
    h = headers or H
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.read().decode('utf-8')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8')

def patch_slide(slide_idx, html):
    h_patch = {**H, 'Prefer':'return=minimal'}
    url = f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.{slide_idx}'
    code, body = http('PATCH', url, {'html': html}, h_patch)
    return 200 <= code < 300, code, body

# ============================================================
# 메인
# ============================================================
def main():
    print('=== 세션 1 재구성 ===')
    print(f'시작: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

    # 백업
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&select=slide_idx,html&order=slide_idx', None, {'apikey':SR,'Authorization':f'Bearer {SR}'})
    slides = json.loads(body)
    backup_path = f'session1_backup_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(slides, f, ensure_ascii=False)
    print(f'1) 백업: {backup_path} ({len(slides)} slides)\n')

    # 카운터
    cover_done = False
    label_changed = 0
    text_repl_count = 0
    failed = 0

    for s in slides:
        idx = s['slide_idx']
        orig = s['html'] or ''
        new = orig

        # === 1) 표지 본문 갱신 ===
        if idx == 0:
            # SESSION 01 · 4H · 거점리더 환경 세팅 → 새 라벨
            new = new.replace('SESSION 01 · 4H · 거점리더 환경 세팅', NEW_SESSION_LABEL)
            new = new.replace('공공 AI 거점리더의 기술 지형과 환경 세팅', NEW_SUBTITLE)
            # 본문 p 태그 통째로 교체 — 기존 p 시작 지점부터 다음 div 시작 전까지
            # (사용자 표지 HTML은 p가 깨진 구조 — div 끝부분도 함께 정리)
            cover_pattern = re.compile(
                r'<p style="margin-top: 22px[\s\S]*?</p>',
                re.MULTILINE
            )
            if cover_pattern.search(new):
                new = cover_pattern.sub(NEW_COVER_BODY, new)
                # 그 직후 깨진 div(<div><strong>9가지 공공...</div><p></p>) 잔재 제거
                new = re.sub(r'<div><strong[^>]*>9가지 공공[\s\S]*?</div><p></p>', '', new)
                cover_done = True

        # === 2) PART 라벨 통합 — hbar-l 안의 텍스트 치환 ===
        for old_lbl, new_lbl in PART_RELABEL.items():
            pattern = re.compile(
                r'(<div class="hbar-l"[^>]*>)' + re.escape(old_lbl) + r'(</div>)',
                re.MULTILINE
            )
            if pattern.search(new):
                new = pattern.sub(rf'\1{new_lbl}\2', new)
                label_changed += 1

        # === 3) "거점미션" 단어 일괄 제거 ===
        for old_t, new_t in TEXT_REPLACE:
            if old_t in new:
                cnt = new.count(old_t)
                new = new.replace(old_t, new_t)
                text_repl_count += cnt

        # === PATCH ===
        if new != orig:
            ok, code, body = patch_slide(idx, new)
            if ok:
                print(f'  [{idx:2d}] updated')
            else:
                print(f'  [{idx:2d}] FAIL ({code}): {body[:100]}')
                failed += 1

    print(f'\n=== 결과 ===')
    print(f'  표지 본문 갱신:   {"✓" if cover_done else "✗"}')
    print(f'  PART 라벨 변경:   {label_changed}건')
    print(f'  거점미션 텍스트:  {text_repl_count}건 치환')
    print(f'  실패:           {failed}건')

if __name__ == '__main__':
    main()
