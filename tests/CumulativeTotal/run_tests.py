#!/usr/bin/env python3
"""Run the DaxPatterns.CumulativeTotal tests.

Each test query compares a function call with a reference measure (the original DAX of the pattern).
The runner adds the functions of src/CumulativeTotal/lib/functions.tmdl as DEFINE FUNCTION, so you do not have to
install the package to run the tests.

Targets:
  daxdo                       public dax.do service (Contoso model), no authentication
  pbi <workspaceId> <datasetId>  Power BI REST executeQueries. Needs a service principal:
                               env PBI_TENANT_ID, PBI_CLIENT_ID, PBI_CLIENT_SECRET (never commit them)

Usage:
  python3 run_tests.py daxdo [--profile daxdo]
  python3 run_tests.py pbi <workspaceId> <datasetId> --profile contoso --expected expected/contoso-10k.json
  python3 run_tests.py print <case> --profile contoso    (print the full query, to paste in DAX query view)
  add --write-expected <file> to save the checksums as the new expected results
"""
import json, os, re, sys, urllib.error, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FUNCTIONS = os.path.join(ROOT, "src", "CumulativeTotal", "lib", "functions.tmdl")

PROFILES = {
    # Contoso Data Generator models (Contoso 10k, 100k, ...)
    "contoso": {"YearMonth": "Year Month", "YearMonthNumber": "Year Month Number", "Year": "Year", "Female": '"female"', "SelectedYear": "2024", "OtherYear": "2023"},
    # dax.do Contoso model
    "daxdo": {"YearMonth": "Calendar Year Month", "YearMonthNumber": "Calendar Year Month Number", "Year": "Calendar Year Number", "Female": '"F"', "SelectedYear": "2008", "OtherYear": "2007"},
}

def tmdl_to_define(path):
    """Convert the TMDL functions to DEFINE FUNCTION statements."""
    text = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"function\s+'([^']+)'\s*=\s*```(.*?)```", text, re.S):
        out.append(f"    FUNCTION {m.group(1)} = {m.group(2).strip()}\n")
    if not out:
        raise SystemExit("No functions found in " + path)
    return "\n".join(out)

def build(case, profile):
    src = open(os.path.join(HERE, "cases", case + ".dax"), encoding="utf-8").read()
    header = src.split("EVALUATE", 1)[0]
    needs = re.findall(r"common/[\w\-.]+\.dax", header)
    defs, body = src.split("\nEVALUATE\n", 1)
    local_defs = "\n".join(l for l in defs.splitlines() if not l.strip().startswith("//"))
    q = "DEFINE\n" + tmdl_to_define(FUNCTIONS)
    for n in needs:
        q += open(os.path.join(HERE, n), encoding="utf-8").read() + "\n"
    q += local_defs + "\nEVALUATE\n" + body
    for k, v in PROFILES[profile].items():
        q = q.replace(f"@@{k}@@", v)
    return q

def run_daxdo(q):
    data = urllib.parse.urlencode({"dax": q}).encode()
    try:
        r = json.load(urllib.request.urlopen("https://daxdo.azurewebsites.net/api/_ContosoV01/query", data, timeout=300))
    except urllib.error.HTTPError as e:
        raise RuntimeError(e.read().decode()[:2000])
    if not isinstance(r, list):
        raise RuntimeError(str(r)[:2000])
    return r[0]["result"]

_token = None
def run_pbi(q, ws, ds):
    global _token
    if _token is None:
        d = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": os.environ["PBI_CLIENT_ID"],
            "client_secret": os.environ["PBI_CLIENT_SECRET"], "scope": "https://analysis.windows.net/powerbi/api/.default"}).encode()
        _token = json.load(urllib.request.urlopen(f"https://login.microsoftonline.com/{os.environ['PBI_TENANT_ID']}/oauth2/v2.0/token", d))["access_token"]
    req = urllib.request.Request(f"https://api.powerbi.com/v1.0/myorg/groups/{ws}/datasets/{ds}/executeQueries",
        data=json.dumps({"queries": [{"query": q}], "serializerSettings": {"includeNulls": True}}).encode(),
        headers={"Authorization": "Bearer " + _token, "Content-Type": "application/json"}, method="POST")
    try:
        r = json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        raise RuntimeError(e.read().decode()[:2000])
    return r["results"][0]["tables"][0]["rows"]

def norm(row):
    return {k.strip("[]").split("[")[-1].strip("]"): v for k, v in row.items()}

def main(a):
    profile = a[a.index("--profile") + 1] if "--profile" in a else ("daxdo" if a[0] == "daxdo" else "contoso")
    if a[0] == "print":
        print(build(a[1], profile)); return 0
    expected = json.load(open(a[a.index("--expected") + 1])) if "--expected" in a else None
    cases = sorted(f[:-4] for f in os.listdir(os.path.join(HERE, "cases")) if f.endswith(".dax"))
    results, failed = {}, 0
    for c in cases:
        q = build(c, profile)
        src = open(os.path.join(HERE, "cases", c + ".dax"), encoding="utf-8").read()
        expect_error = re.search(r"// ExpectError: (.+)", src)
        try:
            rows = run_daxdo(q) if a[0] == "daxdo" else run_pbi(q, a[1], a[2])
            if expect_error:
                print(f"FAIL {c}: expected an error, the query returned rows"); failed += 1; continue
        except Exception as e:
            if expect_error and expect_error.group(1).strip() in str(e):
                print(f"PASS {c}: expected error raised"); results[c] = {"Rows": 0, "Checksum": 0}; continue
            print(f"FAIL {c}: query error: {e}"); failed += 1; continue
        for r in map(norm, rows):
            t = r["Test"]; results[t] = {"Rows": r["Rows"], "Checksum": r["Checksum"]}
            ok = r["Mismatches"] == 0 and (r["Rows"] or 0) > 0
            if expected is not None and t in expected:
                ok = ok and abs((r["Checksum"] or 0) - (expected[t]["Checksum"] or 0)) <= 0.01 and r["Rows"] == expected[t]["Rows"]
            failed += 0 if ok else 1
            print(f"{'PASS' if ok else 'FAIL'} {t}  rows={r['Rows']}  mismatches={r['Mismatches']}  checksum={r['Checksum']}")
    if "--write-expected" in a:
        json.dump(results, open(a[a.index("--write-expected") + 1], "w"), indent=2)
    print(f"\n{len(results)} tests, {failed} failed")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
