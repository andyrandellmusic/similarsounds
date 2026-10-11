-- SimilarSounds: each signed-in person's saved set and recent searches (run 11 Oct 2026)
create table if not exists public.user_data (
  user_id uuid primary key references auth.users(id) on delete cascade,
  set_tracks jsonb not null default '[]'::jsonb,
  recent jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.user_data enable row level security;
create policy "read own data" on public.user_data for select to authenticated using ((select auth.uid()) = user_id);
create policy "add own data" on public.user_data for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "change own data" on public.user_data for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "remove own data" on public.user_data for delete to authenticated using ((select auth.uid()) = user_id);
create or replace function public.delete_my_account() returns void
language plpgsql security definer set search_path = '' as $$
begin
  delete from auth.users where id = auth.uid();
end;
$$;
revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;
