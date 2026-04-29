-- ==============================================================
-- Lecture Workbench · Supabase Schema
-- Project: uykrzkhnlxozsbllvffk.supabase.co
-- 실행 방법: Supabase 대시보드 → SQL Editor → New query → 전체 붙여넣기 → Run
-- ==============================================================

-- 1. SLIDES — 슬라이드 최신본
create table if not exists public.slides (
  id bigserial primary key,
  session_num int not null check (session_num between 1 and 8),
  slide_idx int not null,
  data_title text,
  html text not null,
  updated_at timestamptz not null default now(),
  updated_by text,
  unique (session_num, slide_idx)
);

create index if not exists slides_session_order_idx
  on public.slides (session_num, slide_idx);

-- 2. REVISIONS — 수정 이력 (auto-snapshot)
create table if not exists public.revisions (
  id bigserial primary key,
  session_num int not null,
  slide_idx int not null,
  html text not null,
  changed_at timestamptz not null default now(),
  changed_by text,
  note text
);

create index if not exists revisions_session_history_idx
  on public.revisions (session_num, slide_idx, changed_at desc);

-- 3. SESSION_META — 회차별 메타 (제목·CSS·JS)
create table if not exists public.session_meta (
  session_num int primary key check (session_num between 1 and 8),
  title text,
  css text,
  js text,
  updated_at timestamptz not null default now()
);

-- 4. RLS — 익명: 읽기만 / 인증: 모두
alter table public.slides enable row level security;
alter table public.revisions enable row level security;
alter table public.session_meta enable row level security;

-- 익명·인증 모두 읽기 가능 (수강생은 익명으로 열람)
drop policy if exists "public read slides" on public.slides;
create policy "public read slides"
  on public.slides for select
  using (true);

drop policy if exists "public read revisions" on public.revisions;
create policy "public read revisions"
  on public.revisions for select
  using (true);

drop policy if exists "public read meta" on public.session_meta;
create policy "public read meta"
  on public.session_meta for select
  using (true);

-- 인증된 사용자(=강사)만 쓰기·수정·삭제 가능
drop policy if exists "auth write slides" on public.slides;
create policy "auth write slides"
  on public.slides for insert to authenticated
  with check (true);

drop policy if exists "auth update slides" on public.slides;
create policy "auth update slides"
  on public.slides for update to authenticated
  using (true) with check (true);

drop policy if exists "auth delete slides" on public.slides;
create policy "auth delete slides"
  on public.slides for delete to authenticated
  using (true);

drop policy if exists "auth write revisions" on public.revisions;
create policy "auth write revisions"
  on public.revisions for insert to authenticated
  with check (true);

drop policy if exists "auth write meta" on public.session_meta;
create policy "auth write meta"
  on public.session_meta for insert to authenticated
  with check (true);

drop policy if exists "auth update meta" on public.session_meta;
create policy "auth update meta"
  on public.session_meta for update to authenticated
  using (true) with check (true);

-- 5. TRIGGER — slides UPDATE 시 변경 직전 본을 revisions에 자동 저장
create or replace function public.record_slide_revision()
returns trigger
language plpgsql
security definer
as $$
begin
  if old.html is distinct from new.html then
    insert into public.revisions
      (session_num, slide_idx, html, changed_at, changed_by, note)
    values
      (old.session_num, old.slide_idx, old.html, old.updated_at, old.updated_by, 'auto-snapshot');
  end if;
  return new;
end;
$$;

drop trigger if exists slide_history_trigger on public.slides;
create trigger slide_history_trigger
  before update on public.slides
  for each row
  execute function public.record_slide_revision();

-- 6. 검증
-- select count(*) from public.slides;        -- 0 (시드 전)
-- select count(*) from public.revisions;     -- 0
-- select count(*) from public.session_meta;  -- 0

-- ==============================================================
-- 끝. 다음 단계:
-- A. Authentication → Users → Add user 7회 (이메일/비번 직접 입력)
--    이메일: lec1@workbench.local ~ lec7@workbench.local
--    "Auto Confirm User" 체크 필수
--    비밀번호: 강사 7명 각자 비번 (운영자가 정해 강사에게 전달)
-- B. 시드: 편집기 페이지에서 "DB로 마이그레이션" 1회 실행 (제가 따로 안내)
-- ==============================================================
