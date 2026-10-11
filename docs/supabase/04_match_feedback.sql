-- Thumbs up / down on matches (run 11 Oct 2026). Every vote is a DJ's judgement of one match,
-- used to measure and improve matching. Visitors can only add votes through record_vote();
-- nobody can read other people's votes from the website.
create table if not exists public.match_feedback (
  id bigserial primary key,
  seed bigint not null,            -- the track that was searched (Deezer id)
  match bigint not null,           -- the match that was shown
  vote smallint not null check (vote in (-1, 1)),
  device uuid not null,
  user_id uuid,
  rank int, similarity int, mix text,   -- what the site showed, for learning later
  at timestamptz not null default now(),
  unique (device, seed, match)
);
alter table public.match_feedback enable row level security;

create or replace function public.record_vote(p_device uuid, p_seed bigint, p_match bigint, p_vote int,
                                              p_rank int default null, p_similarity int default null, p_mix text default null)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if p_vote not in (-1, 0, 1) then raise exception 'bad vote'; end if;
  if (select count(*) from public.match_feedback where device = p_device and at > now() - interval '1 day') > 500 then
    return;   -- simple spam limit per device
  end if;
  if p_vote = 0 then
    delete from public.match_feedback where device = p_device and seed = p_seed and match = p_match;
    return;
  end if;
  insert into public.match_feedback(seed, match, vote, device, user_id, rank, similarity, mix)
  values (p_seed, p_match, p_vote, p_device, auth.uid(), p_rank, p_similarity, left(p_mix, 16))
  on conflict (device, seed, match) do update set vote = excluded.vote, at = now(), user_id = excluded.user_id;
end;
$$;
revoke all on function public.record_vote(uuid, bigint, bigint, int, int, int, text) from public;
grant execute on function public.record_vote(uuid, bigint, bigint, int, int, int, text) to anon, authenticated;
