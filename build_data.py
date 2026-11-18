"""Builds data.json for the music dashboard from the public Spotify songs dataset.
Run:  python3 build_data.py   (downloads the CSV, runs analysis.sql, writes data.json and dashboard.html)
"""
import csv, json, sqlite3, statistics as st, urllib.request, os, re
URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-01-21/spotify_songs.csv"
here = os.path.dirname(os.path.abspath(__file__))
csv_path = os.environ.get("SONGS_CSV") or os.path.join(here, "spotify_songs.csv")
if not os.path.exists(csv_path):
    urllib.request.urlretrieve(URL, csv_path)
rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
cols = list(rows[0].keys())
num = {"track_popularity","danceability","energy","key","loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo","duration_ms"}
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE songs(%s)" % ",".join(c + (" REAL" if c in num else "") for c in cols))
con.executemany("INSERT INTO songs VALUES(%s)" % ",".join("?" * len(cols)), [[r[c] for c in cols] for r in rows])
blocks = [b.strip() for b in open(os.path.join(here, "analysis.sql")).read().split("\n\n") if "SELECT" in b or "CREATE" in b]
con.execute(re.sub(r"^--.*\n", "", blocks[0], flags=re.M).strip().rstrip(";"))
def run(i):
    sql = "\n".join(l for l in blocks[i].splitlines() if not l.startswith("--")).strip().rstrip(";")
    return con.execute(sql).fetchall()
n_rows = con.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
n_tracks = con.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
n_artists = con.execute("SELECT COUNT(DISTINCT track_artist) FROM songs").fetchone()[0]
by_playlists = run(1); by_genre = run(2); by_year = run(3); by_len = run(4); top_artists = run(5)
# correlations (track level)
feat = {"Danceability":"danceability","Energy":"energy","Mood (valence)":"valence","Tempo":"tempo","Loudness":"loudness","Acousticness":"acousticness","Speechiness":"speechiness"}
tl = con.execute("""SELECT t.track_id, t.popularity, t.n_playlists, t.minutes,
  AVG(s.danceability),AVG(s.energy),AVG(s.valence),AVG(s.tempo),AVG(s.loudness),AVG(s.acousticness),AVG(s.speechiness)
  FROM tracks t JOIN songs s USING(track_id) GROUP BY t.track_id""").fetchall()
def corr(x, y):
    mx, my = st.mean(x), st.mean(y)
    return sum((a-mx)*(b-my) for a, b in zip(x, y)) / ((sum((a-mx)**2 for a in x) ** .5) * (sum((b-my)**2 for b in y) ** .5))
pop = [r[1] for r in tl]
corrs = [("Playlists the song is on", corr(pop, [r[2] for r in tl])), ("Song length", corr(pop, [r[3] for r in tl]))]
for i, name in enumerate(feat, 4):
    corrs.append((name, corr(pop, [r[i] for r in tl])))
corrs.sort(key=lambda c: -abs(c[1]))
avg_pop = st.mean(pop)
multi = [r[1] for r in tl if r[2] >= 3]; single = [r[1] for r in tl if r[2] == 1]
data = {
  "source": URL, "rows": n_rows, "tracks": n_tracks, "artists": n_artists, "avg_pop": round(avg_pop, 1),
  "pop_zero_share": round(100 * sum(1 for p in pop if p == 0) / len(pop), 1),
  "single_pop": round(st.mean(single), 1), "multi_pop": round(st.mean(multi), 1),
  "single_n": len(single), "multi_n": len(multi),
  "by_playlists": [{"k": ("6+" if r[0] == 6 else str(r[0])), "n": r[1], "v": r[2]} for r in by_playlists],
  "by_genre": [{"k": r[0], "n": r[1], "v": r[2]} for r in by_genre],
  "by_year": [{"k": r[0], "n": r[1], "v": r[2]} for r in by_year],
  "by_len": [{"k": r[0][3:], "n": r[1], "v": r[2]} for r in by_len],
  "corrs": [{"k": k, "v": round(v, 3)} for k, v in corrs],
  "top_artists": [{"k": r[0], "n": r[1], "v": r[2]} for r in top_artists],
}
json.dump(data, open(os.path.join(here, "data.json"), "w"), indent=1)
tpl = open(os.path.join(here, "dashboard_template.html")).read()
open(os.path.join(here, "dashboard.html"), "w").write(tpl.replace("/*DATA*/null", json.dumps(data)))
print(json.dumps(data, indent=1))
