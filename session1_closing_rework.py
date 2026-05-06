#!/usr/bin/env python3
"""
세션 1 CLOSING 재작성:
- slide_idx 66 → "8회차 학습 흐름" (회차별 핵심 토픽)
- slide_idx 67 → "8회차 핵심 도구·기술 스택" (회차별 도구·산출물)
- slide_idx 68 → 삭제 (오늘 남겨야 할 5가지 — 비유적 요약 제거)
모두 비유·은유·캔버스 6칸·선언서 진화 같은 메타포 표현 제거. 사실 진술만.
"""
import json, urllib.request, urllib.error, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CONF = json.load(open('_supabase.local.json', encoding='utf-8'))
URL = CONF['project_url']; SR = CONF['service_role_jwt']
H = {'apikey':SR, 'Authorization':f'Bearer {SR}', 'Content-Type':'application/json'}

def http(method, url, body=None):
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=H, method=method)
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.read().decode('utf-8')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8')

# ============================================================
# slide 66 — 8회차 학습 흐름 (회차별 핵심 토픽)
# ============================================================
SLIDE_66 = '''<div class="slide" data-title="Course Flow Overview">
  <div class="hbar"><div class="hbar-l">CLOSING · 8회차 흐름</div><div class="hbar-r"><span style="letter-spacing: 1.5px">AI 챔피언 고급 과정 · Session 01</span></div></div>
  <div class="hl">
    <div class="hl-kicker">CLOSING · 8회차 학습 흐름 — 회차별 핵심 토픽</div>
    <div class="hl-title">8회차에 걸쳐 다루는 기술 흐름</div>
    <div class="hl-sub">1차시는 AI 트렌드·9가지 구현 유형·환경 세팅. 2~3차시는 프론티어 모델 비교와 프롬프트·워크플로우 설계. 4~5차시는 AI 어시스트 기반 데이터 분석과 업무 자동화. 6~8차시는 에이전트 도구·RAG·API/MCP 풀스택까지. 매 회차 산출물이 다음 회차로 누적됩니다.</div>
    <div class="hl-bar"></div>
  </div>
  <div class="hl-rule"></div>
  <div class="bd" style="position:absolute;left:60px;right:60px;top:280px;bottom:60px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px">
    <div style="border:1px solid var(--ln);background:var(--bg2);padding:14px 16px"><div style="font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:2px;font-weight:700;margin-bottom:6px">SESSION 01</div><div style="font-family:var(--serif);font-size:17px;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:6px">AI 트렌드와 환경 세팅</div><div style="font-size:11.5px;color:var(--ink2);line-height:1.55">AI·NLP 진화사 · NanoGPT Q·K·V · 프론티어 5종 · 9가지 구현 유형 · GitHub·Git·WSL·Node·Python 환경 세팅</div></div>
    <div style="border:1px solid var(--ln);background:var(--bg2);padding:14px 16px"><div style="font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:2px;font-weight:700;margin-bottom:6px">SESSION 02</div><div style="font-family:var(--serif);font-size:17px;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:6px">프론티어 모델·AI 도구 50선</div><div style="font-size:11.5px;color:var(--ink2);line-height:1.55">Claude·GPT·Gemini·Grok·오픈소스 심층. 문서·이미지·영상·음성·검색·데이터 6 카테고리 50개 도구. 로컬 LLM(Ollama) 실습.</div></div>
    <div style="border:1px solid var(--ln);background:var(--bg2);padding:14px 16px"><div style="font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:2px;font-weight:700;margin-bottom:6px">SESSION 03</div><div style="font-family:var(--serif);font-size:17px;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:6px">메타 프롬프트·워크플로우</div><div style="font-size:11.5px;color:var(--ink2);line-height:1.55">메타 프롬프트 라이브러리 · 6가지 워크플로우 타입(체인·라우터·병렬·검증·반복·하이브리드). 회의록·민원답변·보고서 자동화.</div></div>
    <div style="border:1px solid var(--ln);background:var(--bg2);padding:14px 16px"><div style="font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:2px;font-weight:700;margin-bottom:6px">SESSION 04</div><div style="font-family:var(--serif);font-size:17px;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:6px">어시스트 ① 데이터 시각화·분석</div><div style="font-size:11.5px;color:var(--ink2);line-height:1.55">Python·pandas·Plotly로 공공데이터 분석·시각화. 외부망↔내부망 코드 이전 루틴. Streamlit 미니 대시보드.</div></div>
    <div style="border:1px solid var(--ln);background:var(--bg2);padding:14px 16px"><div style="font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:2px;font-weight:700;margin-bottom:6px">SESSION 05</div><div style="font-family:var(--serif);font-size:17px;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:6px">어시스트 ② 업무 자동화·로컬 AI</div><div style="font-size:11.5px;color:var(--ink2);line-height:1.55">Python 반복 업무 자동화 · HWP 일괄 생성 · Excel VBA + Ollama 연동 · Node.js 미니 도구 · PyInstaller로 .exe 패키징.</div></div>
    <div style="border:1px solid var(--ln);background:var(--bg2);padding:14px 16px"><div style="font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:2px;font-weight:700;margin-bottom:6px">SESSION 06</div><div style="font-family:var(--serif);font-size:17px;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:6px">AI 에이전트 도구 마스터리</div><div style="font-size:11.5px;color:var(--ink2);line-height:1.55">Claude Code · Codex · OpenCode · Antigravity · Cursor 도구별 슬래시 명령·CLAUDE.md·권한·MCP. 부서 업무 봇 시제품.</div></div>
    <div style="border:1px solid var(--ln);background:var(--bg2);padding:14px 16px"><div style="font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:2px;font-weight:700;margin-bottom:6px">SESSION 07</div><div style="font-family:var(--serif);font-size:17px;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:6px">RAG 파이프라인·웹서비스</div><div style="font-size:11.5px;color:var(--ink2);line-height:1.55">RAG 4단계(인덱싱·검색·생성·평가) · 임베딩·벡터DB · 사내 매뉴얼 봇 시제품 · 백엔드 결합 웹서비스 1식.</div></div>
    <div style="border:1px solid var(--ln);background:var(--bg2);padding:14px 16px"><div style="font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:2px;font-weight:700;margin-bottom:6px">SESSION 08</div><div style="font-family:var(--serif);font-size:17px;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:6px">API · MCP · 멀티 에이전트</div><div style="font-size:11.5px;color:var(--ink2);line-height:1.55">공공 API 카탈로그 · MCP 서버 자체 제작 · 3개 에이전트 협업 워크플로우 · 통합 데모 + 최종 발표.</div></div>
  </div>
  <div class="fbar"><div class="fbar-l"><span class="fbar-label">MODULE</span><span class="fbar-title">01 · AI 에이전트 시대의 개막과 공공 구현 지형도</span></div><div class="fbar-r"><span class="fbar-label">PAGE</span><span class="fbar-title">067 / 067</span></div></div>
</div>'''

