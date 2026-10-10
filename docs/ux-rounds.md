# SimilarSounds UX/UI improvement rounds

Each round: review the local site (desktop 800px + phone 375px), score with the fixed
rubric below, make 1-2 highest-impact upgrades, re-score. Kept only if the overall score
goes up (committed + pushed live); otherwise reverted with git.

## Rubric (each 0-10, overall = average, rounded to 0.5)

| Area | 10/10 means |
|---|---|
| Visual design | Consistent spacing/type scale, clear hierarchy, polished components, no rough edges |
| UX clarity | A first-time visitor instantly knows what to do and what each control means |
| Search flow | Typing, suggestions, loading and errors feel fast, guided and forgiving |
| Results | Easy to scan and compare; key/BPM/energy/newness readable at a glance; preview is one tap |
| Build your set | Discoverable, easy to add/reorder, transition feedback clear, useful export |
| Mobile | Thumb-friendly, no overflow, filters and panel comfortable at 375px |
| Accessibility | Contrast, focus states, keyboard use, labels, reduced motion |
| Polish/perf | Empty/loading states, no layout jumps, no console errors, small touches (favicon, meta, share image) |

## Log

### Baseline: 6.5
Visual 6.5 · Clarity 6 · Search 7.5 · Results 6 · Set 7 · Mobile 6.5 · Access 5.5 · Polish 6

### Round 1: 6.5 → 7.0 (kept)
- Compact result rows: cover art is the play button (one-tap preview), NEW badge, one chip line
  incl. match %, only "+ Set" and "Beatport" on the row; SoundCloud/YouTube links appear with the preview.
- Start screen: 4 fresh example releases to try (newest per sub-genre, cover required, explicit titles
  skipped) and a 3-step "how it works". Filters grouped as label+control pairs; BPM shows ±3/±6/±10.
Scores: Visual 7.5 · Clarity 7.5 · Search 7.5 · Results 7.5 · Set 7 · Mobile 7 · Access 6 · Polish 6.5

### Round 2: 7.0 → 7.5 (kept)
- Accessibility: visible green focus ring everywhere (search box glows when focused), reduced-motion
  support, screen-reader announcements for searching/results, errors as alerts, suggestion list
  wired to the input (aria-activedescendant), set panel is a proper dialog: unreachable while
  closed (inert), focus moves in on open and back to the button on close.
- Loading: spinner + skeleton result rows + honest "new tracks can take ~10 seconds" hint.
- Polish: meta description, social share title/description, theme colour, friendlier footer.
Scores: Visual 7.5 · Clarity 7.5 · Search 8 · Results 7.5 · Set 7.5 · Mobile 7 · Access 8 · Polish 7.5

### Round 3: 7.5 → 8.0 (kept)
- Build your set: "✦ Smart order" reorders the set for the smoothest key/BPM/energy transitions
  and a gentle energy build (test set: 1 smooth/3 workable → 4 smooth/0 clashing), with Undo.
  Energy-flow line now scaled to the set's own range with round, coloured dots and a start→end label.
- Mobile: sticky "Your set" bar at the bottom (count + clash status, one tap to open), cramped top bar
  removed, filters fold into a one-line "Filters" summary showing the current choices.
Scores: Visual 8 · Clarity 7.5 · Search 8 · Results 7.5 · Set 8.5 · Mobile 8.5 · Access 8 · Polish 8

### Round 4: 8.0 → 8.3 (kept)  [scores now reported to one decimal]
- Results: every match shows "why" in the same green/amber/red language as Build your set
  (e.g. "Mixes well · Same key · +2 BPM · energy +1"). Sort by Best match / Smoothest mix /
  Newest / Closest BPM (client-side, instant).
- Clarity: "How to read these results" legend explaining the mix dot, Camelot key, energy bars
  and sound-match %.
Scores: Visual 8 · Clarity 8.5 · Search 8 · Results 8.5 · Set 8.5 · Mobile 8.5 · Access 8 · Polish 8
