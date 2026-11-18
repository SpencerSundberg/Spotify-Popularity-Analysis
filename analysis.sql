-- Spotify songs analysis (public TidyTuesday dataset, 2020-01-21)
-- Table `songs` holds one row per track-in-playlist (32,833 rows).

-- 1. One row per unique track, with how many playlists it appears in
CREATE TABLE tracks AS
SELECT track_id,
       MIN(track_artist)                       AS artist,
       MAX(track_popularity)                   AS popularity,
       COUNT(DISTINCT playlist_id)             AS n_playlists,
       AVG(duration_ms) / 60000.0              AS minutes,
       MIN(SUBSTR(track_album_release_date,1,4)) AS release_year
FROM songs
GROUP BY track_id;

-- 2. Does being on more playlists go with higher popularity?
SELECT CASE WHEN n_playlists >= 6 THEN 6 ELSE n_playlists END AS playlists,
       COUNT(*)                     AS tracks,
       ROUND(AVG(popularity), 1)    AS avg_popularity
FROM tracks
GROUP BY 1
ORDER BY 1;

-- 3. Average popularity by genre (each track counted once per genre)
SELECT playlist_genre AS genre,
       COUNT(*)                     AS tracks,
       ROUND(AVG(track_popularity), 1) AS avg_popularity
FROM (SELECT DISTINCT track_id, playlist_genre, track_popularity FROM songs)
GROUP BY playlist_genre
ORDER BY avg_popularity DESC;

-- 4. Average popularity by release year, 2010-2019
SELECT release_year, COUNT(*) AS tracks, ROUND(AVG(popularity), 1) AS avg_popularity
FROM tracks
WHERE release_year BETWEEN '2010' AND '2019'
GROUP BY release_year
ORDER BY release_year;

-- 5. Average popularity by song length
SELECT CASE WHEN minutes < 2.5 THEN '1. under 2:30'
            WHEN minutes < 3.0 THEN '2. 2:30 to 3:00'
            WHEN minutes < 3.5 THEN '3. 3:00 to 3:30'
            WHEN minutes < 4.0 THEN '4. 3:30 to 4:00'
            WHEN minutes < 5.0 THEN '5. 4:00 to 5:00'
            ELSE '6. over 5:00' END AS length_bucket,
       COUNT(*) AS tracks,
       ROUND(AVG(popularity), 1) AS avg_popularity
FROM tracks
GROUP BY 1
ORDER BY 1;

-- 6. Artists with at least 8 tracks, ranked by average popularity
SELECT artist, COUNT(*) AS tracks, ROUND(AVG(popularity), 1) AS avg_popularity
FROM tracks
GROUP BY artist
HAVING COUNT(*) >= 8
ORDER BY avg_popularity DESC
LIMIT 10;
