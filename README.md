# Supplementary materials / Додаткові матеріали

Materials for the article on local-LLM-assisted forensic analysis of Windows artifacts (input-completeness control and source traceability of conclusions).

Матеріали до статті про криміналістичний аналіз артефактів Windows із локальними ВММ (контроль повноти вхідних даних і простежуваність висновків).

| Path | What |
|---|---|
| `measurements/thesis_evidence_01.sql`, `_02.sql` | SQL queries that produced the level-A figures (run read-only against the analysis database) |
| `measurements/hayabusa_per_case_ratio.txt` | Per-case ratio of Hayabusa alerts to deterministic-layer alerts (10 cases; median 208) |
| `fault_injection/fault_injection.py` | Input-fault simulation on the per-file ingest ledger: rule (2) vs. "fail on first error" vs. completeness threshold |
| `fault_injection/fault_injection.txt`, `.json` | Its output (34 cases, seed 20261108) |
| `reproducibility/repro_check.py` | Three independent re-runs of the fault simulation and of both measurement queries; compares SHA-256 across runs and with the original run |
| `reproducibility/repro_report.json` | Its output: all re-runs byte-identical and identical to the original run |
| `reproducibility/netaudit_2026-11-13.json` | Network audit of the model host under load: 40 requests, 201 samples every 250 ms, 0 connections outside local networks |

Case materials, case identifiers and personal data are **not** included and cannot be shared; all figures are aggregates.
Справи, їхні ідентифікатори й персональні дані сюди **не** входять; усі показники зведені.

License: MIT.
