-- SimilarSounds search tokens
-- Every visitor's device gets 3 free searches; a free account adds 2 more; a subscription is unlimited.
-- Searching the same track again within a day (filters, more results) is free.
-- Only the search_tokens() function below can read or change these tables.

create table if not exists public.token_usage (
  owner text primary key,                       -- 'd:<device id>' or 'u:<user id>'
  used int not null default 0,
  updated_at timestamptz not null default now()
);

create table if not exists public.token_seeds (
  owner text not null,
  seed bigint not null,                         -- the Deezer id of the track searched
  at timestamptz not null default now(),
  primary key (owner, seed)
);

-- Free searches without an account are also capped per network per day (hashed IP, never the IP itself)
create table if not exists public.token_ip (
  ip_hash text not null,
  day date not null default current_date,
  used int not null default 0,
  primary key (ip_hash, day)
);

-- Filled in by the payment provider later
create table if not exists public.subscriptions (
  user_id uuid primary key references auth.users(id) on delete cascade,
  status text not null,
  current_period_end timestamptz,
  customer_ref text,
  updated_at timestamptz not null default now()
);

alter table public.token_usage enable row level security;
alter table public.token_seeds enable row level security;
alter table public.token_ip enable row level security;
alter table public.subscriptions enable row level security;
drop policy if exists "read own subscription" on public.subscriptions;
create policy "read own subscription" on public.subscriptions for select to authenticated
  using ((select auth.uid()) = user_id);

create or replace function public.search_tokens(p_device uuid, p_ip text, p_seed bigint, p_consume boolean)
returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  uid uuid := auth.uid();
  d text := 'd:' || p_device::text;
  u text := case when uid is null then null else 'u:' || uid::text end;
  anon_free constant int := 3;
  acct_free constant int := 2;
  ip_cap constant int := 6;
  d_used int;
  u_used int := 0;
  ip_used int;
  subscribed boolean := false;
  d_left int;
  u_left int;
begin
  if length(coalesce(p_ip, '')) > 128 then raise exception 'bad ip'; end if;
  if uid is not null then
    select exists (select 1 from public.subscriptions s where s.user_id = uid
                   and s.status in ('active', 'trialing')
                   and (s.current_period_end is null or s.current_period_end > now()))
      into subscribed;
  end if;

  if p_consume then insert into public.token_usage(owner) values (d) on conflict do nothing; end if;
  d_used := coalesce((select used from public.token_usage where owner = d), 0);
  if u is not null then
    if p_consume then insert into public.token_usage(owner) values (u) on conflict do nothing; end if;
    u_used := coalesce((select used from public.token_usage where owner = u), 0);
  end if;
  select coalesce((select used from public.token_ip where ip_hash = p_ip and day = current_date), 0) into ip_used;

  if p_consume and not subscribed and p_seed is not null then
    if exists (select 1 from public.token_seeds where seed = p_seed and owner in (d, coalesce(u, ''))
               and at > now() - interval '1 day') then
      null;   -- same track again today: free
    elsif d_used < anon_free and (u is not null or ip_used < ip_cap) then
      update public.token_usage set used = used + 1, updated_at = now() where owner = d;
      d_used := d_used + 1;
      insert into public.token_seeds(owner, seed) values (d, p_seed)
        on conflict (owner, seed) do update set at = now();
      if u is null then
        insert into public.token_ip(ip_hash, used) values (p_ip, 1)
          on conflict (ip_hash, day) do update set used = public.token_ip.used + 1;
        ip_used := ip_used + 1;
      end if;
    elsif u is not null and u_used < acct_free then
      update public.token_usage set used = used + 1, updated_at = now() where owner = u;
      u_used := u_used + 1;
      insert into public.token_seeds(owner, seed) values (u, p_seed)
        on conflict (owner, seed) do update set at = now();
    else
      return jsonb_build_object('allowed', false, 'subscribed', false, 'signed_in', u is not null,
                                'left', 0, 'stage', case when u is null then 'anon' else 'account' end);
    end if;
  end if;

  d_left := greatest(anon_free - d_used, 0);
  if u is null then d_left := least(d_left, greatest(ip_cap - ip_used, 0)); end if;
  u_left := case when u is null then 0 else greatest(acct_free - u_used, 0) end;
  return jsonb_build_object(
    'allowed', true, 'subscribed', subscribed, 'signed_in', u is not null,
    'left', case when subscribed then null else d_left + u_left end,
    'stage', case when subscribed then 'subscribed' when u is null then 'anon' else 'account' end);
end;
$$;

revoke all on function public.search_tokens(uuid, text, bigint, boolean) from public;
grant execute on function public.search_tokens(uuid, text, bigint, boolean) to anon, authenticated;
