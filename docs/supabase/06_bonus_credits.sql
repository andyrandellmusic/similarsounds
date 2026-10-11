-- Bonus credits (run 11 Oct 2026): extra searches SimilarSounds gives an account by hand.
-- They're used after the free ones, never reset, and only change through SQL here.
create table if not exists public.token_bonus (
  user_id uuid primary key references auth.users(id) on delete cascade,
  credits int not null default 0 check (credits >= 0),
  note text,
  updated_at timestamptz not null default now()
);
alter table public.token_bonus enable row level security;

create or replace function public.search_tokens(p_device uuid, p_ip text, p_seed bigint, p_consume boolean)
returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  uid uuid := auth.uid();
  d text := 'd:' || p_device::text;                 -- this device's 3 free searches
  a text := 'a:' || p_device::text;                 -- account searches used on this device (any account)
  u text := case when uid is null then null else 'u:' || uid::text end;
  anon_free constant int := 3;
  acct_free constant int := 2;
  ip_cap constant int := 6;
  d_used int; u_used int := 0; a_used int := 0; ip_used int;
  u_reset timestamptz; a_reset timestamptz;
  subscribed boolean := false;
  d_left int; acct_left int := 0; r_at timestamptz;
  b_left int := 0;                                   -- bonus credits given by SimilarSounds
begin
  if length(coalesce(p_ip, '')) > 128 then raise exception 'bad ip'; end if;
  if uid is not null then
    select exists (select 1 from public.subscriptions s where s.user_id = uid
                   and s.status in ('active', 'trialing')
                   and (s.current_period_end is null or s.current_period_end > now()))
      into subscribed;
  end if;

  -- a finished 24-hour wait gives 2 more searches
  update public.token_usage set used = 0, reset_at = null, updated_at = now()
    where owner in (a, coalesce(u, '')) and reset_at is not null and reset_at <= now();

  if p_consume then
    insert into public.token_usage(owner) values (d) on conflict do nothing;
    if u is not null then
      insert into public.token_usage(owner) values (u) on conflict do nothing;
      insert into public.token_usage(owner) values (a) on conflict do nothing;
    end if;
  end if;
  d_used := coalesce((select used from public.token_usage where owner = d), 0);
  if u is not null then
    select coalesce(used, 0), reset_at into u_used, u_reset from public.token_usage where owner = u;
    select coalesce(used, 0), reset_at into a_used, a_reset from public.token_usage where owner = a;
    u_used := coalesce(u_used, 0); a_used := coalesce(a_used, 0);
  end if;
  select coalesce((select used from public.token_ip where ip_hash = p_ip and day = current_date), 0) into ip_used;
  if uid is not null then
    b_left := coalesce((select credits from public.token_bonus where user_id = uid), 0);
  end if;

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
    elsif u is not null and u_used < acct_free and a_used < acct_free then
      u_used := u_used + 1; a_used := a_used + 1;
      update public.token_usage set used = u_used, updated_at = now(),
        reset_at = case when u_used >= acct_free then now() + interval '24 hours' else reset_at end
        where owner = u;
      update public.token_usage set used = a_used, updated_at = now(),
        reset_at = case when a_used >= acct_free then now() + interval '24 hours' else reset_at end
        where owner = a;
      select reset_at into u_reset from public.token_usage where owner = u;
      select reset_at into a_reset from public.token_usage where owner = a;
      insert into public.token_seeds(owner, seed) values (u, p_seed)
        on conflict (owner, seed) do update set at = now();
    elsif u is not null and b_left > 0 then
      update public.token_bonus set credits = credits - 1, updated_at = now() where user_id = uid;
      b_left := b_left - 1;
      insert into public.token_seeds(owner, seed) values (u, p_seed)
        on conflict (owner, seed) do update set at = now();
    else
      r_at := case when u is null then null
                       when u_used >= acct_free then u_reset else a_reset end;
      return jsonb_build_object('allowed', false, 'subscribed', false, 'signed_in', u is not null,
                                'left', 0, 'stage', case when u is null then 'anon' else 'account' end,
                                'reset_at', r_at);
    end if;
  end if;

  d_left := greatest(anon_free - d_used, 0);
  if u is null then d_left := least(d_left, greatest(ip_cap - ip_used, 0)); end if;
  if u is not null then acct_left := greatest(least(acct_free - u_used, acct_free - a_used), 0); end if;
  if u is not null and d_left + acct_left + b_left = 0 then
    r_at := case when u_used >= acct_free then u_reset else a_reset end;
  end if;
  return jsonb_build_object(
    'allowed', true, 'subscribed', subscribed, 'signed_in', u is not null,
    'left', case when subscribed then null else d_left + acct_left + b_left end,
    'stage', case when subscribed then 'subscribed' when u is null then 'anon' else 'account' end,
    'reset_at', r_at);
end;
$$;

revoke all on function public.search_tokens(uuid, text, bigint, boolean) from public;
grant execute on function public.search_tokens(uuid, text, bigint, boolean) to anon, authenticated;

-- Give hanky3@live.co.uk 50 bonus credits (Boss, 11 Oct 2026)
insert into public.token_bonus (user_id, credits, note)
select id, 50, 'gift from Boss' from auth.users where lower(email) = 'hanky3@live.co.uk'
on conflict (user_id) do update set credits = public.token_bonus.credits + 50, note = excluded.note, updated_at = now();

select u.email, b.credits from public.token_bonus b join auth.users u on u.id = b.user_id;
