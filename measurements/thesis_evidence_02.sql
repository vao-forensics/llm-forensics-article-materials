-- Зведені показники повноти вхідних даних і бази справ (для підрозділів 4.1-4.2).
\echo '=== H. ПОВНОТА ВХІДНИХ ДАНИХ: зведення по справах ==='
SELECT case_key,
       count(*) FILTER (WHERE status = 'consumed')     AS consumed,
       count(*) FILTER (WHERE status = 'empty')        AS empty,
       count(*) FILTER (WHERE status LIKE 'skipped:%') AS skipped,
       count(*) FILTER (WHERE status = 'unconsumed')   AS unconsumed,
       count(*) FILTER (WHERE status NOT IN ('consumed', 'empty', 'unconsumed')
                          AND status NOT LIKE 'skipped:%') AS other,
       count(*) AS files,
       round(100.0 * count(*) FILTER (WHERE status = 'consumed') / count(*), 1) AS consumed_pct
  FROM dfir_ingest_coverage_v1 GROUP BY 1 ORDER BY 1;

\echo ''
\echo '=== I. ПОВНОТА ВХІДНИХ ДАНИХ: загалом ==='
SELECT count(DISTINCT case_key) AS cases, count(*) AS files,
       count(*) FILTER (WHERE status = 'consumed') AS consumed,
       count(*) FILTER (WHERE status = 'empty') AS empty,
       count(*) FILTER (WHERE status LIKE 'skipped:%') AS skipped,
       count(*) FILTER (WHERE status = 'unconsumed') AS unconsumed,
       sum(rows) AS rows_loaded
  FROM dfir_ingest_coverage_v1;

\echo ''
\echo '=== J. НЕОПРАЦЬОВАНІ ФАЙЛИ: що саме лишилось поза аналізом ==='
SELECT rel_path, count(*) AS n, count(DISTINCT case_key) AS cases
  FROM dfir_ingest_coverage_v1 WHERE status = 'unconsumed'
 GROUP BY 1 ORDER BY 2 DESC LIMIT 25;

\echo ''
\echo '=== K. ПИТАННЯ І ВІДПОВІДІ ПО СПРАВАХ ==='
SELECT case_key,
       count(*) AS qa,
       count(*) FILTER (WHERE status = 'grounded') AS grounded,
       count(*) FILTER (WHERE status = 'no_data')  AS no_data,
       round(100.0 * count(*) FILTER (WHERE status = 'grounded') / count(*), 1) AS grounded_pct,
       round(avg(confidence) FILTER (WHERE status = 'grounded')::numeric, 3) AS avg_conf
  FROM dfir_case_qa_v1 GROUP BY 1 ORDER BY 1;

\echo ''
\echo '=== L. АРТЕФАКТИ ВИКОНАННЯ ЗА КЛАСОМ ДЖЕРЕЛА ==='
SELECT CASE
         WHEN source_file ILIKE '%amcache%'      THEN 'Amcache'
         WHEN source_file ILIKE '%appcompat%'
           OR source_file ILIKE '%shimcache%'    THEN 'ShimCache'
         WHEN source_file ILIKE '%prefetch%'     THEN 'Prefetch'
         WHEN source_file ILIKE '%userassist%'   THEN 'UserAssist'
         WHEN source_file ILIKE '%srum%'         THEN 'SRUM'
         WHEN source_file ILIKE '%bam%'          THEN 'BAM/DAM'
         ELSE 'iнше'
       END AS artefact,
       count(*) AS rows, count(DISTINCT case_key) AS cases
  FROM program_exec_v2 GROUP BY 1 ORDER BY 2 DESC;
