# What Makes a Song Popular? (Spotify analytics)

**Question:** Is a song's popularity about how it sounds, or about where it gets heard?

**Data:** Public TidyTuesday Spotify dataset (2020-01-21): 32,833 track-in-playlist rows, 28,356 unique tracks, six genres.

**Tools:** SQL (SQLite), Python, an HTML dashboard.

## Key findings
- Songs on 3 or more playlists average a popularity score of 71.4. Songs on one playlist average 37.1.
- Playlist count has the strongest link to popularity (correlation 0.29). Every audio feature (energy, danceability, mood, tempo) is near zero, and song length is the only notable one (-0.14).
- Songs of 2:30 to 3:00 score highest (42.6). Songs over five minutes score lowest (31.2).
- Pop (45.9) and Latin (44.3) lead by genre. EDM (34.1) trails.

## Recommendations
Build release plans around playlist placement, do not chase a "hit sound", keep singles tight when the song allows, and benchmark within genre.

## Limits
These are associations, not causes. The dataset was built by sampling playlists, popularity is a single early-2020 snapshot, and it has no stream, save, or listener counts.

## Files
- `analysis.sql`: all queries
- `build_data.py`: downloads the data, runs the SQL, writes `data.json` and `dashboard.html`
- `dashboard.html`: the finished dashboard (open it in a browser)

To rebuild: `python3 build_data.py`
