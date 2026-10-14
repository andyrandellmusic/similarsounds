-- SimilarSounds "Most played": how many times each track's preview is played, per day.
-- Nothing about the visitor is stored, just the track and a count. Only the two functions below
-- can read or change the table.

create table if not exists public.track_plays (
  deezer_id bigint not null,
  day date not null default current_date,
  plays int not null default 0,
  primary key (deezer_id, day)
);

alter table public.track_plays enable row level security;

-- one play of a track's preview
create or replace function public.count_play(p_id bigint)
returns void language sql security definer set search_path = public as $$
  insert into public.track_plays (deezer_id, day, plays) values (p_id, current_date, 1)
  on conflict (deezer_id, day) do update set plays = public.track_plays.plays + 1;
$$;

-- the most played tracks over the last p_days days
create or replace function public.top_played(p_days int default 7, p_limit int default 20)
returns table (deezer_id bigint, plays bigint) language sql security definer set search_path = public as $$
  select deezer_id, sum(plays)::bigint as plays from public.track_plays
  where day > current_date - greatest(1, least(p_days, 90))
  group by deezer_id order by plays desc, deezer_id limit greatest(1, least(p_limit, 50));
$$;

revoke all on function public.count_play(bigint) from public;
revoke all on function public.top_played(int, int) from public;
grant execute on function public.count_play(bigint) to anon, authenticated;
grant execute on function public.top_played(int, int) to anon, authenticated;
