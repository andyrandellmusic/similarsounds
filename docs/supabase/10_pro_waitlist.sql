-- "Tell me when Pro is ready" sign-up list (11 Nov 2026). Safe to run again.
-- Visitors leave an email to hear (once) when SimilarSounds Pro launches; early sign-ups get £3.99/month for their
-- first 3 months. Nobody can read the list through the site: only the server's service key (to apply the discount
-- at checkout) and the owner's stats page (the count only).
create table if not exists public.pro_waitlist (
  email text primary key check (email = lower(email) and length(email) between 6 and 254 and email like '%_@_%._%'),
  language text not null default 'en',
  joined timestamptz not null default now()
);
alter table public.pro_waitlist enable row level security;

create or replace function public.join_waitlist(p_email text, p_lang text default 'en') returns void
language plpgsql security definer set search_path = '' as $$
declare e text := lower(trim(coalesce(p_email, '')));
begin
  if length(e) not between 6 and 254 or e !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' then raise exception 'bad email'; end if;
  -- the public key can call this directly, so a ceiling stops anyone flooding the list
  if (select count(*) from public.pro_waitlist where joined > now() - interval '1 hour') >= 300 then
    raise exception 'busy';
  end if;
  insert into public.pro_waitlist(email, language) values (e, left(coalesce(nullif(p_lang, ''), 'en'), 8))
  on conflict (email) do nothing;          -- joining twice is harmless
end;
$$;
revoke all on function public.join_waitlist(text, text) from public;
grant execute on function public.join_waitlist(text, text) to anon, authenticated;

-- The owner's stats page: same as 09_visit_country.sql, plus the sign-up count.
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
    'waitlist', (select count(*) from public.pro_waitlist),
    'waitlist_7_days', (select count(*) from public.pro_waitlist where joined > now() - interval '7 days'),
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
