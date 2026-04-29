// Lecture Workbench · AI Rewrite Edge Function
// Anthropic Claude Sonnet 4.5로 슬라이드 텍스트 수정안 생성
// JWT 검증 필수 (인증된 강사만 호출 가능)

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MODEL = "claude-sonnet-4-5-20250929";

const SYSTEM_PROMPT = `당신은 한국 공공 행정 강의안(2026 행정안전부 AI·데이터기반행정 전문인재 양성과정)의 슬라이드 텍스트 편집자입니다.

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
- 다른 설명·인사·코드블록·따옴표 없이 수정된 텍스트만 출력`;

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
    const { current_text, instruction, context_hint, max_tokens } = await req.json();

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

    const claudeResp = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: max_tokens ?? 2048,
        system: SYSTEM_PROMPT,
        messages: [{ role: "user", content: userMsg }],
      }),
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