# ============================================================
# slide 67 — 8회차 핵심 도구·기술 스택
# ============================================================
SLIDE_67 = '''<div class="slide" data-title="Course Tool Stack">
  <div class="hbar"><div class="hbar-l">CLOSING · 도구 스택</div><div class="hbar-r"><span style="letter-spacing: 1.5px">AI 챔피언 고급 과정 · Session 01</span></div></div>
  <div class="hl">
    <div class="hl-kicker">CLOSING · 8회차 핵심 도구·기술 스택</div>
    <div class="hl-title">회차별 다루는 도구와 산출물</div>
    <div class="hl-sub">8회차는 단계적으로 도구·기술을 누적합니다. 1~2차시는 환경과 모델 선택. 3~5차시는 프롬프트·어시스트 코딩 도구. 6~8차시는 에이전트·RAG·API·MCP 풀스택. 각 회차 끝에 코드·문서·시제품 형태의 산출물이 GitHub Org에 누적됩니다.</div>
    <div class="hl-bar"></div>
  </div>
  <div class="hl-rule"></div>
  <div class="bd" style="position:absolute;left:60px;right:60px;top:280px;bottom:60px;display:grid;grid-template-columns:1fr 1fr;gap:14px">
    <table class="mtbl" style="width:100%;border-collapse:collapse"><thead><tr><th style="text-align:left;padding:9px 12px;background:var(--bg2);font-family:var(--mono);font-size:11px;letter-spacing:1.5px;color:var(--ink3);font-weight:700;border-bottom:2px solid var(--acc);width:90px">SESSION</th><th style="text-align:left;padding:9px 12px;background:var(--bg2);font-family:var(--mono);font-size:11px;letter-spacing:1.5px;color:var(--ink3);font-weight:700;border-bottom:2px solid var(--acc)">핵심 도구·기술</th></tr></thead><tbody>
      <tr><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-family:var(--serif);font-weight:700;color:var(--acc)">01</td><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-size:12px;color:var(--ink2);line-height:1.55"><b style="color:var(--ink)">환경:</b> Git · GitHub · WSL · Node.js · Python · VS Code · Vercel · Netlify · Power BI Desktop</td></tr>
      <tr><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-family:var(--serif);font-weight:700;color:var(--acc)">02</td><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-size:12px;color:var(--ink2);line-height:1.55"><b style="color:var(--ink)">모델:</b> Claude · GPT · Gemini · Grok · Llama · Qwen · Mistral · NotebookLM · Ollama (로컬 sLLM)</td></tr>
      <tr><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-family:var(--serif);font-weight:700;color:var(--acc)">03</td><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-size:12px;color:var(--ink2);line-height:1.55"><b style="color:var(--ink)">프롬프트:</b> 메타 프롬프트 · 시스템 프롬프트 · 6가지 워크플로우 타입 · Make · Zapier · n8n</td></tr>
      <tr><td style="padding:9px 12px;font-family:var(--serif);font-weight:700;color:var(--acc)">04</td><td style="padding:9px 12px;font-size:12px;color:var(--ink2);line-height:1.55"><b style="color:var(--ink)">분석:</b> Python · pandas · NumPy · Plotly · Streamlit · Jupyter · 공공데이터포털 API</td></tr>
    </tbody></table>
    <table class="mtbl" style="width:100%;border-collapse:collapse"><thead><tr><th style="text-align:left;padding:9px 12px;background:var(--bg2);font-family:var(--mono);font-size:11px;letter-spacing:1.5px;color:var(--ink3);font-weight:700;border-bottom:2px solid var(--acc);width:90px">SESSION</th><th style="text-align:left;padding:9px 12px;background:var(--bg2);font-family:var(--mono);font-size:11px;letter-spacing:1.5px;color:var(--ink3);font-weight:700;border-bottom:2px solid var(--acc)">핵심 도구·기술</th></tr></thead><tbody>
      <tr><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-family:var(--serif);font-weight:700;color:var(--acc)">05</td><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-size:12px;color:var(--ink2);line-height:1.55"><b style="color:var(--ink)">자동화:</b> Python·HWP·Excel VBA · Outlook automation · Node.js · PyInstaller · xlam · Ollama API</td></tr>
      <tr><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-family:var(--serif);font-weight:700;color:var(--acc)">06</td><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-size:12px;color:var(--ink2);line-height:1.55"><b style="color:var(--ink)">에이전트:</b> Claude Code · Codex · OpenCode · Cursor · Antigravity · CLAUDE.md · Skills · Plugins</td></tr>
      <tr><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-family:var(--serif);font-weight:700;color:var(--acc)">07</td><td style="padding:9px 12px;border-bottom:1px solid var(--ln);font-size:12px;color:var(--ink2);line-height:1.55"><b style="color:var(--ink)">RAG:</b> 임베딩 모델 · 벡터DB(Chroma·pgvector) · 청크 분할 · FastAPI · Flask · Express · Supabase</td></tr>
      <tr><td style="padding:9px 12px;font-family:var(--serif);font-weight:700;color:var(--acc)">08</td><td style="padding:9px 12px;font-size:12px;color:var(--ink2);line-height:1.55"><b style="color:var(--ink)">통합:</b> 공공 API(data.go.kr) · MCP 서버 제작 · 멀티 에이전트 협업 · 통합 데모 + 최종 발표</td></tr>
    </tbody></table>
  </div>
  <div class="fbar"><div class="fbar-l"><span class="fbar-label">MODULE</span><span class="fbar-title">01 · AI 에이전트 시대의 개막과 공공 구현 지형도</span></div><div class="fbar-r"><span class="fbar-label">PAGE</span><span class="fbar-title">068 / 067</span></div></div>
</div>'''

