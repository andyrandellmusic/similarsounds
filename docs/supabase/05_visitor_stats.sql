-- Private visitor count (run 11 Oct 2026). Records which (random) device visited on which day and
-- how many pages were opened. Only the owner account can read the totals, via visitor_stats().
-- The owner's own visits are never counted: any device that has been signed in as the owner is
-- remembered in owner_devices and skipped, even when it later visits signed out.
create table if not exists public.owner_devices (device uuid primary key, at timestamptz not null default now());
alter table public.owner_devices enable row level security;
create table if not exists public.visits (
  day date not null default current_date,
  device uuid not null,
  views int not null default 1,
  signed_in boolean not null default false,
  primary key (day, device)
);
alter table public.visits enable row level security;

create or replace function public.log_visit(p_device uuid) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if exists (select 1 from public.subscriptions where user_id = auth.uid() and customer_ref like 'owner%') then
    insert into public.owner_devices(device) values (p_device) on conflict do nothing;
    delete from public.visits where device = p_device;
    return;
  end if;
  if exists (select 1 from public.owner_devices where device = p_device) then return; end if;
  insert into public.visits(day, device, signed_in) values (current_date, p_device, auth.uid() is not null)
  on conflict (day, device) do update set views = least(public.visits.views + 1, 10000),
    signed_in = public.visits.signed_in or excluded.signed_in;
end;
$$;
revoke all on function public.log_visit(uuid) from public;
grant execute on function public.log_visit(uuid) to anon, authenticated;

-- Star reviews from the pop-up (also kept in reviews.csv). Added by the server only.
create table if not exists public.site_reviews (
  id bigserial primary key,
  at timestamptz not null default now(),
  stars smallint not null check (stars between 1 and 5),
  language text, tracks_played int,
  source text,          -- 'popup' (after 60 plays) or 'page' (the box at the bottom)
  comment text          -- "How can we improve?"
);
alter table public.site_reviews enable row level security;
create or replace function public.add_review(p_stars int, p_lang text, p_plays int, p_comment text default null, p_source text default 'popup')
returns void language sql security definer set search_path = '' as $$
  insert into public.site_reviews(stars, language, tracks_played, source, comment)
  values (p_stars, left(p_lang, 8), p_plays, left(p_source, 8), nullif(left(p_comment, 1000), ''));
$$;
revoke all on function public.add_review(int, text, int, text, text) from public;
grant execute on function public.add_review(int, text, int, text, text) to anon, authenticated;

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
    'days', (select coalesce(jsonb_agg(jsonb_build_object('day', day, 'visitors', n, 'views', v, 'new', nw) order by day desc), '[]'::jsonb)
             from (select v1.day, count(*) n, sum(v1.views) v,
                          count(*) filter (where not exists (select 1 from public.visits v2 where v2.device = v1.device and v2.day < v1.day)) nw
                   from public.visits v1 where v1.day > current_date - 30 group by v1.day) x));
end;
$$;
revoke all on function public.visitor_stats() from public, anon;
grant execute on function public.visitor_stats() to authenticated;
