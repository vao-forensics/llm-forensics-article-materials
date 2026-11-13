#!/usr/bin/env python3
"""Відтворюваність (рецензія B15): 3 незалежні прогони моделювання збоїв і запитів вимірювань,
порівняння SHA-256 між прогонами та з оригіналом 08.11. Оригінальні файли доказів НЕ змінюються."""
import hashlib, json, os, subprocess, time

SRC = "/srv/dfir/thesis_evidence/2026-11-08"
OUT = "/srv/dfir/thesis_evidence/2026-11-13/repro"
MAT = "/srv/dfir/var/article_materials/measurements"
os.makedirs(OUT, exist_ok=True)
h = lambda b: hashlib.sha256(b).hexdigest()
rep = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "fault_injection": [], "sql": {}}

orig_json = open(os.path.join(SRC, "fault_injection.json"), "rb").read()
rep["fault_injection_original_sha256"] = h(orig_json)

code = open(os.path.join(SRC, "fault_injection.py"), encoding="utf-8").read()
for i in range(1, 4):
    out_json = os.path.join(OUT, "fi_run%d.json" % i)
    c2 = code.replace(os.path.join(SRC, "fault_injection.json"), out_json)
    assert out_json in c2, "path rewrite failed"
    p = os.path.join(OUT, "fi_copy.py")
    open(p, "w", encoding="utf-8").write(c2)
    t0 = time.time()
    r = subprocess.run(["python3", p], capture_output=True, text=True, timeout=1800)
    rep["fault_injection"].append({"run": i, "sec": round(time.time() - t0, 1), "rc": r.returncode,
                                   "json_sha256": h(open(out_json, "rb").read()) if os.path.exists(out_json) else None,
                                   "stdout_sha256": h(r.stdout.encode())})

for sql in sorted(f for f in os.listdir(MAT) if f.endswith(".sql")):
    q = open(os.path.join(MAT, sql), encoding="utf-8").read()
    hs = []
    for i in range(3):
        r = subprocess.run(["docker", "exec", "-i", "logdb", "psql", "-U", "dfir", "-d", "dfir_logs", "-At", "-F", "|"],
                           input=q, capture_output=True, text=True, timeout=600)
        hs.append(h(r.stdout.encode()))
        if i == 0:
            rep["sql"][sql] = {"rows": len(r.stdout.strip().splitlines())}
    rep["sql"][sql]["sha256_runs"] = hs

fi_hashes = {x["json_sha256"] for x in rep["fault_injection"]}
rep["verdict"] = {
    "fi_runs_identical": len(fi_hashes) == 1,
    "fi_equals_original_08_11": rep["fault_injection_original_sha256"] in fi_hashes,
    "sql_runs_identical": all(len(set(v["sha256_runs"])) == 1 for v in rep["sql"].values()),
}
json.dump(rep, open(os.path.join(OUT, "repro_report.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(rep["verdict"], ensure_ascii=False))
print("прогони FI (с):", [x["sec"] for x in rep["fault_injection"]], "| rc:", [x["rc"] for x in rep["fault_injection"]])
print("SQL рядків:", {k: v["rows"] for k, v in rep["sql"].items()})