# ============================================================
# 메인
# ============================================================
def main():
    print('=== 세션 1 CLOSING 재작성 ===\n')
    h_min = {**H, 'Prefer':'return=minimal'}

    # 백업
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=in.(66,67,68)&select=slide_idx,html&order=slide_idx')
    bk = json.loads(body)
    bk_path = f'session1_closing_backup_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    with open(bk_path, 'w', encoding='utf-8') as f:
        json.dump(bk, f, ensure_ascii=False)
    print(f'1) 백업: {bk_path} ({len(bk)} slides)\n')

    # slide 66 → 8회차 학습 흐름
    code, body = http('PATCH', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.66',
        {'html': SLIDE_66, 'data_title': 'Course Flow Overview'})
    ok = 200 <= code < 300
    print(f'2) slide 66 → "8회차 학습 흐름" — {"✓" if ok else "✗ "+body[:120]}')

    # slide 67 → 8회차 도구 스택
    code, body = http('PATCH', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.67',
        {'html': SLIDE_67, 'data_title': 'Course Tool Stack'})
    ok = 200 <= code < 300
    print(f'3) slide 67 → "8회차 도구 스택" — {"✓" if ok else "✗ "+body[:120]}')

    # slide 68 → 삭제
    code, body = http('DELETE', f'{URL}/rest/v1/slides?session_num=eq.1&slide_idx=eq.68')
    ok = 200 <= code < 300
    print(f'4) slide 68 → 삭제 — {"✓" if ok else "✗ "+body[:120]}')

    # 검증
    code, body = http('GET', f'{URL}/rest/v1/slides?session_num=eq.1&select=slide_idx&order=slide_idx.desc&limit=3')
    rows = json.loads(body)
    print(f'\n검증: 세션 1 마지막 3개 slide_idx = {[r["slide_idx"] for r in rows]} (전: 68, 후: 67)')

if __name__ == '__main__':
    main()
