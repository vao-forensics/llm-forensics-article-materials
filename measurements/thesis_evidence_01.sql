-- Первинні виміри для розділу 4 магістерської роботи.
-- Нічого не змінює: лише читання. Вивід зберігається як сирий протокол виміру,
-- бо саме сирих протоколів бракувало попередній версії роботи.

\echo '=== A. ЕТАЛОННА БАЗА СПРАВ (склад кожної справи) ==='
SELECT c.case_key,
       to_char(c.created_at, 'YYYY-MM-DD') AS created,
       (SELECT count(*) FROM event_logs_v2 e WHERE e.case_key = c.case_key) AS events,
       (SELECT count(*) FROM filesystem_v2 f WHERE f.case_key = c.case_key) AS fs_rows,
       (SELECT count(*) FROM program_exec_v2 p WHERE p.case_key = c.case_key) AS exec_rows,
       (SELECT count(*) FROM srum_v2 s WHERE s.case_key = c.case_key) AS srum_rows,
       (SELECT count(*) FROM case_iocs i WHERE i.case_key = c.case_key) AS iocs,
       (SELECT count(*) FROM case_trigger_hits_v2 t WHERE t.case_key = c.case_key) AS trigger_hits,
       (SELECT count(*) FROM dfir_case_qa_v1 q WHERE q.case_key = c.case_key) AS qa
  FROM cases c
 ORDER BY 1;

\echo ''
\echo '=== B. ПОКРИТТЯ ЖУРНАЛІВ ПОДІЙ: скільки каналів у кожній справі ==='
SELECT case_key, count(DISTINCT channel) AS channels, count(*) AS rows
  FROM event_logs_v2 GROUP BY 1 ORDER BY 1;

\echo ''
\echo '=== C. ПОВНОТА ВХІДНИХ ДАНИХ: стан опрацювання файлів архіву ==='
SELECT case_key, status, count(*) AS files, sum(rows) AS rows_loaded
  FROM dfir_ingest_coverage_v1 GROUP BY 1, 2 ORDER BY 1, 2;

\echo ''
\echo '=== D. СПРАЦЮВАННЯ ДЕТЕРМІНОВАНОГО ШАРУ за ознакою ==='
SELECT trigger, count(*) AS hits, count(DISTINCT case_key) AS cases,
       round(avg(score), 3) AS avg_score
  FROM case_trigger_hits_v2 GROUP BY 1 ORDER BY 2 DESC;

\echo ''
\echo '=== E. РУШІЙ ПИТАНЬ І ВІДПОВІДЕЙ: стан відповідей ==='
SELECT status, count(*) AS answers, count(DISTINCT case_key) AS cases,
       round(avg(confidence)::numeric, 3) AS avg_confidence
  FROM dfir_case_qa_v1 GROUP BY 1 ORDER BY 2 DESC;

\echo ''
\echo '=== F. ТВЕРДЖЕННЯ ТА ЇХ ЗВЯЗОК ІЗ ДОКАЗАМИ ==='
SELECT (SELECT count(*) FROM dfir_claims_v1) AS claims,
       (SELECT count(*) FROM dfir_claim_evidence_links_v1) AS evidence_links,
       (SELECT count(DISTINCT claim_id) FROM dfir_claim_evidence_links_v1) AS claims_with_evidence;

\echo ''
\echo '=== G. ЧАСОВИЙ ОХОПЛЕНИЙ ДІАПАЗОН ПОДІЙ ПО СПРАВАХ ==='
SELECT case_key, min(event_ts)::date AS first_event, max(event_ts)::date AS last_event,
       count(*) AS rows
  FROM event_logs_v2 WHERE event_ts IS NOT NULL GROUP BY 1 ORDER BY 1;
