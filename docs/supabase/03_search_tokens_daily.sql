-- SimilarSounds search tokens, version 2 (run 11 Oct 2026)
-- * Each device: 3 free searches (once).
-- * Signed in: 2 more. When they're used, a 24-hour timer starts; when it ends, 2 more.
-- * Extra accounts don't help: account searches are also counted per device, so a second account
--   on the same device shares the first one's 2 searches and timer.
-- * Searching the same track again within a day is free. Subscribers are unlimited.

alter table public.token_usage add column if not exists reset_at timestamptz;

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
  if u is not null and d_left + acct_left = 0 then
    r_at := case when u_used >= acct_free then u_reset else a_reset end;
  end if;
  return jsonb_build_object(
    'allowed', true, 'subscribed', subscribed, 'signed_in', u is not null,
    'left', case when subscribed then null else d_left + acct_left end,
    'stage', case when subscribed then 'subscribed' when u is null then 'anon' else 'account' end,
    'reset_at', r_at);
end;
$$;

revoke all on function public.search_tokens(uuid, text, bigint, boolean) from public;
grant execute on function public.search_tokens(uuid, text, bigint, boolean) to anon, authenticated;
