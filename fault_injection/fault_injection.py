"""Моделювання збоїв входу на обліку файлів (dfir_ingest_coverage_v1): правило (2) проти двох базових ліній.
Перевіряється лише частина правила про повноту входу (вважаємо Z_h = ∅, тобто контур хоче сказати «чисто»)."""
import subprocess, random, json, collections
random.seed(20261108)
CRIT = {"event": {"event", "logon_logoff"}, "exec": {"pe_prefetch", "pe_amcache", "pe_shimcache", "pe_bam"}, "fs": {"fs_mft"}}
FAM2CLS = {f: k for k, fs in CRIT.items() for f in fs}
q = "select case_key, coalesce(family,chr(32)), coalesce(rows,0), status from dfir_ingest_coverage_v1"
out = subprocess.run(["docker","exec","logdb","psql","-U","dfir","-d","dfir_logs","-At","-F","|","-c",q],capture_output=True,text=True).stdout
cases = collections.defaultdict(list)
for ln in out.splitlines():
    c, f, r, s = ln.split("|"); cases[c].append({"fam": f, "rows": int(r), "st": s})
# лише справи з усіма трьома критичними класами (як у статті: дискові тріажні архіви)
def has_all(fs): return all(any(FAM2CLS.get(x["fam"]) == k and x["rows"] > 0 for x in fs) for k in CRIT)
cases = {c: fs for c, fs in cases.items() if has_all(fs)}
def rule2(fs):
    if any(x["st"] == "rejected" for x in fs): return True
    n = collections.Counter()
    for x in fs:
        k = FAM2CLS.get(x["fam"])
        if k and x["st"] == "consumed": n[k] += x["rows"]
    return any(n[k] == 0 for k in CRIT)
def class_only(fs):
    n = collections.Counter()
    for x in fs:
        k = FAM2CLS.get(x["fam"])
        if k and x["st"] == "consumed": n[k] += x["rows"]
    return any(n[k] == 0 for k in CRIT)
def crash_first(fs): return any(x["st"] == "rejected" for x in fs)
def thresh(fs, tau=0.5):
    read = [x for x in fs if x["st"] in ("consumed", "empty", "unconsumed", "rejected")]
    return (sum(x["st"] == "consumed" for x in read) / max(1, len(read))) < tau
def mk(fs): return [dict(x) for x in fs]
SC = {}
def s_encoding(fs):
    fs = mk(fs); cons = [x for x in fs if x["st"] == "consumed"]
    for x in random.sample(cons, int(len(cons) * 143 / 147)): x["st"] = "rejected"; x["rows"] = 0
    return fs
def s_drop(k):
    def f(fs): return [x for x in mk(fs) if FAM2CLS.get(x["fam"]) != k]
    return f
def s_empty(k):
    def f(fs):
        fs = mk(fs)
        for x in fs:
            if FAM2CLS.get(x["fam"]) == k: x["st"] = "empty"; x["rows"] = 0
        return fs
    return f
def s_trunc(k):
    def f(fs):
        fs = mk(fs)
        for x in fs:
            if FAM2CLS.get(x["fam"]) == k and x["rows"] > 0: x["rows"] = max(1, x["rows"] // 100)
        return fs
    return f
def s_benign(fs):
    fs = mk(fs); nb = [x for x in fs if x["st"] == "consumed" and x["fam"].startswith("fb_browser")]
    if nb: random.choice(nb)["st"] = "rejected"
    return fs
SC["0 непошкоджений вхід"] = lambda fs: mk(fs)
SC["1 збій кодування (97 % файлів відхилено)"] = s_encoding
for k, nm in (("event", "журнали подій"), ("exec", "артефакти виконання"), ("fs", "$MFT")):
    SC["2 тиха втрата класу: %s відсутні в архіві" % nm] = s_drop(k)
    SC["3 файли класу порожні: %s" % nm] = s_empty(k)
    SC["4 обрізання класу до 1 %%: %s" % nm] = s_trunc(k)
SC["5 один некритичний файл відхилено (браузер)"] = s_benign
res = {}
for name, f in SC.items():
    r = {"rule2": 0, "class_only": 0, "crash_first": 0, "threshold_C<0.5": 0}
    for c, fs in cases.items():
        g = f(fs); r["rule2"] += rule2(g); r["class_only"] += class_only(g); r["crash_first"] += crash_first(g); r["threshold_C<0.5"] += thresh(g)
    res[name] = r
print("N справ:", len(cases))
for k, v in res.items(): print("%-55s %s" % (k, "  ".join("%s=%d" % kv for kv in v.items())))
json.dump({"n_cases": len(cases), "seed": 20261108, "results": res}, open("/srv/dfir/thesis_evidence/2026-11-08/fault_injection.json", "w"), ensure_ascii=False, indent=1)
