-- Top extensions by total size
SELECT * FROM v_ext_summary LIMIT 50;

-- Biggest files
SELECT rel_path, size_bytes, ROUND(size_bytes/1048576.0,2) AS mb, mtime_iso FROM files ORDER BY size_bytes DESC LIMIT 50;

-- Example: TSX under keystone
SELECT rel_path, size_bytes FROM files WHERE ext='.tsx' AND rel_path LIKE '%apps/keystone%' ORDER BY size_bytes DESC LIMIT 200;

-- Directory size leaderboard
SELECT dir_rel, file_count, ROUND(total_size_bytes/1048576.0,2) AS total_mb FROM dir_stats ORDER BY total_size_bytes DESC LIMIT 100;

-- If sha1 enabled: real duplicates
SELECT sha1, COUNT(*) c, MIN(size_bytes) size_bytes FROM files WHERE sha1 IS NOT NULL GROUP BY sha1 HAVING c>1 ORDER BY c DESC LIMIT 100;