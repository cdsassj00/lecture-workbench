// Lecture Workbench · AI Rewrite Edge Function
// Anthropic Claude Sonnet 4.5로 슬라이드 텍스트 수정안 생성
// JWT 검증 필수 (인증된 강사만 호출 가능)

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MODEL = "claude-sonnet-4-5-20250929";

const SYSTEM_PROMPT = `당신은 한국 공공 행정 강의안 「AI 챔피언 고급 과정 · AI 데이터분석 전문인재 과정」의 슬라이드 텍스트 편집자입니다.

작성 원칙:
- 한국어 존댓말("~합니다"), 강의 voice
- 비유·은유·메거진 어조 금지 ("~의 무기는", "여섯 칸을 채우는 설계자", "재료 창고" 류 X)
- 추상적 역할 라벨 금지 (기획자·아키텍트·코치·확산자 류)
- 구체적 도구명·버전·숫자·시간·파일명 우선
- 첫째·둘째·셋째·넷째 열거 권장 (1)2)3) ①②③ 금지)
- vision casting / glamour 카피 금지
- 짧은 문장 권장, 정보 밀도 높게

출력 형식 규칙:
- 사용자가 보낸 원본이 HTML 태그를 포함하면 동일한 태그 구조 유지하고 텍스트 노드만 수정
- 사용자가 보낸 원본이 평문이면 평문으로 출력
- 다른 설명·인사·코드블록·따옴표 없이 수정된 텍스트만 출력

웹검색 도구 사용 시 추가 규칙 (use_web_search=true일 때만):
- "최신/2026/올해/이번/현재" 등 시점성 있는 정보 요청에만 검색 활용
- 검색 결과의 핵심 사실(도구명·버전·숫자·일정·발표일)을 본문에 자연스럽게 녹이기
- [1], [n] 같은 인라인 인용 표시 절대 출력하지 말 것
- URL·"출처:" 라벨도 출력 금지 — 강의안 본문은 깔끔해야 함
- 검색해도 확실하지 않은 정보는 추가하지 않음 (잘못된 사실 기재 금지)`;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  try {
    const { current_text, instruction, context_hint, max_tokens, stream, useWebSearch } = await req.json();

    if (!current_text || typeof current_text !== "string") {
      return new Response(JSON.stringify({ error: "current_text required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }
    if (!instruction || typeof instruction !== "string") {
      return new Response(JSON.stringify({ error: "instruction required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const apiKey = Deno.env.get("ANTHROPIC_API_KEY");
    if (!apiKey) {
      return new Response(
        JSON.stringify({ error: "ANTHROPIC_API_KEY secret not configured" }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const userParts = [
      `[원본 텍스트]\n${current_text}`,
      context_hint ? `[슬라이드 맥락]\n${context_hint}` : "",
      `[수정 지시]\n${instruction}`,
      `위 원본을 지시에 따라 수정해 주세요. 다른 설명·인사·코드블록 없이 수정된 텍스트만 그대로 출력하세요.`,
    ].filter(Boolean);
    const userMsg = userParts.join("\n\n");

    const wantStream = stream === true;
    const wantSearch = useWebSearch === true;

    const requestBody: Record<string, unknown> = {
      model: MODEL,
      max_tokens: max_tokens ?? 2048,
      system: SYSTEM_PROMPT,
      stream: wantStream,
      messages: [{ role: "user", content: userMsg }],
    };
    if (wantSearch) {
      // Anthropic 공식 웹검색 server-tool — 모델이 필요할 때만 자동 호출
      requestBody.tools = [
        { type: "web_search_20250305", name: "web_search", max_uses: 3 },
      ];
    }

    const claudeResp = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!claudeResp.ok) {
      const errBody = await claudeResp.text();
      return new Response(
        JSON.stringify({
          error: "Anthropic API error",
          status: claudeResp.status,
          details: errBody.substring(0, 500),
        }),
        {
          status: 502,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    if (wantStream) {
      // Anthropic의 SSE 스트림을 그대로 클라이언트로 패스스루
      return new Response(claudeResp.body, {
        headers: {
          ...corsHeaders,
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
          "X-Accel-Buffering": "no",
        },
      });
    }

    const data = await claudeResp.json();
    const rewritten =
      (data.content && data.content[0] && data.content[0].text) || "";

    return new Response(
      JSON.stringify({
        rewritten: rewritten.trim(),
        usage: data.usage ?? null,
        model: MODEL,
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (e) {
    return new Response(
      JSON.stringify({ error: "Function exception", details: String(e) }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
