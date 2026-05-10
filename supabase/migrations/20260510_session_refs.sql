-- ============================================================
-- session_refs · 교안 목록 모달의 동적 참고자료 메타 테이블
-- + Storage 버킷 session-refs (public read, auth write/delete)
-- ============================================================

-- 1) 메타 테이블
create table if not exists public.session_refs (
  id bigserial primary key,
  session_num int not null,
  label text not null,
  filename text not null,
  url text not null,
  content_type text,
  size bigint,
  description text,
  created_at timestamptz default now(),
  created_by text
);

create index if not exists session_refs_session_num_idx
  on public.session_refs (session_num, created_at desc);

-- 2) RLS — 공개 read, 인증된 사용자만 write/delete
alter table public.session_refs enable row level security;

drop policy if exists session_refs_public_read on public.session_refs;
create policy session_refs_public_read
  on public.session_refs for select
  to anon, authenticated
  using (true);

drop policy if exists session_refs_auth_insert on public.session_refs;
create policy session_refs_auth_insert
  on public.session_refs for insert
  to authenticated
  with check (true);

drop policy if exists session_refs_auth_delete on public.session_refs;
create policy session_refs_auth_delete
  on public.session_refs for delete
  to authenticated
  using (true);

-- 3) Storage 버킷 (이미 있으면 건너뜀)
insert into storage.buckets (id, name, public)
values ('session-refs', 'session-refs', true)
on conflict (id) do update set public = excluded.public;

-- 4) Storage RLS — 공개 read, 인증된 사용자만 write/delete
drop policy if exists "session_refs_public_download" on storage.objects;
create policy "session_refs_public_download"
  on storage.objects for select
  to anon, authenticated
  using (bucket_id = 'session-refs');

drop policy if exists "session_refs_auth_upload" on storage.objects;
create policy "session_refs_auth_upload"
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'session-refs');

drop policy if exists "session_refs_auth_update" on storage.objects;
create policy "session_refs_auth_update"
  on storage.objects for update
  to authenticated
  using (bucket_id = 'session-refs');

drop policy if exists "session_refs_auth_delete" on storage.objects;
create policy "session_refs_auth_delete"
  on storage.objects for delete
  to authenticated
  using (bucket_id = 'session-refs');
