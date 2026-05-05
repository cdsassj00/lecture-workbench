#!/usr/bin/env python3
"""
Markdown → Editorial HTML 변환기
- 입력: 마크다운 (#, ##, ###, 표, 코드블록, 인용, 리스트)
- 출력: lecture_transcript_editorial.html 스타일의 단독 HTML
  · EB Garamond + Noto Serif KR
  · 좌측 사이드바 (H2 그룹 + H3 항목)
  · 다크모드 토글
  · 키보드 단축키 (s, d)
  · 능동 섹션 하이라이트 (IntersectionObserver)
"""
import re, os, sys, io, html as html_lib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))

# 변환 작업 목록 (소스 → 출력 + 메타)
JOBS = [
    {
        'src': r'C:\Users\value\Downloads\takeout-20260409T073847Z-3-001\Takeout\Chrome\claude-code-완전가이드.md',
        'out': 'references/06-claude-code-guide.html',
        'title': 'Claude Code 완전 가이드',
        'subtitle': 'Full Guide · 슬래시 명령 · 설정 · 확장',
    },
    {
        'src': r'C:\Users\value\Downloads\takeout-20260409T073847Z-3-001\Takeout\Chrome\codex_슬래시명령_설정_일반사용자_완전가이드.md',
        'out': 'references/06-codex-guide.html',
        'title': 'Codex 완전 가이드',
        'subtitle': 'CLI Slash Commands · Config · MCP',
    },
    {
        'src': r'C:\Users\value\Downloads\takeout-20260409T073847Z-3-001\Takeout\Chrome\오픈코드-클로드코드-슬래시명령_툴_설정-올인원-가이드.md',
        'out': 'references/06-opencode-claudecode-allinone.html',
        'title': 'OpenCode · Claude Code 올인원',
        'subtitle': '슬래시 명령 · 툴 · 설정 비교 가이드',
    },
    {
        'src': r'C:\Users\value\Downloads\takeout-20260409T073847Z-3-001\Takeout\Chrome\opencode-슬래시명령-툴-설정-완전가이드.md',
        'out': 'references/06-opencode-guide.html',
        'title': 'OpenCode 완전 가이드',
        'subtitle': 'Tool 인터페이스 · Skill · Plugin 인벤토리',
    },
]

# ---------- 마크다운 파싱 ----------

def slugify(text):
    s = re.sub(r'[^\w가-힣\- ]', '', text).strip().lower()
    s = re.sub(r'\s+', '-', s)
    return s[:60] or 'sec'

def inline_md(text):
    """인라인 마크다운: **bold**, *em*, `code`, [link](url), <br>"""
    # escape HTML first
    text = html_lib.escape(text, quote=False)
    # code spans
    text = re.sub(r'`([^`]+)`', lambda m: f'<code>{m.group(1)}</code>', text)
    # bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # italic (but not inside ** which we already replaced)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    # links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', text)
    return text

