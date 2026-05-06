#!/usr/bin/env python3
"""
세션 1 slide_idx 67 (페이지 68) 재작성:
- 표 레이아웃을 4x2 카드 그리드로 통일 (slide 66과 동일 디자인)
- 각 카드: SESSION 번호 + 분류명(환경/모델/...) + 핵심 도구 리스트
- hbar 보장
"""
import json, urllib.request, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CONF = json.load(open('_supabase.local.json', encoding='utf-8'))
URL = CONF['project_url']; SR = CONF['service_role_jwt']
H = {'apikey':SR, 'Authorization':f'Bearer {SR}', 'Content-Type':'application/json'}

# 카드 헬퍼
def card(num, cat, tools):
    return (
      '<div style="border:1px solid var(--ln);background:var(--bg2);padding:14px 16px">'
      f'<div style="font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:2px;font-weight:700;margin-bottom:6px">SESSION {num}</div>'
      f'<div style="font-family:var(--serif);font-size:17px;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:6px">{cat}</div>'
      f'<div style="font-size:11.5px;color:var(--ink2);line-height:1.55">{tools}</div>'
      '</div>'
    )

CARDS = (
    card('01', '환경 세팅',           'Git · GitHub · WSL · Node.js · Python · VS Code · Vercel · Netlify · Power BI Desktop')
  + card('02', '프론티어 모델',        'Claude · GPT · Gemini · Grok · Llama · Qwen · Mistral · NotebookLM · Ollama (로컬 sLLM)')
  + card('03', '프롬프트·워크플로우',   '메타 프롬프트 · 시스템 프롬프트 · 6 워크플로우 타입 · Make · Zapier · n8n')
  + card('04', '데이터 분석',          'Python · pandas · NumPy · Plotly · Streamlit · Jupyter · 공공데이터포털 API')
  + card('05', '업무 자동화',          'Python · HWP · Excel VBA · Outlook automation · Node.js · PyInstaller · xlam · Ollama API')
  + card('06', '에이전트 도구',        'Claude Code · Codex · OpenCode · Cursor · Antigravity · CLAUDE.md · Skills · Plugins')
  + card('07', 'RAG·웹서비스',         '임베딩 · Chroma · pgvector · 청크 분할 · FastAPI · Flask · Express · Supabase')
  + card('08', 'API · MCP · 통합',     '공공 API(data.go.kr) · MCP 서버 제작 · 멀티 에이전트 협업 · 통합 데모 + 최종 발표')
)

SLIDE_67 = (
'<div class="slide" data-title="Course Tool Stack">'
  '<div class="hbar"><div class="hbar-l">CLOSING · 도구 스택</div><div class="hbar-r"><span style="letter-spacing: 1.5px">AI 챔피언 고급 과정 · Session 01</span></div></div>'
  '<div class="hl">'
    '<div class="hl-kicker">CLOSING · 8회차 핵심 도구·기술 스택</div>'
    '<div class="hl-title">회차별 다루는 도구와 산출물</div>'
    '<div class="hl-sub">8회차는 단계적으로 도구·기술을 누적합니다. 1~2차시는 환경과 모델 선택. 3~5차시는 프롬프트·어시스트 코딩 도구. 6~8차시는 에이전트·RAG·API·MCP 풀스택. 각 회차 끝에 코드·문서·시제품 형태의 산출물이 GitHub Org에 누적됩니다.</div>'
    '<div class="hl-bar"></div>'
  '</div>'
  '<div class="hl-rule"></div>'
  '<div class="bd" style="position:absolute;left:60px;right:60px;top:280px;bottom:60px;display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:1fr 1fr;gap:14px">'
  + CARDS +
  '</div>'
  '<div class="fbar"><div class="fbar-l"><span class="fbar-label">MODULE</span><span class="fbar-title">01 · AI 에이전트 시대의 개막과 공공 구현 지형도</span></div><div class="fbar-r"><span class="fbar-label">PAGE</span><span class="fbar-title">068 / 068</span></div></div>'
'</div>'
)

def main():
    print('=== slide 67 재작성 (표 → 4x2 카드 그리드) ===')
    h_min = {**H, 'Prefer':'return=minimal'}
    data = json.dumps({'html': SLIDE_67}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.67',
        data=data, method='PATCH', headers=h_min
    )
    try:
        with urllib.request.urlopen(req) as r:
            print(f'  ✓ status {r.status}')
    except urllib.error.HTTPError as e:
        print(f'  ✗ {e.code}: {e.read().decode()[:120]}')

if __name__ == '__main__':
    import urllib.error
    main()
