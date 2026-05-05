#!/usr/bin/env python3
"""
폰트 일괄 키움: <10pt(<=13.0px) → 11pt(15px)
대상: 본문 섹션 (.bd 안)
제외: .hbar*, .fbar*, .toolbar*, .cblk*, .code, .mtbl* (헤더/푸터/코드/표)
범위: Supabase DB (slides + session_meta) + 정적 session-XX-complete.html
백업: bump_fonts_backup_<timestamp>.json (DB), git tag (정적)
"""
import json, os, re, sys, io, urllib.request, urllib.error, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))
CONF = json.load(open(os.path.join(BASE, '_supabase.local.json'), encoding='utf-8'))
URL = CONF['project_url']; SR = CONF['service_role_jwt']
H = {'apikey': SR, 'Authorization': f'Bearer {SR}', 'Content-Type': 'application/json'}

THRESHOLD_PX = 13.0   # < 10pt
TARGET_PX    = 15     # 11pt
SKIP_RE = re.compile(r'\.(hbar|fbar|toolbar|cblk|code|mtbl)(\b|[-\s,{:.])', re.I)

def http(method, url, headers, body=None):
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.read().decode('utf-8')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8')

def selector_should_skip(selector):
    """selector에 chrome 클래스가 포함되면 skip"""
    return bool(SKIP_RE.search(selector))

def bump_css(css):
    """CSS 텍스트에서 font-size: Xpx (X<=13) 규칙을 15px로. chrome 셀렉터는 skip."""
    if not css: return css, 0
    out = []
    last = 0
    n = 0
    # 'selectors { ... }' 블록 찾기
    for m in re.finditer(r'([^{}]+?)\s*\{([^{}]*)\}', css):
        sel = m.group(1).strip()
        body = m.group(2)
        # selectors 안에 chrome이 하나라도 있으면 그 블록은 통째로 skip
        if any(selector_should_skip(s) for s in sel.split(',')):
            out.append(css[last:m.end()])
        else:
            # body 안 font-size: Xpx (X <= 13) 치환
            def repl(mm):
                px = float(mm.group(1))
                if px <= THRESHOLD_PX:
                    nonlocal n; n += 1
                    return f'font-size:{TARGET_PX}px'
                return mm.group(0)
            new_body = re.sub(r'font-size\s*:\s*([\d.]+)\s*px', repl, body)
            out.append(css[last:m.start()])
            out.append(sel + '{' + new_body + '}')
        last = m.end()
    out.append(css[last:])
    return ''.join(out), n

def bump_inline(html):
    """슬라이드 HTML 내 인라인 style의 font-size: Xpx (X<=13) → 15px.
    단, 같은 요소의 class 속성에 chrome 키워드가 있으면 skip."""
    if not html: return html, 0
    n = 0
    # <tag ... style="...font-size:Xpx..."...> 패턴
    def replace_in_style(match):
        nonlocal n
        full_tag = match.group(0)
        # 같은 태그 안의 class 속성 검사
        cls_m = re.search(r'class="([^"]*)"', full_tag)
        cls_str = cls_m.group(1) if cls_m else ''
        if SKIP_RE.search('.' + cls_str.replace(' ', ' .')):
            return full_tag
        # style 안의 font-size:Xpx 모두 검사
        def fs_repl(fm):
            nonlocal n
            px = float(fm.group(1))
            if px <= THRESHOLD_PX:
                n += 1
                return f'font-size:{TARGET_PX}px'
            return fm.group(0)
        return re.sub(r'font-size\s*:\s*([\d.]+)\s*px', fs_repl, full_tag)
    # 시작 태그만 매칭 (style 속성 가진)
    new_html = re.sub(r'<[a-zA-Z][^>]*\bstyle="[^"]*"[^>]*>', replace_in_style, html)
    return new_html, n

