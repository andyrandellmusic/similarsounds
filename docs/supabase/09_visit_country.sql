-- Where visitors and accounts are (run 28 Oct 2026). Each visit keeps the browser's time zone (e.g. "Europe/London"),
-- never an IP address; the stats page turns time zones into countries. An account keeps the time zone it was first
-- seen in. Safe to run again. Older pages that send only p_device still work (p_tz defaults to null).
alter table public.visits add column if not exists tz text;
create table if not exists public.account_tz (
  user_id uuid primary key references auth.users(id) on delete cascade,
  tz text not null,
  at timestamptz not null default now()
);
alter table public.account_tz enable row level security;

drop function if exists public.log_visit(uuid);
create or replace function public.log_visit(p_device uuid, p_tz text default null) returns void
language plpgsql security definer set search_path = '' as $$
declare z text := nullif(left(coalesce(p_tz, ''), 64), '');
begin
  if exists (select 1 from public.subscriptions where user_id = auth.uid() and customer_ref like 'owner%') then
    insert into public.owner_devices(device) values (p_device) on conflict do nothing;
    delete from public.visits where device = p_device;
    return;
  end if;
  if exists (select 1 from public.owner_devices where device = p_device) then return; end if;
  insert into public.visits(day, device, signed_in, tz) values (current_date, p_device, auth.uid() is not null, z)
  on conflict (day, device) do update set views = least(public.visits.views + 1, 10000),
    signed_in = public.visits.signed_in or excluded.signed_in, tz = coalesce(public.visits.tz, excluded.tz);
  if auth.uid() is not null and z is not null then
    insert into public.account_tz(user_id, tz) values (auth.uid(), z) on conflict (user_id) do nothing;
  end if;
end;
$$;
revoke all on function public.log_visit(uuid, text) from public;
grant execute on function public.log_visit(uuid, text) to anon, authenticated;

create or replace function public.visitor_stats() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare is_owner boolean;
begin
  select exists (select 1 from public.subscriptions where user_id = auth.uid() and customer_ref like 'owner%') into is_owner;
  if not is_owner then raise exception 'not allowed'; end if;
  return jsonb_build_object(
    'today', (select count(*) from public.visits where day = current_date),
    'last_7_days', (select count(distinct device) from public.visits where day > current_date - 7),
    'last_30_days', (select count(distinct device) from public.visits where day > current_date - 30),
    'all_time', (select count(distinct device) from public.visits),
    'accounts', (select count(*) from auth.users),
    'searches_used', (select coalesce(sum(used), 0) from public.token_usage where owner like 'd:%' or owner like 'u:%'),
    'votes_up', (select count(*) from public.match_feedback where vote = 1),
    'votes_down', (select count(*) from public.match_feedback where vote = -1),
    'reviews', (select count(*) from public.site_reviews),
    'stars_avg', (select round(avg(stars)::numeric, 2) from public.site_reviews),
    'stars', (select coalesce(jsonb_object_agg(stars, n), '{}'::jsonb) from (select stars, count(*) n from public.site_reviews group by stars) y),
    'recent_reviews', (select coalesce(jsonb_agg(r order by r.at desc), '[]'::jsonb) from
                       (select at, stars, language, tracks_played, source, comment from public.site_reviews order by at desc limit 100) r),
    -- where people are: browser time zones (the stats page turns them into countries)
    'zones_30_days', (select coalesce(jsonb_object_agg(tz, n), '{}'::jsonb) from
                      (select tz, count(distinct device) n from public.visits where tz is not null and day > current_date - 30 group by tz) z),
    'zones_all_time', (select coalesce(jsonb_object_agg(tz, n), '{}'::jsonb) from
                       (select tz, count(distinct device) n from public.visits where tz is not null group by tz) z),
    'account_zones', (select coalesce(jsonb_object_agg(tz, n), '{}'::jsonb) from
                      (select tz, count(*) n from public.account_tz group by tz) z),
    'days', (select coalesce(jsonb_agg(jsonb_build_object('day', day, 'visitors', n, 'views', v, 'new', nw) order by day desc), '[]'::jsonb)
             from (select v1.day, count(*) n, sum(v1.views) v,
                          count(*) filter (where not exists (select 1 from public.visits v2 where v2.device = v1.device and v2.day < v1.day)) nw
                   from public.visits v1 where v1.day > current_date - 30 group by v1.day) x));
end;
$$;
revoke all on function public.visitor_stats() from public, anon;
grant execute on function public.visitor_stats() to authenticated;
