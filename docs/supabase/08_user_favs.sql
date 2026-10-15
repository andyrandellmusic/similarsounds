-- SimilarSounds: favourites kept in the account too, alongside the set and recent searches (run 15 Oct 2026)
alter table public.user_data add column if not exists favs jsonb not null default '[]'::jsonb;
