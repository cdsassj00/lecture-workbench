#!/usr/bin/env python3
"""
Lecture Workbench · Supabase 마이그레이션 스크립트
사용법:
  python migrate.py schema      # schema.sql 적용 (idempotent)
  python migrate.py seed        # 8개 정적 HTML → DB 시드 (upsert)
  python migrate.py user        # editor@workbench.local 계정 생성/확인
  python migrate.py all         # schema → user → seed 순차 실행
  python migrate.py status      # 현재 DB 상태 출력 (slides·revisions·users)
  python migrate.py reseed N    # 특정 회차(N=1~8)만 재시드

비밀키는 _supabase.local.json (gitignore됨)에서 읽음.
"""
import json, re, os, sys, io, urllib.request, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
CONF = json.load(open(os.path.join(BASE, "_supabase.local.json"), encoding="utf-8"))
URL = CONF["project_url"]
REF = CONF["project_ref"]
ANON = CONF["anon_key"]
SR = CONF["service_role_jwt"]
SBP = CONF["personal_access_token"]
EDITOR_EMAIL = CONF["shared_editor_email"]

H_REST_SR = {"apikey": SR, "Authorization": f"Bearer {SR}", "Content-Type": "application/json"}
H_MGMT = {"Authorization": f"Bearer {SBP}", "Content-Type": "application/json"}

def http(method, url, headers, body=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")

def cmd_schema():
    """schema.sql을 Management API로 실행. CREATE IF NOT EXISTS로 idempotent."""
    sql = open(os.path.join(BASE, "schema.sql"), encoding="utf-8").read()
    code, body = http("POST", f"https://api.supabase.com/v1/projects/{REF}/database/query",
                      H_MGMT, {"query": sql})
    if 200 <= code < 300:
        print(f"[schema] OK ({code})")
    else:
        print(f"[schema] FAILED ({code}): {body[:300]}")
        sys.exit(1)

def cmd_user():
    """editor@workbench.local 계정 확인·생성."""
    # Try create
    pwd = "1111"
    code, body = http("POST", f"{URL}/auth/v1/admin/users", H_REST_SR,
                      {"email": EDITOR_EMAIL, "password": pwd, "email_confirm": True})
    if 200 <= code < 300:
        print(f"[user] CREATED {EDITOR_EMAIL} (password={pwd})")
    elif "already" in body.lower() or code == 422:
        print(f"[user] already exists: {EDITOR_EMAIL}")
    else:
        print(f"[user] FAILED ({code}): {body[:300]}")

def parse_session(num, path):
    html = open(path, encoding="utf-8").read()
    m = re.search(r"<title>([^<]*)</title>", html)
    title = m.group(1).strip() if m else f"Session {num}"
    m = re.search(r"<style>([\s\S]*?)</style>", html)
    css = m.group(1) if m else ""
    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    js = scripts[-1] if scripts else ""
    stages = []
    i = 0
    while True:
        start = html.find('<div class="stage">', i)
        if start < 0:
            break
        depth = 0
        j = start
        end = -1
        while j < len(html):
            if html[j:j+5] == "<div ":
                depth += 1; j += 5
            elif html[j:j+4] == "<div":
                depth += 1; j += 4
            elif html[j:j+6] == "</div>":
                depth -= 1; j += 6
                if depth == 0:
                    end = j; break
            else:
                j += 1
        if end < 0:
            break
        outer = html[start:end]
        inner = outer[len('<div class="stage">'):-len('</div>')]
        dm = re.search(r'<div class="slide"[^>]*data-title="([^"]*)"', inner)
        data_title = dm.group(1) if dm else f"Slide {len(stages)+1}"
        stages.append({"data_title": data_title, "html": inner})
        i = end
    return title, css, js, stages

def upsert(table, rows, on_conflict):
    headers = {**H_REST_SR, "Prefer": "resolution=merge-duplicates,return=minimal"}
    code, body = http("POST", f"{URL}/rest/v1/{table}?on_conflict={on_conflict}",
                      headers, rows)
    return code, body

def cmd_seed(only_session=None):
    """정적 HTML → DB upsert. only_session=N (1~8)이면 그것만."""
    total = 0
    for num in range(1, 9):
        if only_session and num != only_session:
            continue
        path = os.path.join(BASE, f"session-{num:02d}-complete.html")
        if not os.path.exists(path):
            print(f"[seed] Session {num} file not found, skip")
            continue
        title, css, js, stages = parse_session(num, path)
        # session_meta
        code, body = upsert("session_meta",
                            [{"session_num": num, "title": title, "css": css, "js": js}],
                            "session_num")
        if code >= 300:
            print(f"[seed] Session {num} meta FAILED ({code}): {body[:200]}")
            continue
        # slides
        rows = [{"session_num": num, "slide_idx": i, "data_title": s["data_title"],
                 "html": s["html"], "updated_by": "migration"}
                for i, s in enumerate(stages)]
        code, body = upsert("slides", rows, "session_num,slide_idx")
        if code >= 300:
            print(f"[seed] Session {num} slides FAILED ({code}): {body[:200]}")
            continue
        total += len(rows)
        print(f"[seed] Session {num}: {len(rows)} slides upserted ({title[:40]}...)")
    print(f"[seed] DONE — {total} slides total")

def cmd_status():
    """현재 DB 상태."""
    # slides count by session
    code, body = http("GET", f"{URL}/rest/v1/slides?select=session_num",
                      {"apikey": SR, "Authorization": f"Bearer {SR}"})
    if 200 <= code < 300:
        rows = json.loads(body)
        from collections import Counter
        c = Counter(r["session_num"] for r in rows)
        print("slides per session:")
        for k in sorted(c):
            print(f"  Session {k}: {c[k]} slides")
        print(f"  TOTAL slides: {sum(c.values())}")
    else:
        print(f"slides query failed: {code} {body[:200]}")
    # revisions count
    code, body = http("GET", f"{URL}/rest/v1/revisions?select=id",
                      {"apikey": SR, "Authorization": f"Bearer {SR}"})
    if 200 <= code < 300:
        rows = json.loads(body)
        print(f"revisions: {len(rows)} entries")
    # users
    code, body = http("GET", f"{URL}/auth/v1/admin/users", H_REST_SR)
    if 200 <= code < 300:
        users = json.loads(body).get("users", [])
        print(f"auth users: {len(users)}")
        for u in users:
            print(f"  {u.get('email')} (confirmed={bool(u.get('email_confirmed_at'))})")

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "schema":
        cmd_schema()
    elif cmd == "user":
        cmd_user()
    elif cmd == "seed":
        cmd_seed()
    elif cmd == "reseed" and len(sys.argv) >= 3:
        cmd_seed(only_session=int(sys.argv[2]))
    elif cmd == "all":
        cmd_schema(); cmd_user(); cmd_seed()
    elif cmd == "status":
        cmd_status()
    else:
        print(__doc__); sys.exit(1)

if __name__ == "__main__":
    main()