def parse_md(md):
    """
    md 문자열 → (sections, body_html)
    sections = [(level, text, anchor_id)] for sidebar
    body_html = 본문 HTML
    """
    lines = md.split('\n')
    out = []
    sections = []
    i = 0
    used_ids = set()
    def get_id(text):
        base = slugify(text)
        cand = base
        n = 2
        while cand in used_ids:
            cand = f'{base}-{n}'; n += 1
        used_ids.add(cand)
        return cand

    while i < len(lines):
        ln = lines[i]
        # H1
        m = re.match(r'^# (.+)$', ln)
        if m:
            txt = m.group(1).strip()
            aid = get_id(txt)
            sections.append((1, txt, aid))
            out.append(f'<h1 id="{aid}">{inline_md(txt)}</h1>')
            i += 1; continue
        # H2
        m = re.match(r'^## (.+)$', ln)
        if m:
            txt = m.group(1).strip()
            aid = get_id(txt)
            sections.append((2, txt, aid))
            out.append(f'<h2 id="{aid}">{inline_md(txt)}</h2>')
            i += 1; continue
        # H3
        m = re.match(r'^### (.+)$', ln)
        if m:
            txt = m.group(1).strip()
            aid = get_id(txt)
            sections.append((3, txt, aid))
            out.append(f'<h3 id="{aid}">{inline_md(txt)}</h3>')
            i += 1; continue
        # H4 (treat as smaller h3)
        m = re.match(r'^#### (.+)$', ln)
        if m:
            txt = m.group(1).strip()
            out.append(f'<h4>{inline_md(txt)}</h4>')
            i += 1; continue
        # HR
        if re.match(r'^---+\s*$', ln) or re.match(r'^\*\*\*\s*$', ln):
            out.append('<hr>')
            i += 1; continue
        # Code block (fenced)
        m = re.match(r'^```(\w*)\s*$', ln)
        if m:
            lang = m.group(1) or ''
            buf = []
            i += 1
            while i < len(lines) and not re.match(r'^```\s*$', lines[i]):
                buf.append(lines[i]); i += 1
            i += 1  # skip closing
            code_html = html_lib.escape('\n'.join(buf), quote=False)
            out.append(f'<pre class="code"><code class="lang-{lang}">{code_html}</code></pre>')
            continue
        # Blockquote
        if ln.startswith('> '):
            buf = []
            while i < len(lines) and lines[i].startswith('> '):
                buf.append(lines[i][2:]); i += 1
            out.append(f'<div class="quote">{inline_md(" ".join(buf))}</div>')
            continue
        # Table (heuristic: line starts with `|` and next line is `|---`)
        if ln.lstrip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[-:\|\s]+\|\s*$', lines[i+1]):
            header_cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            i += 2  # skip header + separator
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                rows.append(cells); i += 1
            tbl = '<div class="tblwrap"><table><thead><tr>'
            tbl += ''.join(f'<th>{inline_md(c)}</th>' for c in header_cells)
            tbl += '</tr></thead><tbody>'
            for r in rows:
                tbl += '<tr>' + ''.join(f'<td>{inline_md(c)}</td>' for c in r) + '</tr>'
            tbl += '</tbody></table></div>'
            out.append(tbl)
            continue
        # Unordered list
        if re.match(r'^\s*[-*]\s+', ln):
            buf = []
            while i < len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                m2 = re.match(r'^\s*[-*]\s+(.*)$', lines[i])
                buf.append(m2.group(1)); i += 1
            ul = '<ul>' + ''.join(f'<li>{inline_md(b)}</li>' for b in buf) + '</ul>'
            out.append(ul)
            continue
        # Ordered list
        if re.match(r'^\s*\d+\.\s+', ln):
            buf = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                m2 = re.match(r'^\s*\d+\.\s+(.*)$', lines[i])
                buf.append(m2.group(1)); i += 1
            ol = '<ol>' + ''.join(f'<li>{inline_md(b)}</li>' for b in buf) + '</ol>'
            out.append(ol)
            continue
        # 빈 줄
        if not ln.strip():
            i += 1; continue
        # 일반 문단 — 다음 빈 줄까지 합침
        buf = [ln]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6} |```|---+|>\s|\s*[-*]\s|\s*\d+\.\s|\|)', lines[i]):
            buf.append(lines[i]); i += 1
        out.append(f'<p>{inline_md(" ".join(buf))}</p>')

    return sections, '\n'.join(out)

# ---------- 사이드바 빌드 ----------

def build_sidebar(sections, brand, sub):
    """sections에서 H2/H3 추출해 그룹별 사이드바 생성"""
    parts = [f'<div class="brand">{html_lib.escape(brand)}</div>',
             f'<div class="sub">{html_lib.escape(sub)}</div>']
    cur_group_open = False
    cur_ul_open = False
    for lvl, txt, aid in sections:
        if lvl == 1:
            continue  # H1은 사이드바에 안 넣음
        if lvl == 2:
            if cur_ul_open:
                parts.append('</ul>'); cur_ul_open = False
            # H2 → grp 라벨로
            parts.append(f'<div class="grp">{html_lib.escape(txt[:30])}</div>')
            parts.append('<ul>')
            parts.append(f'<li><a href="#{aid}">{html_lib.escape(txt)}</a></li>')
            cur_ul_open = True
        elif lvl == 3:
            if not cur_ul_open:
                parts.append('<ul>'); cur_ul_open = True
            parts.append(f'<li><a href="#{aid}">{html_lib.escape(txt)}</a></li>')
    if cur_ul_open:
        parts.append('</ul>')
    return '\n'.join(parts)

# ---------- 풀 페이지 빌드 ----------

TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,500;0,700;1,500&family=Noto+Serif+KR:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f5efe4;--ink:#2b2015;--ink-soft:#4a3826;--accent:#b8532a;--line:#d8c8ae;--line-soft:#e6d9bf;--code-bg:#ebe1cc;--sb-w:260px}}
[data-theme="dark"]{{--bg:#1a1612;--ink:#ede4d3;--ink-soft:#c9bba0;--accent:#e07a4a;--line:#3a2f22;--line-soft:#2d2419;--code-bg:#2d2419}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;background:var(--bg);color:var(--ink)}}
body{{font-family:'EB Garamond','Noto Serif KR','Batang',serif;font-size:18px;line-height:1.85;-webkit-font-smoothing:antialiased;word-break:keep-all}}

.ctrl{{position:fixed;top:16px;z-index:20;display:flex;gap:8px}}
.ctrl button{{background:var(--bg);border:1px solid var(--line);color:var(--ink);width:36px;height:36px;border-radius:6px;cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center;transition:background .15s}}
.ctrl button:hover{{background:rgba(184,83,42,.1);color:var(--accent)}}
.ctrl.left{{left:16px}} .ctrl.right{{right:16px}}

.sidebar{{position:fixed;top:0;left:0;width:var(--sb-w);height:100vh;background:var(--bg);border-right:1px solid var(--line-soft);padding:72px 22px 40px 26px;overflow-y:auto;transition:transform .3s ease;z-index:15}}
body.sb-closed .sidebar{{transform:translateX(-100%)}}
.sidebar .brand{{font-family:'EB Garamond','Noto Serif KR',serif;font-weight:700;font-size:14px;color:var(--accent);letter-spacing:.15em;text-transform:uppercase;margin-bottom:6px}}
.sidebar .sub{{font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-soft);opacity:.7;margin-bottom:24px;padding-bottom:18px;border-bottom:1px solid var(--line-soft)}}
.sidebar .grp{{font-size:10px;letter-spacing:.2em;font-weight:700;color:var(--accent);text-transform:uppercase;margin:18px 0 6px;opacity:.85}}
.sidebar .grp:first-of-type{{margin-top:0}}
.sidebar ul{{list-style:none;padding:0;margin:0 0 4px}}
.sidebar ul li{{font-family:'Noto Serif KR',serif;font-size:12px;line-height:1.45;padding:4px 0 4px 10px;border-left:2px solid transparent;color:var(--ink-soft);transition:all .15s}}
.sidebar ul li a{{display:block;color:inherit;text-decoration:none}}
.sidebar ul li:hover{{color:var(--accent);border-left-color:var(--line)}}
.sidebar ul li.active{{color:var(--accent);border-left-color:var(--accent);font-weight:700}}

.page{{padding-left:var(--sb-w);transition:padding-left .3s ease}}
body.sb-closed .page{{padding-left:0}}
article{{max-width:880px;margin:0 auto;padding:80px 36px 120px}}

h1{{font-family:'EB Garamond','Noto Serif KR',serif;font-size:38px;font-weight:700;line-height:1.2;margin:0 0 56px;text-align:center;letter-spacing:-.4px;scroll-margin-top:32px}}
h1 em{{font-style:italic;color:var(--accent)}}
h2{{font-family:'EB Garamond','Noto Serif KR',serif;font-size:25px;font-weight:700;line-height:1.3;margin:54px 0 16px;letter-spacing:-.2px;color:var(--ink);scroll-margin-top:32px;border-bottom:1px solid var(--line-soft);padding-bottom:8px}}
h3{{font-family:'EB Garamond','Noto Serif KR',serif;font-size:20px;font-weight:700;margin:34px 0 12px;color:var(--ink);letter-spacing:-.1px;scroll-margin-top:32px}}
h4{{font-family:'Noto Serif KR',serif;font-size:16px;font-weight:700;margin:24px 0 10px;color:var(--ink-soft)}}

p{{margin:0 0 18px;color:var(--ink-soft)}}
p strong{{color:var(--ink);font-weight:700}}
p em{{color:var(--accent);font-style:italic}}
a{{color:var(--accent);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:2px}}
a:hover{{text-decoration-thickness:2px}}

ul, ol{{padding-left:24px;margin:0 0 18px;color:var(--ink-soft)}}
li{{margin-bottom:6px;line-height:1.7}}
li strong{{color:var(--ink)}}

code{{font-family:'JetBrains Mono','Consolas',monospace;font-size:.88em;background:var(--code-bg);color:var(--ink);padding:1.5px 5px;border-radius:3px}}
pre.code{{background:var(--code-bg);padding:14px 18px;border-radius:5px;overflow-x:auto;margin:18px 0;border-left:3px solid var(--accent);font-size:13px;line-height:1.5}}
pre.code code{{background:none;padding:0;font-size:.93em;color:var(--ink)}}

.quote{{margin:24px 0;padding:14px 0 14px 22px;border-left:3px solid var(--accent);font-style:italic;font-size:18px;color:var(--ink);line-height:1.65;font-weight:500}}

.tblwrap{{margin:18px 0;overflow-x:auto;border:1px solid var(--line-soft);border-radius:4px}}
table{{border-collapse:collapse;width:100%;font-family:'Noto Serif KR',serif;font-size:13.5px}}
thead th{{background:var(--code-bg);color:var(--ink);font-weight:700;text-align:left;padding:8px 12px;border-bottom:1.5px solid var(--accent);font-size:12px;letter-spacing:.5px}}
tbody td{{padding:8px 12px;border-bottom:1px solid var(--line-soft);color:var(--ink-soft);vertical-align:top}}
tbody tr:last-child td{{border-bottom:none}}
tbody tr:hover{{background:rgba(184,83,42,.04)}}
table code{{font-size:.85em}}

hr{{border:none;text-align:center;margin:48px 0;color:var(--accent);letter-spacing:.7em;font-size:14px}}
hr::after{{content:"✦ ❦ ✦"}}

@media(max-width:900px){{
  .page{{padding-left:0}}
  .sidebar{{transform:translateX(-100%)}}
  body.sb-open .sidebar{{transform:translateX(0);box-shadow:6px 0 24px rgba(0,0,0,.15)}}
}}
@media(max-width:720px){{
  body{{font-size:16px}}
  article{{padding:56px 18px 80px}}
  h1{{font-size:28px;margin-bottom:36px}}
  h2{{font-size:21px;margin:42px 0 12px}}
  h3{{font-size:18px}}
  table{{font-size:12.5px}}
}}
</style>
</head>
<body>

<div class="ctrl left"><button id="sbToggle" title="사이드바 토글 (s)" aria-label="Toggle sidebar">☰</button></div>
<div class="ctrl right"><button id="themeToggle" title="다크모드 (d)" aria-label="Toggle theme">◐</button></div>

<nav class="sidebar" aria-label="목차">
{sidebar}
</nav>

<div class="page">
<article>
{body}
</article>
</div>

<script>
(function(){{
  const body = document.body;
  const KEY = 'editorial_sb_state_{slug}';
  const isWide = () => window.matchMedia('(min-width:901px)').matches;
  const saved = localStorage.getItem(KEY);
  if (isWide()) {{ if (saved === 'closed') body.classList.add('sb-closed'); }}
  else {{ if (saved === 'open') body.classList.add('sb-open'); }}
  document.getElementById('sbToggle').addEventListener('click', () => {{
    if (isWide()) {{ body.classList.toggle('sb-closed'); localStorage.setItem(KEY, body.classList.contains('sb-closed') ? 'closed' : 'open'); }}
    else {{ body.classList.toggle('sb-open'); localStorage.setItem(KEY, body.classList.contains('sb-open') ? 'open' : 'closed'); }}
  }});
  const savedTheme = localStorage.getItem('editorial_theme');
  if (savedTheme === 'dark') document.documentElement.dataset.theme = 'dark';
  document.getElementById('themeToggle').addEventListener('click', () => {{
    const cur = document.documentElement.dataset.theme;
    const next = cur === 'dark' ? '' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('editorial_theme', next || 'light');
  }});
  document.addEventListener('keydown', (e) => {{
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 's' || e.key === 'S') {{ e.preventDefault(); document.getElementById('sbToggle').click(); }}
    if (e.key === 'd' || e.key === 'D') {{ e.preventDefault(); document.getElementById('themeToggle').click(); }}
  }});
  document.querySelectorAll('.sidebar a').forEach(a => {{
    a.addEventListener('click', () => {{
      if (!isWide()) {{ body.classList.remove('sb-open'); localStorage.setItem(KEY, 'closed'); }}
    }});
  }});
  const navLinks = [...document.querySelectorAll('.sidebar ul li')];
  const targets = navLinks.map(li => {{
    const a = li.querySelector('a');
    if (!a) return null;
    const id = a.getAttribute('href').slice(1);
    return {{ li, el: document.getElementById(id) }};
  }}).filter(x => x && x.el);
  const obs = new IntersectionObserver((entries) => {{
    entries.forEach(en => {{
      if (en.isIntersecting) {{
        const match = targets.find(t => t.el === en.target);
        if (match) {{ navLinks.forEach(li => li.classList.remove('active')); match.li.classList.add('active'); }}
      }}
    }});
  }}, {{ rootMargin: '-10% 0px -75% 0px' }});
  targets.forEach(t => obs.observe(t.el));
}})();
</script>

</body>
</html>
"""

def convert(src_path, out_path, brand, sub):
    if not os.path.exists(src_path):
        print(f'  [skip] not found: {src_path}'); return False
    with open(src_path, encoding='utf-8') as f:
        md = f.read()
    sections, body_html = parse_md(md)
    sidebar_html = build_sidebar(sections, brand, sub)
    title = brand
    slug = re.sub(r'[^\w-]', '_', os.path.splitext(os.path.basename(out_path))[0])
    page = TEMPLATE.format(title=title, sidebar=sidebar_html, body=body_html, slug=slug)
    out_full = os.path.join(BASE, out_path.replace('/', os.sep))
    os.makedirs(os.path.dirname(out_full), exist_ok=True)
    with open(out_full, 'w', encoding='utf-8') as f:
        f.write(page)
    sz = os.path.getsize(out_full)
    print(f'  [ok] {out_path} ({sz//1024} KB, {len(sections)} 섹션)')
    return True

if __name__ == '__main__':
    print('=== Markdown → Editorial HTML ===')
    ok = 0
    for j in JOBS:
        if convert(j['src'], j['out'], j['title'], j['subtitle']):
            ok += 1
    print(f'\n변환 완료: {ok}/{len(JOBS)}')
