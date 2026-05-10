"""
v2 강의안 골격 8개 생성기.

기존 session-XX-complete.html의 시각 언어(타이포·여백·배경)를 그대로 따르되,
'이론·개념 + 실습 시나리오' 하이브리드 오프라인 강의안 골격으로 재구성한다.

각 회차는 다음 구조로 생성된다:
  1. Cover
  2. Agenda (목차)
  3. 각 PART:
     - Part Divider (파트 표지)
     - 이론·개념 (Theory & Concept)
     - 실습 시나리오 (Practice Scenario)
  4. Closing (마무리)

산출물: session-01-v2.html ~ session-08-v2.html
"""

from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ───────────────────────────────────────────────────────────────────────────────
# HEAD (CSS + 폰트) — session-01-complete.html에서 차용한 디자인 토큰
# ───────────────────────────────────────────────────────────────────────────────
HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Session {num:02d} (v2) · {title}</title>
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700;9..144,800&family=Noto+Serif+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f5efe4;--bg2:#ede4d3;--ink:#2b2015;--ink2:#5a4a38;--ink3:#8a7659;--acc:#b8532a;--acc3:#d49575;--ln:#d8c8ae;--ln2:#e6d9bf;--dk:#1a1612;--dk2:#241e17;--on:#ede4d3;--on2:#a89172;--serif:'Fraunces','Noto Serif KR',Georgia,serif;--sans:'Pretendard Variable',Pretendard,sans-serif;--mono:'JetBrains Mono',ui-monospace,Consolas,monospace}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{margin:0;padding:0;overflow:hidden;height:100vh;width:100vw;background:#0e0a06;font-family:var(--sans);-webkit-font-smoothing:antialiased}}
.deck{{height:100vh;overflow-y:scroll;scroll-snap-type:y mandatory;scroll-behavior:smooth;scrollbar-width:none;-ms-overflow-style:none;background:#0e0a06}}
.deck::-webkit-scrollbar{{display:none}}
.stage{{width:100vw;min-height:100vh;display:flex;align-items:center;justify-content:center;scroll-snap-align:start;padding:0;background:#0e0a06}}
.slide{{width:1600px;height:900px;background:var(--bg);position:relative;overflow:hidden;transform-origin:center;box-shadow:0 40px 90px -30px rgba(0,0,0,0.7);background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' seed='3'/%3E%3CfeColorMatrix values='0 0 0 0 0.16  0 0 0 0 0.12  0 0 0 0 0.08  0 0 0 0.025 0'/%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E")}}
.slide.dark{{background:var(--dk);color:var(--on)}}
.slide.dark::before{{content:"";position:absolute;inset:0;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' seed='3'/%3E%3CfeColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.03 0'/%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E");pointer-events:none}}

/* ───── Header / Footer bars ───── */
.hbar{{position:absolute;top:0;left:0;right:0;height:52px;background:var(--dk);display:flex;align-items:center;justify-content:space-between;padding:0 80px;z-index:2}}
.hbar-l{{display:flex;align-items:center;gap:12px;font-family:var(--mono);font-size:10.5px;color:#fff;letter-spacing:2.5px;font-weight:600}}
.hbar-l::before{{content:"";width:22px;height:8px;background:var(--acc)}}
.hbar-r{{font-family:var(--mono);font-size:10.5px;color:#bbb;letter-spacing:1.5px}}
.fbar{{position:absolute;bottom:0;left:0;right:0;height:52px;background:#f0e8d8;border-top:3px solid var(--ln);display:flex;align-items:center;justify-content:space-between;padding:0 80px;z-index:2}}
.slide.dark .fbar{{background:var(--dk2);border-top-color:var(--acc)}}
.fbar-l,.fbar-r{{display:flex;flex-direction:column;gap:2px}}
.fbar-r{{align-items:flex-end}}
.fbar-label{{font-family:var(--mono);font-size:10px;color:var(--ink3);letter-spacing:2.5px;font-weight:700}}
.slide.dark .fbar-label{{color:var(--acc3)}}
.fbar-title{{font-size:13px;color:var(--ink)}}
.slide.dark .fbar-title{{color:var(--on)}}

/* ───── Headline block ───── */
.hl{{position:absolute;left:80px;right:80px;top:86px}}
.hl-kicker{{font-family:var(--mono);font-size:15px;color:var(--ink3);letter-spacing:2.5px;font-weight:700;margin-bottom:14px}}
.hl-title{{font-family:var(--serif);font-weight:700;font-size:36px;line-height:1.22;letter-spacing:-0.5px;color:var(--ink)}}
.hl-sub{{font-size:15.5px;color:var(--ink2);margin-top:12px;line-height:1.6}}
.hl-bar{{width:60px;height:3px;background:var(--ink);margin-top:16px}}
.hl-rule{{position:absolute;left:80px;right:80px;top:248px;height:1px;background:var(--ln2)}}

/* ───── Body grid ───── */
.bd{{position:absolute;left:80px;right:80px;top:264px;bottom:72px;display:grid;gap:1px;background:var(--ln2)}}
.bd.col2{{grid-template-columns:1fr 1fr}}
.bd.col2w{{grid-template-columns:1.25fr 1fr}}
.bd.col3{{grid-template-columns:1fr 1fr 1fr}}
.col{{background:var(--bg);padding:30px 34px;display:flex;flex-direction:column;overflow:hidden;min-width:0;gap:14px}}

/* ───── Card ───── */
.card{{background:var(--bg);padding:34px 36px;display:flex;flex-direction:column;gap:16px;overflow:hidden;min-width:0}}
.card.dk{{background:var(--dk);color:var(--on)}}
.card-k{{font-family:var(--mono);font-size:13px;color:var(--acc);letter-spacing:2.5px;font-weight:700}}
.card.dk .card-k{{color:var(--acc3)}}
.card-anchor{{font-family:var(--serif);font-size:24px;font-weight:700;line-height:1.25;color:var(--ink);letter-spacing:-0.4px}}
.card.dk .card-anchor{{color:var(--on)}}
.card-anchor em{{color:var(--acc);font-style:normal}}
.card.dk .card-anchor em{{color:var(--acc3)}}
.card-body{{font-size:14px;line-height:1.75;color:var(--ink2)}}
.card.dk .card-body{{color:var(--on2)}}
.card-body strong{{color:var(--ink);font-weight:700}}
.card.dk .card-body strong{{color:var(--on)}}
.card-spacer{{flex:1;min-height:8px}}
.card-note{{font-size:13px;color:var(--ink3);font-style:italic;line-height:1.6}}
.card.dk .card-note{{color:var(--on2)}}

/* ───── Placeholder marker ───── */
.ph{{border:1.5px dashed var(--ln);background:rgba(184,83,42,0.04);border-radius:4px;padding:18px 22px;color:var(--ink3);font-style:italic;line-height:1.7;font-size:13.5px}}
.ph-tag{{display:inline-block;font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--acc);font-weight:700;font-style:normal;padding:2px 8px;background:#fff;border:1px solid var(--acc);border-radius:2px;margin-bottom:8px}}
.ph ul{{margin-top:8px;padding-left:18px;font-size:13px;color:var(--ink2)}}
.ph ul li{{margin-bottom:4px;font-style:normal}}

/* ───── Agenda list ───── */
.agenda{{display:flex;flex-direction:column;gap:1px;background:var(--ln2)}}
.agenda-row{{display:grid;grid-template-columns:90px 1fr 220px;gap:18px;align-items:center;background:var(--bg);padding:14px 22px}}
.agenda-num{{font-family:var(--mono);font-size:13px;color:var(--acc);letter-spacing:2px;font-weight:700}}
.agenda-h{{font-family:var(--serif);font-size:18px;color:var(--ink);font-weight:700;line-height:1.35;letter-spacing:-0.3px}}
.agenda-d{{font-size:13px;color:var(--ink2);margin-top:3px;line-height:1.55}}
.agenda-tag{{font-family:var(--mono);font-size:10.5px;color:var(--ink3);letter-spacing:1.5px;font-weight:700;text-align:right}}

/* ───── Toolbar ───── */
.toolbar{{position:fixed;top:0;left:0;right:0;z-index:200;display:flex;align-items:center;justify-content:center;gap:6px;padding:6px 20px;background:rgba(14,10,6,0.92);backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,255,255,0.08)}}
.toolbar button{{background:rgba(255,255,255,0.08);color:#ccc;border:1px solid rgba(255,255,255,0.12);padding:5px 14px;font-family:var(--mono);font-size:10px;letter-spacing:1.5px;cursor:pointer;border-radius:3px;text-transform:uppercase;font-weight:600}}
.toolbar button:hover{{background:var(--acc);color:#fff;border-color:var(--acc)}}
.toolbar .pg{{color:rgba(255,255,255,0.55);font-size:11px;padding:5px 10px;min-width:80px;text-align:center;font-family:var(--mono);letter-spacing:1px}}

@media print{{
  @page{{size:423.33mm 237.5mm;margin:0}}
  *{{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}}
  html,body{{overflow:visible!important;height:auto!important;background:#fff!important}}
  .deck{{overflow:visible!important;height:auto!important;scroll-snap-type:none!important;background:#fff!important}}
  .stage{{min-height:0!important;height:auto!important;page-break-after:always;page-break-inside:avoid;padding:0!important;margin:0!important;background:#fff!important;display:block!important}}
  .stage:last-child{{page-break-after:avoid}}
  .slide{{transform:none!important;box-shadow:none!important;width:1600px!important;height:900px!important}}
  .toolbar{{display:none!important}}
}}
</style>
</head>
<body>
<div class="deck" id="deck">
"""

FOOTER_SCRIPT = r"""
</div>
<script>
(function(){
  document.querySelectorAll('.toolbar,.deck-nav').forEach(e=>e.remove());
  const tb = document.createElement('div');
  tb.className = 'toolbar';
  tb.innerHTML = `<button onclick="pNav(-1)">◀</button><span class="pg" id="pgInd">1 / 1</span><button onclick="pNav(1)">▶</button><button onclick="window.open(location.protocol==='blob:'?'https://cdsassj00.github.io/lecture-workbench/curriculum.html':'curriculum.html','_blank')">📋 CURRICULUM</button><button onclick="window.print()">⬇ PDF</button><button onclick="tFull()">⛶ FULL</button><button id="editBtn" onclick="tEdit()">✎ EDIT</button>`;
  document.body.appendChild(tb);
})();

const allSlides = document.querySelectorAll('.slide');
const allStages = document.querySelectorAll('.stage');
const deck = document.getElementById('deck');

function fitSlides(){const vw=innerWidth,vh=innerHeight;const r=Math.min(1,Math.min(vw/1600,vh/900));allSlides.forEach(s=>{s.style.transform=`scale(${r})`;s.style.transformOrigin='center center'})}
addEventListener('resize',fitSlides);fitSlides();

function curIdx(){let i=0,m=1e9;allStages.forEach((s,x)=>{const d=Math.abs(s.getBoundingClientRect().top+s.getBoundingClientRect().height/2-innerHeight/2);if(d<m){m=d;i=x}});return i}
function pNav(dir){const i=curIdx()+dir;if(i>=0&&i<allStages.length)allStages[i].scrollIntoView({behavior:'smooth'})}
function updPg(){document.getElementById('pgInd').textContent=`${curIdx()+1} / ${allStages.length}`}
deck.addEventListener('scroll',updPg);updPg();
function tFull(){if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen().catch(()=>{})}

let editMode=false;
function tEdit(){
  editMode=!editMode;
  const btn=document.getElementById('editBtn'),tb=document.querySelector('.toolbar');
  const SEL='.hl-kicker,.hl-title,.hl-sub,.card-k,.card-anchor,.card-body,.card-note,.hbar-l,.hbar-r,.fbar-title,.agenda-h,.agenda-d,.agenda-tag,.ph,h1,h2,p';
  if(editMode){btn.textContent='✎ EDITING';btn.style.background='#b8532a';btn.style.color='#fff';tb.style.borderBottom='2px solid #b8532a';
    document.querySelectorAll(SEL).forEach(el=>{el.contentEditable='true';el.style.outline='1px dashed rgba(184,83,42,0.3)';el.style.cursor='text'});
    deck.style.scrollSnapType='none';
    sToast('EDIT ON — 텍스트 클릭 수정 · Ctrl+S 저장 · E 또는 ESC로 종료');
  }else{btn.textContent='✎ EDIT';btn.style.background='';btn.style.color='';tb.style.borderBottom='';
    document.querySelectorAll('[contenteditable="true"]').forEach(el=>{el.contentEditable='false';el.style.outline='';el.style.cursor=''});
    deck.style.scrollSnapType='y mandatory';
    sToast('EDIT OFF — 프레젠테이션 모드');
  }
}
function sToast(m){let t=document.getElementById('toast');if(!t){t=document.createElement('div');t.id='toast';t.style.cssText='position:fixed;bottom:60px;left:50%;transform:translateX(-50%);background:rgba(14,10,6,0.92);color:#ede4d3;font-family:var(--mono,monospace);font-size:13px;letter-spacing:1.5px;padding:10px 24px;border-radius:4px;z-index:300;pointer-events:none;opacity:0;transition:opacity 0.4s';document.body.appendChild(t)}t.textContent=m;t.style.opacity='1';clearTimeout(t._tid);t._tid=setTimeout(()=>{t.style.opacity='0'},3000)}

document.addEventListener('keydown',e=>{
  if(editMode){
    if(e.key==='s'&&(e.ctrlKey||e.metaKey)){e.preventDefault();const b=new Blob(['<!DOCTYPE html>\n'+document.documentElement.outerHTML],{type:'text/html'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=document.title.replace(/[^a-zA-Z0-9가-힣\s·_-]/g,'')+'.html';a.click();URL.revokeObjectURL(a.href);sToast('HTML 파일 저장 완료')}
    if(e.key==='Escape'||e.key==='e'||e.key==='E'){if(!document.activeElement||document.activeElement===document.body)tEdit()}
    return;
  }
  if(e.key==='ArrowRight'||e.key==='ArrowDown'||e.key===' '||e.key==='PageDown'){e.preventDefault();pNav(1)}
  else if(e.key==='ArrowLeft'||e.key==='ArrowUp'||e.key==='PageUp'){e.preventDefault();pNav(-1)}
  else if(e.key==='Home'){e.preventDefault();allStages[0].scrollIntoView({behavior:'smooth'})}
  else if(e.key==='End'){e.preventDefault();allStages[allStages.length-1].scrollIntoView({behavior:'smooth'})}
  else if(e.key==='f'||e.key==='F11'){e.preventDefault();tFull()}
  else if(e.key==='Escape'){if(document.fullscreenElement)document.exitFullscreen()}
  else if(e.key==='e'||e.key==='E'){tEdit()}
});
</script>
</body>
</html>
"""


# ───────────────────────────────────────────────────────────────────────────────
# 8회차 메타데이터
# 각 회차의 parts: (구분, 제목, 부제·요약)
# 1회차는 기존 골격을 그대로 유지하지 않고 'v2 골격'으로 단순화하되 같은 8주 흐름의 출발점.
# 2~8회차는 사용자 제공 아웃라인을 반영.
# ───────────────────────────────────────────────────────────────────────────────
SESSIONS = [
    {
        "num": 1,
        "title": "AI 에이전트 시대의 개막과 공공 구현 지형도",
        "subtitle": "거점리더의 환경 세팅과 9유형 지형도 — 8주 동안 무엇을 만드는가",
        "module_short": "AI 에이전트 시대 · 공공 구현 지형도",
        "parts": [
            ("OPENING", "거점리더 정체성과 페인포인트 캡처",
             "본 과정 수강생을 거점리더로 정의한다. 문제해결자·공유확산자·검증자 세 정체성과 결핍 캡처 5질문(Who·When·What blocks·How long·Workaround)으로 미션의 출발선을 세운다."),
            ("PART 1", "AI·NLP 진화사",
             "Bard/PaLM → GPT → Agent까지의 흐름을 한 장에 압축한다. 어디까지 왔고, 거점리더가 지금 서 있는 위치는 어디인가."),
            ("PART 2", "MicroGPT로 Q·K·V 체감",
             "수식 없이 Query·Key·Value·Multi-head를 직관으로 잡는다. 트랜스포머가 왜 컨텍스트를 다루는 데 강한지 한 장으로 설명한다."),
            ("PART 3", "프롬프트 → 컨텍스트 → 하네스",
             "어시스트와 에이전트의 차이를 시스템 관점에서 정리한다. 단발 프롬프트, 컨텍스트 쌓기, 하네스(도구·기억·계획)까지의 진화."),
            ("PART 4", "프론티어 모델 5종",
             "GPT · Claude · Gemini · Grok · OSS(오픈소스) 5종의 강점과 공공 활용 포인트를 비교한다."),
            ("PART 5", "공공 9유형 구현 지도",
             "9가지 공공 구현 유형을 한 장의 지도로 펼친다. 각 유형이 본 과정 어디에서 다뤄지는지 매핑."),
            ("PART 6", "환경 세팅",
             "Git · WSL · Node.js · Python · VS Code · Power BI Desktop. 8주 내내 쓸 도구를 한 번에 세팅한다."),
            ("CLOSING", "거점 미션 선언",
             "5질문 결과를 미션 선언서 1장으로 정리한다. 공용 저장소(GitHub Org)에 첫 커밋."),
        ],
    },
    {
        "num": 2,
        "title": "LLM 사용 서비스 마스터리",
        "subtitle": "ChatGPT · Claude · Gemini + 노코드 바이브코딩 도구 — 외부망에서 가능한 모든 것",
        "module_short": "LLM 사용 서비스 마스터리",
        "parts": [
            ("OPENING", "자기소개 + Fuse.js 챗봇 리버스엔지니어링",
             "https://cdsassj00.github.io/2026-proposals-rss/ 사이트를 함께 열어, Fuse.js로 만든 '챗봇 흉내내기'의 동작을 분해한다. 1시간 분량."),
            ("PART 1", "1주차 과제 리뷰 — Hugging Face SLM",
             "수강생이 조사한 SLM 스펙을 모아 48개 SLM 카드 사이트(예정)로 정리. 강의 매뉴얼로 활용."),
            ("PART 2", "공공 적용 9유형 맛보기 + 사전 설치",
             "유형 01 AI 코드 내부망 실행 / 02 VBA+로컬 sLLM(Ollama) / 03 Python+PyInstaller / 04 Electron / 05 HTML+CSS+JS 단일 파일 / 06 Node.js CLI / 07 Ollama 로컬 RAG / 08 백엔드 결합 웹 / 09 API·MCP 풀스택. 필요한 프로그램을 같이 깐다."),
            ("PART 3", "ChatGPT 활용 팁 + 약간의 바이브코딩",
             "ChatGPT로 SVG · HTML · Mermaid를 즉석에서 만들고 화면에서 검증하는 흐름. '만약에 이 기능이 우리 기관·내 업무 어디에 적용될까'를 같이 토의."),
            ("PART 4", "Gemini 활용 팁",
             "NotebookLM · AI Studio · Flow · labs.google. 특히 AI Studio가 지금 어디까지 왔는지 라이브로 살펴본다."),
            ("PART 5", "Claude 활용 팁",
             "Projects · Artifacts · MCP를 활용한 거점리더 워크플로우. ChatGPT/Gemini와의 차이점을 짚는다."),
            ("PART 6", "강사 추천 사이트 + 실습결과 공유",
             "워크벤치 강의안에 박아둔 사이트들을 함께 돌아본다. 사이트만 보지 않고 즉시 실습 → 결과물을 구글드라이브 공용 폴더에 업로드."),
            ("PART 7", "GitHub 가입 + 노코드 바이브코딩 툴",
             "1주차 과제 때문에 모두 GitHub 가입 완료. Lovable · Bolt · v0 · Replit + GitHub 연동을 한 자리에서 비교한다."),
            ("CLOSING", "내가 자주 쓰는 AI 툴 리스트",
             "각자 자주 쓰는 AI 도구를 구글시트 한 장에 모은다. 거점리더 공동 큐레이션의 시작점."),
        ],
    },
    {
        "num": 3,
        "title": "바이브코딩 워크플로우",
        "subtitle": "오픈코드 + 안티그래비티 + 코딩에이전트로 파일·문서를 다룬다",
        "module_short": "바이브코딩 워크플로우",
        "parts": [
            ("OPENING", "오픈코드 소개 (Codex · Antigravity)",
             "오픈코드 계열 도구를 개관한다. Claude Code는 6주차에서 본격적으로 다루므로 이번 주차에서는 가볍게 짚고 넘어간다."),
            ("PART 1", "환경 세팅",
             "오픈코드 설치 → 안티그래비티 설치 → 안티그래비티 확장으로 오픈코드 설치 → oh my agent 설치 + 명령어 한 바퀴."),
            ("PART 2", "파이썬으로 파일시스템 다루기",
             "폴더 생성 · 삭제 · 압축 등 기초 파일시스템 작업을 Python 또는 Jupyter Notebook에서 코딩에이전트로 처리한다."),
            ("PART 3", "파이썬으로 hwpx 다루기",
             "GitHub 오픈소스 + python-hwpx 라이브러리를 활용해 한글 문서를 다루는 기본 패턴을 익힌다."),
            ("PART 4", "파이썬으로 PDF 다루기",
             "PDF ↔ 엑셀/hwpx/docx 전환, PDF 통합·분리, 표·텍스트·이미지 추출. Python 또는 Jupyter, 코딩에이전트 활용."),
            ("PART 5", "파이썬으로 엑셀 다루기",
             "시트 통합·분리, 계산표 생성, 새 엑셀 파일 만들기. Jupyter Notebook 또는 코딩에이전트로 진행."),
            ("PART 6", "엑셀 싱크 (LLM 프롬프트)",
             "LLM 프롬프트만으로 엑셀 작업을 자동화하는 흐름. 비코딩 트랙 동료에게 인계하기 좋은 패턴."),
            ("PART 7", "외부 GitHub 다루기",
             "markitdown 등 외부 라이브러리를 코딩에이전트가 가져와서 작업하게 한다. 다양한 GitHub 레퍼런스는 노션에 정리되어 있음."),
            ("CLOSING", "그린 · 블루 연습문제 풀이",
             "기본기 적용 실습. 위 7파트의 도구를 한 미션 안에서 조합한다."),
        ],
    },
    {
        "num": 4,
        "title": "데이터분석 — 코딩에이전트 트랙",
        "subtitle": "엑셀 · LLM · SQL · 파이썬 · 쥬피터 · 머신러닝",
        "module_short": "데이터분석 트랙",
        "parts": [
            ("OPENING", "데이터분석 트랙 개관",
             "엑셀 · LLM · SQL · 파이썬 4축으로 분석 워크플로우를 매핑한다. 거점리더 미션의 데이터 후보를 같이 적는다."),
            ("PART 1", "엑셀 + LLM 데이터분석",
             "엑셀과 LLM을 함께 쓰는 표준 패턴. 파워쿼리 · VBA까지 포함해 사무 환경에서 바로 쓰는 데이터 처리."),
            ("PART 2", "HTML · CSS · JS 데이터시각화",
             "LLM과 코딩에이전트로 HTML 차트를 만든다. 파워BI · 그라파나 같은 BI 도구 활용도 같이 다룬다."),
            ("PART 3", "LLM 기반 SQL 마스터",
             "SQLite · MySQL을 코딩에이전트와 LLM이 어떻게 다루게 할지. 쿼리 생성·검증·디버깅 루프."),
            ("PART 4", "구글코랩으로 csv 분석",
             "일반 csv 파일을 구글코랩에서 분석하는 가장 가벼운 코스. 코딩 미경험자에게 부담 없는 진입로."),
            ("PART 5", "파이썬 + 쥬피터노트북 설치",
             "로컬 분석 환경 구성. 가상환경 · 커널 · 확장. 다음 파트의 출발점이 된다."),
            ("PART 6", "파이썬 API 데이터 수집",
             "공공 API · 외부 API에서 데이터를 직접 수집한다. 인증 · 페이지네이션 · 저장 패턴."),
            ("PART 7", "쥬피터노트북 머신러닝 · 딥러닝",
             "기본 ML/DL 모델링을 코딩에이전트가 거든다. 거점리더는 결과 검증·해석에 집중."),
            ("CLOSING", "(선택) 지리정보 파일 다루기",
             "여유가 있으면 GIS · 공간 데이터 입문. 시간이 빠듯하면 다음 주차로 이월."),
        ],
    },
    {
        "num": 5,
        "title": "공공 9유형 — 코딩에이전트 구현 6선",
        "subtitle": "외부망 어시스트로 코드 받아 내부망에서 실행하는 6가지 패턴",
        "module_short": "공공 9유형 코딩에이전트 구현",
        "parts": [
            ("OPENING", "9유형 지도 다시 보기",
             "1·2주차에서 본 9유형 지도를 다시 펼치고, 이번 주차에서 본격 구현할 6유형(01·02·03·04·05·06)을 픽업한다. 07·08·09는 6~8주차로 이월."),
            ("PART 1", "유형 01 — AI 코드 내부망 실행",
             "외부망에서 받은 파이썬 코드를 내부망에서 단순 실행하는 가장 기본적인 패턴. 권한·로그 점검 포함."),
            ("PART 2", "유형 02 — VBA + 로컬 sLLM(Ollama)",
             "엑셀 매크로와 로컬 sLLM을 결합해 인터넷 없이도 돌아가는 자동화. 보안망 환경의 표준 후보."),
            ("PART 3", "유형 03 — Python + PyInstaller (.exe)",
             "독립 실행 가능한 .exe 파일로 패키징. 동료 PC에 설치 없이 바로 돌릴 수 있는 형태."),
            ("PART 4", "유형 04 — Electron 데스크톱 앱",
             "GUI가 필요한 도구를 Electron으로 만든다. 비개발자 동료가 쓰는 화면을 직접 디자인."),
            ("PART 5", "유형 05 — HTML + CSS + JS + CDN 로컬화",
             "단일 HTML 파일 앱. 워크벤치 강의안과 같은 형식. 폐쇄망에서도 돌아가도록 CDN을 로컬화하는 패턴."),
            ("PART 6", "유형 06 — Node.js 로컬 툴 / CLI",
             "자동화 스크립트와 CLI 도구를 Node.js로 만든다. 정기 작업·일괄 처리에 강하다."),
            ("CLOSING", "유형별 산출물 정리",
             "오늘 만든 6유형 사례를 비교 정리. 7·8·9 유형은 다음 주차에서 풀스택으로 다룬다는 예고."),
        ],
    },
    {
        "num": 6,
        "title": "외부 서비스 풀스택 바이브코딩",
        "subtitle": "코딩에이전트 + GitHub + Vercel/Netlify + Supabase",
        "module_short": "풀스택 바이브코딩",
        "parts": [
            ("OPENING", "풀스택 바이브코딩 지도",
             "프론트엔드 → 깃헙 → 배포 → 백엔드(Supabase) → MCP까지의 전체 파이프라인을 한 장에 펼친다."),
            ("PART 1", "프론트엔드 → GitHub 커밋 · 푸쉬",
             "코딩에이전트로 프론트엔드 코드를 만들고 GitHub에 커밋·푸쉬하는 손길 실습."),
            ("PART 2", "프론트엔드 배포",
             "코딩에이전트 → GitHub → Vercel 또는 Netlify로 배포까지 한 번에. URL을 동료에게 공유 가능한 상태로."),
            ("PART 3", "코딩에이전트 + Supabase 연결",
             "데이터베이스 · 인증을 Supabase로 붙인다. 코딩에이전트가 스키마·쿼리를 같이 만들게 한다."),
            ("PART 4", "코딩에이전트 풀스택 배포",
             "프론트와 백엔드를 동시에 배포하는 풀스택 흐름. 거점 미션 MVP의 그릇이 된다."),
            ("PART 5", "거점 미션 아이디어 워크숍",
             "각자 부서 미션 1건을 디자인. 페인포인트 5질문 → 화면 와이어프레임 → 데이터 모델 한 장."),
            ("CLOSING", "실제 개발 착수 — MVP 만들기",
             "1차 MVP 산출물을 합의하고 7·8주차 동안 다듬을 범위를 확정한다."),
        ],
    },
    {
        "num": 7,
        "title": "풀스택 바이브코딩 심화 I",
        "subtitle": "거점 미션 MVP 다듬기 — 운영 가능한 형태로",
        "module_short": "풀스택 바이브코딩 심화 I",
        "parts": [
            ("OPENING", "6주차 산출물 점검",
             "각자 만든 MVP를 짧게 시연한다. 막힌 지점을 모아 이번 주차 학습 메뉴에 반영."),
            ("PART 1", "코딩에이전트 운영 패턴",
             "Plan → Edit → Verify 루프. 에이전트가 스스로 점검하게 만드는 지시법."),
            ("PART 2", "RAG · 벡터DB 결합",
             "조례·매뉴얼·내부 문서를 벡터스토어에 넣고 검색·요약 라인으로 쓴다. 공공 도메인의 RAG 패턴."),
            ("PART 3", "API / MCP 연동 실습",
             "외부 API와 MCP 서버를 붙인다. 거점 미션을 다른 시스템과 연결하는 표준 인터페이스."),
            ("PART 4", "권한 · 로그 · 보안 점검",
             "공공 운영의 기본기. 누가 무엇을 했는지 남기고, 누가 무엇을 볼 수 있는지 분리한다."),
            ("PART 5", "동료 인계용 README",
             "산출물 4종(프롬프트.md / 도구체인 README / 결과물 / 1페이지 가이드)의 1페이지 가이드 작성법."),
            ("CLOSING", "다음 주차 발표 준비",
             "8주차 종강 발표용 5~7분 데모 시나리오를 잡는다. 어시스트·에이전트 두 결과물의 비교 포인트."),
        ],
    },
    {
        "num": 8,
        "title": "풀스택 바이브코딩 심화 II — 종강 발표",
        "subtitle": "거점 미션 산출물 발표 + 공용 아카이브 등록",
        "module_short": "풀스택 바이브코딩 심화 II · 종강",
        "parts": [
            ("OPENING", "종강 흐름 안내",
             "오늘은 발표 → 검증 → 아카이브 등록 → 인계 순서로 진행한다. 수료 기준과 평가 포인트를 먼저 합의."),
            ("PART 1", "거점 미션 발표 1부",
             "어시스트 결과물 + 에이전트 결과물 두 벌을 5~7분 시연. 1부 진행."),
            ("PART 2", "거점 미션 발표 2부",
             "이어지는 발표 + 상호 피드백. 도메인 다른 거점리더의 시각으로 검증."),
            ("PART 3", "검증 워크숍",
             "재현성 · 법령 부합 · 권한 점검을 항목 단위로 본다. 공공 운영을 견디는지 함께 본다."),
            ("PART 4", "공용 아카이브 등록",
             "GitHub Org에 4종 산출물 묶음을 등록한다. 차기 거점리더 기수의 시드 라이브러리가 된다."),
            ("PART 5", "차기 거점리더 인계",
             "다음 기수가 그대로 따라할 수 있는 인계 가이드 1페이지를 같이 다듬는다."),
            ("CLOSING", "수료 + 거점리더 다짐",
             "수료증 수여 + 다음 기수와의 연결 약속. 거점리더는 8주에서 끝나지 않는다."),
        ],
    },
]


# ───────────────────────────────────────────────────────────────────────────────
# 슬라이드 빌더
# ───────────────────────────────────────────────────────────────────────────────
def cover_slide(num: int, title: str, subtitle: str, parts: list, total_pages: int) -> str:
    parts_html = ""
    for idx, (kind, ptitle, _psub) in enumerate(parts):
        parts_html += (
            f'<div style="border-top:2px solid var(--acc);padding-top:10px">'
            f'<div style="font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--ink3);font-weight:700;margin-bottom:5px">{kind}</div>'
            f'<div style="font-size:13px;color:var(--ink);font-weight:700;line-height:1.4">{ptitle}</div>'
            f'</div>'
        )
    cols = max(2, len(parts))
    return f"""
<!-- ═══ COVER ═══ -->
<div class="stage"><div class="slide" data-title="Cover">
  <div class="hbar"><div class="hbar-l">SESSION {num:02d} · LECTURE COVER · v2 SKELETON</div><div class="hbar-r">AI 챔피언 고급 과정 · Session {num:02d} of 08</div></div>

  <div style="position:absolute;top:140px;right:72px;font-family:var(--serif);font-size:280px;line-height:1;color:var(--acc);font-weight:300;opacity:0.08;letter-spacing:-0.06em;pointer-events:none;font-style:italic">{num:02d}</div>

  <div style="position:absolute;top:92px;left:80px;display:flex;align-items:center;gap:12px;font-family:var(--mono);font-size:12px;color:var(--acc);letter-spacing:3px;font-weight:700">
    <div style="width:26px;height:2px;background:var(--acc)"></div>
    PUBLIC AI EXPERT PROGRAM · 2026 · v2
  </div>

  <div style="position:absolute;top:150px;left:80px;max-width:1200px">
    <div style="font-family:var(--mono);font-size:12px;color:var(--ink3);letter-spacing:2.5px;font-weight:700;margin-bottom:16px">SESSION {num:02d} · 8H · v2 골격</div>
    <h1 style="font-family:var(--serif);font-weight:700;font-size:58px;line-height:1.06;letter-spacing:-0.04em;color:var(--ink);margin-bottom:18px">{title}</h1>
    <div style="width:72px;height:3px;background:var(--ink);margin-bottom:20px"></div>
    <div style="font-family:var(--serif);font-size:21px;color:var(--ink);font-weight:600;line-height:1.5;letter-spacing:-0.01em">{subtitle}</div>
    <p style="margin-top:22px;font-size:13.5px;color:var(--ink2);line-height:1.85;max-width:1050px">본 회차의 v2 골격은 <strong style="color:var(--ink)">이론·개념 설명</strong>과 <strong style="color:var(--ink)">실습 시나리오</strong>의 하이브리드 오프라인 강의안 구조를 따른다. 각 PART는 (1) 파트 표지 (2) 이론·개념 (3) 실습 시나리오 세 슬라이드로 구성되며, 본문은 <strong style="color:var(--ink)">강사 작성 영역</strong>으로 비어 있다. 기존 session-{num:02d}-complete.html은 보존되며 v2는 별도 파일로 운용한다.</p>
  </div>

  <div style="position:absolute;top:340px;right:80px;width:380px;border-top:2px solid var(--ink);padding-top:18px">
    <div style="font-family:var(--mono);font-size:12px;color:var(--ink3);letter-spacing:2.5px;font-weight:700;margin-bottom:18px">COURSE METADATA</div>
    <div style="display:grid;grid-template-columns:100px 1fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--ln);font-size:13px"><span style="font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--ink3);font-weight:700">PROGRAM</span><span style="color:var(--ink);font-weight:600">AI 챔피언 고급 과정</span></div>
    <div style="display:grid;grid-template-columns:100px 1fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--ln);font-size:13px"><span style="font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--ink3);font-weight:700">SESSION</span><span style="color:var(--ink);font-weight:600">{num:02d} / 08 · 8시간</span></div>
    <div style="display:grid;grid-template-columns:100px 1fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--ln);font-size:13px"><span style="font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--ink3);font-weight:700">TARGET</span><span style="color:var(--ink);font-weight:600">공공 거점리더 후보</span></div>
    <div style="display:grid;grid-template-columns:100px 1fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--ln);font-size:13px"><span style="font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--ink3);font-weight:700">FORMAT</span><span style="color:var(--ink);font-weight:600">이론 + 실습 시나리오</span></div>
    <div style="display:grid;grid-template-columns:100px 1fr;gap:10px;padding:10px 0;font-size:13px"><span style="font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--ink3);font-weight:700">STATUS</span><span style="color:var(--acc);font-weight:700">v2 SKELETON</span></div>
  </div>

  <div style="position:absolute;bottom:80px;left:80px;right:80px;display:grid;grid-template-columns:repeat({cols},1fr);gap:8px">
    {parts_html}
  </div>

  <div class="fbar"><div class="fbar-l"><span class="fbar-label">MODULE</span><span class="fbar-title">{num:02d} · {title}</span></div><div class="fbar-r"><span class="fbar-label">PAGE</span><span class="fbar-title">001 / {total_pages:03d}</span></div></div>
</div></div>
"""


def agenda_slide(num: int, title: str, parts: list, page_no: int, total_pages: int) -> str:
    rows = ""
    for idx, (kind, ptitle, psub) in enumerate(parts, start=1):
        rows += (
            f'<div class="agenda-row">'
            f'<div class="agenda-num">{idx:02d} · {kind}</div>'
            f'<div><div class="agenda-h">{ptitle}</div><div class="agenda-d">{psub}</div></div>'
            f'<div class="agenda-tag">3 SLIDES · 이론 / 실습</div>'
            f'</div>'
        )
    return f"""
<!-- ═══ AGENDA ═══ -->
<div class="stage"><div class="slide" data-title="Agenda">
  <div class="hbar"><div class="hbar-l">AGENDA · 본 회차 흐름</div><div class="hbar-r">AI 챔피언 고급 과정 · Session {num:02d}</div></div>
  <div class="hl">
    <div class="hl-kicker">AGENDA · 오늘의 8시간을 한 장에</div>
    <div class="hl-title">목차 — 본 회차의 PART 흐름</div>
    <div class="hl-sub">각 PART는 (1) 파트 표지 (2) 이론·개념 (3) 실습 시나리오 세 슬라이드로 구성된다. 강사 작성 영역에는 회차 직전에 수강생 수준·현업 이슈를 반영해 본문을 채운다.</div>
    <div class="hl-bar"></div>
  </div>
  <div class="hl-rule"></div>
  <div class="bd" style="grid-template-columns:1fr;gap:0;background:transparent">
    <div class="agenda" style="overflow:auto">{rows}</div>
  </div>
  <div class="fbar"><div class="fbar-l"><span class="fbar-label">MODULE</span><span class="fbar-title">{num:02d} · {title}</span></div><div class="fbar-r"><span class="fbar-label">PAGE</span><span class="fbar-title">{page_no:03d} / {total_pages:03d}</span></div></div>
</div></div>
"""


def part_divider_slide(num: int, title: str, idx: int, kind: str, ptitle: str, psub: str, page_no: int, total_pages: int) -> str:
    return f"""
<!-- ═══ PART {idx:02d} DIVIDER ═══ -->
<div class="stage"><div class="slide dark" data-title="P{idx} Divider">
  <div class="hbar"><div class="hbar-l">{kind} · 파트 표지 · {idx:02d} of {len(SESSIONS[num-1]['parts']):02d}</div><div class="hbar-r">AI 챔피언 고급 과정 · Session {num:02d}</div></div>

  <div style="position:absolute;top:160px;left:80px;right:80px">
    <div style="font-family:var(--mono);font-size:13px;color:var(--acc3);letter-spacing:3px;font-weight:700;margin-bottom:24px">PART {idx:02d} · {kind}</div>
    <h2 style="font-family:var(--serif);font-weight:700;font-size:72px;line-height:1.08;letter-spacing:-0.04em;color:var(--on);margin-bottom:28px">{ptitle}</h2>
    <div style="width:120px;height:3px;background:var(--acc);margin-bottom:32px"></div>
    <p style="font-size:18px;color:var(--on2);line-height:1.7;max-width:1100px">{psub}</p>
  </div>

  <div style="position:absolute;bottom:120px;left:80px;right:80px;display:grid;grid-template-columns:1fr 1fr;gap:24px">
    <div style="border-left:3px solid var(--acc3);padding:16px 22px;background:rgba(255,255,255,0.04)">
      <div style="font-family:var(--mono);font-size:11px;color:var(--acc3);letter-spacing:2.5px;font-weight:700;margin-bottom:8px">SLIDE A · THEORY</div>
      <div style="color:var(--on);font-size:15px;line-height:1.6;font-weight:600">이론 · 개념 설명</div>
      <div style="color:var(--on2);font-size:13px;line-height:1.65;margin-top:6px">왜 이 도구·기법을 다루는가, 핵심 개념과 작동 원리를 한 장으로 정리.</div>
    </div>
    <div style="border-left:3px solid var(--acc3);padding:16px 22px;background:rgba(255,255,255,0.04)">
      <div style="font-family:var(--mono);font-size:11px;color:var(--acc3);letter-spacing:2.5px;font-weight:700;margin-bottom:8px">SLIDE B · PRACTICE</div>
      <div style="color:var(--on);font-size:15px;line-height:1.6;font-weight:600">실습 시나리오</div>
      <div style="color:var(--on2);font-size:13px;line-height:1.65;margin-top:6px">수강생이 직접 손을 움직이는 실습. 입력·과정·산출물을 명시.</div>
    </div>
  </div>

  <div class="fbar"><div class="fbar-l"><span class="fbar-label">MODULE</span><span class="fbar-title">{num:02d} · {title}</span></div><div class="fbar-r"><span class="fbar-label">PAGE</span><span class="fbar-title">{page_no:03d} / {total_pages:03d}</span></div></div>
</div></div>
"""


def theory_slide(num: int, title: str, idx: int, kind: str, ptitle: str, psub: str, page_no: int, total_pages: int) -> str:
    return f"""
<!-- ═══ PART {idx:02d} · THEORY ═══ -->
<div class="stage"><div class="slide" data-title="P{idx} Theory">
  <div class="hbar"><div class="hbar-l">{kind} · 이론 · 개념</div><div class="hbar-r">AI 챔피언 고급 과정 · Session {num:02d}</div></div>
  <div class="hl">
    <div class="hl-kicker">PART {idx:02d} · THEORY · 이론 · 개념</div>
    <div class="hl-title">{ptitle} — 핵심 개념과 작동 원리</div>
    <div class="hl-sub">{psub}</div>
    <div class="hl-bar"></div>
  </div>
  <div class="hl-rule"></div>
  <div class="bd col2w">
    <div class="card">
      <div class="card-k">CONCEPT · 핵심 개념</div>
      <div class="card-anchor"><em>{ptitle}</em>의 핵심 한 줄</div>
      <div class="ph">
        <span class="ph-tag">강사 작성 영역</span>
        이 도구·기법이 무엇이고 왜 다루는가를 1~2문단으로 정리.
        <ul>
          <li>핵심 정의 한 줄</li>
          <li>왜 이 자리에 들어가는가 (앞 PART와의 연결)</li>
          <li>거점리더가 알아야 할 최소 원리</li>
        </ul>
      </div>
      <div class="card-spacer"></div>
      <div class="card-note">팁 — 수강생 수준에 맞춰 1) 비유 1개 2) 1문장 정의 3) 시각 자료 1개로 압축한다.</div>
    </div>
    <div class="card dk">
      <div class="card-k">MECHANICS · 작동 원리</div>
      <div class="card-anchor"><em>이렇게</em> 동작한다</div>
      <div class="ph" style="border-color:rgba(212,149,117,0.5);background:rgba(212,149,117,0.06);color:var(--on2)">
        <span class="ph-tag" style="background:transparent;color:var(--acc3);border-color:var(--acc3)">강사 작성 영역</span>
        도구 또는 기법의 작동 원리·구성요소·데이터 흐름을 한 장으로 정리.
        <ul style="color:var(--on2)">
          <li>구성요소 3~5개</li>
          <li>입력 → 처리 → 출력 흐름</li>
          <li>거점리더가 자주 만날 함정 1~2개</li>
        </ul>
      </div>
      <div class="card-spacer"></div>
      <div class="card-note">팁 — 수식·코드는 최소화. 박스·화살표 다이어그램으로 한 장 안에 끝낸다.</div>
    </div>
  </div>
  <div class="fbar"><div class="fbar-l"><span class="fbar-label">MODULE</span><span class="fbar-title">{num:02d} · {title}</span></div><div class="fbar-r"><span class="fbar-label">PAGE</span><span class="fbar-title">{page_no:03d} / {total_pages:03d}</span></div></div>
</div></div>
"""


def practice_slide(num: int, title: str, idx: int, kind: str, ptitle: str, psub: str, page_no: int, total_pages: int) -> str:
    return f"""
<!-- ═══ PART {idx:02d} · PRACTICE ═══ -->
<div class="stage"><div class="slide" data-title="P{idx} Practice">
  <div class="hbar"><div class="hbar-l">{kind} · 실습 시나리오</div><div class="hbar-r">AI 챔피언 고급 과정 · Session {num:02d}</div></div>
  <div class="hl">
    <div class="hl-kicker">PART {idx:02d} · PRACTICE · 실습 시나리오</div>
    <div class="hl-title">{ptitle} — 손을 움직이는 시간</div>
    <div class="hl-sub">이 슬라이드는 수강생이 직접 따라하거나 도전하는 실습 단위 한 장. 입력·과정·산출물·검증 기준을 명시한다.</div>
    <div class="hl-bar"></div>
  </div>
  <div class="hl-rule"></div>
  <div class="bd col3">
    <div class="card">
      <div class="card-k">SCENARIO · 시나리오</div>
      <div class="card-anchor"><em>오늘 만들 것</em>을 한 줄로</div>
      <div class="ph">
        <span class="ph-tag">강사 작성 영역</span>
        실습 미션을 1문장으로 정의. 누가, 무엇을, 어디까지 만드는가.
        <ul>
          <li>대상 사용자(거점리더 자신/동료/시민)</li>
          <li>입력 데이터·자료</li>
          <li>완성 기준 1~2개</li>
        </ul>
      </div>
      <div class="card-spacer"></div>
      <div class="card-note">팁 — '만들 산출물 파일 형식'이 정해져야 시간 계산이 가능하다.</div>
    </div>
    <div class="card dk">
      <div class="card-k">STEPS · 손길 단계</div>
      <div class="card-anchor"><em>3~5단계</em>로 끊어 쓴다</div>
      <div class="ph" style="border-color:rgba(212,149,117,0.5);background:rgba(212,149,117,0.06);color:var(--on2)">
        <span class="ph-tag" style="background:transparent;color:var(--acc3);border-color:var(--acc3)">강사 작성 영역</span>
        실제 손길 단계 3~5개. 각 단계는 한 줄로 끊는다.
        <ul style="color:var(--on2)">
          <li>STEP 1 — 입력 준비</li>
          <li>STEP 2 — 도구 호출 / 프롬프트</li>
          <li>STEP 3 — 결과 검증</li>
          <li>STEP 4 — 정리 / 공유</li>
        </ul>
      </div>
      <div class="card-spacer"></div>
      <div class="card-note">팁 — 쉬는 시간 빼고 25~40분 안에 끝나는 단위.</div>
    </div>
    <div class="card">
      <div class="card-k">CHECK · 검증 / 산출물</div>
      <div class="card-anchor"><em>어디까지 되면</em> 통과인가</div>
      <div class="ph">
        <span class="ph-tag">강사 작성 영역</span>
        통과 기준과 산출물 위치를 명시.
        <ul>
          <li>완성 기준(예: 동료가 같은 입력으로 같은 결과)</li>
          <li>산출물 저장 위치(공용 폴더/GitHub Org)</li>
          <li>흔한 실패 패턴 1~2개</li>
        </ul>
      </div>
      <div class="card-spacer"></div>
      <div class="card-note">팁 — 통과 기준이 1줄로 안 적히면 실습이 흐릿해진다.</div>
    </div>
  </div>
  <div class="fbar"><div class="fbar-l"><span class="fbar-label">MODULE</span><span class="fbar-title">{num:02d} · {title}</span></div><div class="fbar-r"><span class="fbar-label">PAGE</span><span class="fbar-title">{page_no:03d} / {total_pages:03d}</span></div></div>
</div></div>
"""


def closing_slide(num: int, title: str, page_no: int, total_pages: int) -> str:
    next_text = "다음 회차 예고 + 다음 주차까지의 과제(있다면) 한 줄"
    if num == 8:
        next_text = "수료 + 차기 거점리더 기수 인계"
    return f"""
<!-- ═══ CLOSING ═══ -->
<div class="stage"><div class="slide dark" data-title="Closing">
  <div class="hbar"><div class="hbar-l">CLOSING · 마무리</div><div class="hbar-r">AI 챔피언 고급 과정 · Session {num:02d}</div></div>

  <div style="position:absolute;top:140px;left:80px;right:80px">
    <div style="font-family:var(--mono);font-size:13px;color:var(--acc3);letter-spacing:3px;font-weight:700;margin-bottom:24px">CLOSING · 본 회차를 닫는 한 장</div>
    <h2 style="font-family:var(--serif);font-weight:700;font-size:54px;line-height:1.1;letter-spacing:-0.03em;color:var(--on);margin-bottom:24px">오늘 만든 것 · 가져갈 것 · 다음 회차</h2>
    <div style="width:80px;height:3px;background:var(--acc);margin-bottom:24px"></div>
  </div>

  <div style="position:absolute;top:380px;left:80px;right:80px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:#3a2f24">
    <div style="background:var(--dk2);padding:24px 28px">
      <div style="font-family:var(--mono);font-size:12px;color:var(--acc3);letter-spacing:2.5px;font-weight:700;margin-bottom:14px">RECAP · 오늘 만든 것</div>
      <div class="ph" style="border-color:rgba(212,149,117,0.5);background:rgba(212,149,117,0.06);color:var(--on2)">
        <span class="ph-tag" style="background:transparent;color:var(--acc3);border-color:var(--acc3)">강사 작성 영역</span>
        본 회차 PART별 산출물을 1줄씩.
      </div>
    </div>
    <div style="background:var(--dk2);padding:24px 28px">
      <div style="font-family:var(--mono);font-size:12px;color:var(--acc3);letter-spacing:2.5px;font-weight:700;margin-bottom:14px">TAKEAWAY · 가져갈 것</div>
      <div class="ph" style="border-color:rgba(212,149,117,0.5);background:rgba(212,149,117,0.06);color:var(--on2)">
        <span class="ph-tag" style="background:transparent;color:var(--acc3);border-color:var(--acc3)">강사 작성 영역</span>
        다음 주차까지 거점리더가 자기 부서에서 시도해볼 1~2가지.
      </div>
    </div>
    <div style="background:var(--dk2);padding:24px 28px">
      <div style="font-family:var(--mono);font-size:12px;color:var(--acc3);letter-spacing:2.5px;font-weight:700;margin-bottom:14px">NEXT · 다음 회차</div>
      <div class="ph" style="border-color:rgba(212,149,117,0.5);background:rgba(212,149,117,0.06);color:var(--on2)">
        <span class="ph-tag" style="background:transparent;color:var(--acc3);border-color:var(--acc3)">강사 작성 영역</span>
        {next_text}
      </div>
    </div>
  </div>

  <div class="fbar"><div class="fbar-l"><span class="fbar-label">MODULE</span><span class="fbar-title">{num:02d} · {title}</span></div><div class="fbar-r"><span class="fbar-label">PAGE</span><span class="fbar-title">{page_no:03d} / {total_pages:03d}</span></div></div>
</div></div>
"""


def build_session(meta: dict) -> str:
    num = meta["num"]
    title = meta["title"]
    subtitle = meta["subtitle"]
    parts = meta["parts"]

    # 페이지 수 계산: cover + agenda + (3 × parts) + closing
    total_pages = 2 + len(parts) * 3 + 1

    out = HEAD_TEMPLATE.format(num=num, title=title)
    out += cover_slide(num, title, subtitle, parts, total_pages)
    out += agenda_slide(num, title, parts, page_no=2, total_pages=total_pages)

    page = 3
    for idx, (kind, ptitle, psub) in enumerate(parts, start=1):
        out += part_divider_slide(num, title, idx, kind, ptitle, psub, page, total_pages); page += 1
        out += theory_slide(num, title, idx, kind, ptitle, psub, page, total_pages); page += 1
        out += practice_slide(num, title, idx, kind, ptitle, psub, page, total_pages); page += 1

    out += closing_slide(num, title, page, total_pages)
    out += FOOTER_SCRIPT
    return out


def main():
    for meta in SESSIONS:
        num = meta["num"]
        path = ROOT / f"session-{num:02d}-v2.html"
        path.write_text(build_session(meta), encoding="utf-8")
        print(f"  ✓ wrote {path.name}  ({path.stat().st_size:,} bytes)")
    print(f"\n총 {len(SESSIONS)}개 v2 골격 생성 완료.")


if __name__ == "__main__":
    main()