def backup_db(stamp):
    print('1) DB 백업 중...')
    code, body = http('GET', f'{URL}/rest/v1/slides?select=session_num,slide_idx,html', H)
    slides = json.loads(body) if 200 <= code < 300 else []
    code, body = http('GET', f'{URL}/rest/v1/session_meta?select=*', H)
    metas = json.loads(body) if 200 <= code < 300 else []
    bk = {'timestamp': stamp, 'slides': slides, 'session_meta': metas}
    bkpath = os.path.join(BASE, f'bump_fonts_backup_{stamp}.json')
    with open(bkpath, 'w', encoding='utf-8') as f:
        json.dump(bk, f, ensure_ascii=False)
    print(f'   백업 → {os.path.basename(bkpath)} ({len(slides)} slides + {len(metas)} metas)')
    return slides, metas

def update_db(slides, metas):
    print('\n2) DB 패치 (CSS in session_meta + 인라인 in slides)')
    H_PATCH = {**H, 'Prefer': 'return=minimal'}
    # session_meta CSS
    css_total = 0; css_changed = 0
    for m in metas:
        new_css, n = bump_css(m.get('css') or '')
        if n > 0:
            url = f'{URL}/rest/v1/session_meta?session_num=eq.{m["session_num"]}'
            code, body = http('PATCH', url, H_PATCH, {'css': new_css})
            if 200 <= code < 300:
                css_total += n; css_changed += 1
                print(f'   [meta s{m["session_num"]}] {n}건 폰트 키움')
            else:
                print(f'   [FAIL s{m["session_num"]}] {code}: {body[:100]}')
    print(f'   → meta {css_changed}/{len(metas)}개, 총 {css_total}건')
    # slides 인라인
    inline_total = 0; inline_changed = 0
    for s in slides:
        new_html, n = bump_inline(s.get('html') or '')
        if n > 0:
            url = f'{URL}/rest/v1/slides?session_num=eq.{s["session_num"]}&slide_idx=eq.{s["slide_idx"]}'
            code, body = http('PATCH', url, H_PATCH, {'html': new_html})
            if 200 <= code < 300:
                inline_total += n; inline_changed += 1
            else:
                print(f'   [FAIL s{s["session_num"]}-{s["slide_idx"]}] {code}: {body[:100]}')
    print(f'   → slides {inline_changed}/{len(slides)}장, 총 {inline_total}건')
    return css_total + inline_total

def update_static_files():
    print('\n3) 정적 session-XX-complete.html 패치')
    total = 0; changed_files = 0
    for n in range(1, 9):
        fpath = os.path.join(BASE, f'session-{n:02d}-complete.html')
        if not os.path.exists(fpath): continue
        with open(fpath, encoding='utf-8') as f: orig = f.read()
        # CSS와 인라인 둘 다 적용 (단순화: 전체에 inline 패턴 + CSS 블록 모두 처리)
        new_html, n_css = bump_css(orig)
        new_html, n_inline = bump_inline(new_html)
        cnt = n_css + n_inline
        if cnt > 0:
            with open(fpath, 'w', encoding='utf-8') as f: f.write(new_html)
            print(f'   session-{n:02d}: CSS {n_css}건 + 인라인 {n_inline}건 = {cnt}건')
            total += cnt; changed_files += 1
    print(f'   → 정적 {changed_files}/8개 파일, 총 {total}건')
    return total

if __name__ == '__main__':
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    print(f'=== 폰트 일괄 키움: ≤13px → 15px (본문만) ===')
    print(f'타임스탬프: {stamp}')
    print(f'제외: .hbar*, .fbar*, .toolbar*, .cblk*, .code, .mtbl*\n')
    slides, metas = backup_db(stamp)
    db_n = update_db(slides, metas)
    file_n = update_static_files()
    print(f'\n=== 완료 ===')
    print(f'  DB 변경: {db_n}건')
    print(f'  정적 파일: {file_n}건')
    print(f'  백업: bump_fonts_backup_{stamp}.json (롤백 시 같은 PATCH로 복원)')
