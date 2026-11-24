import sys
from pathlib import Path
import yaml
bench, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
base = yaml.safe_load(Path(f"examples/tunings/starrocks/{bench}_tuned.yaml").read_text())
def write(name, fn):
    doc = yaml.safe_load(yaml.safe_dump(base)); doc["table_tunings"] = fn(doc["table_tunings"])
    (out / f"{name}.yaml").write_text(yaml.safe_dump(doc, sort_keys=False))
def only(key):
    def fn(tables):
        return {n: {"table_name": n, key: t[key]} for n, t in tables.items()}
    return fn
if bench == "tpcds":
    write("dist", only("distribution")); write("sort", only("sorting"))
else:
    write("lineitem", lambda t: {"LINEITEM": t["LINEITEM"]}); write("orders", lambda t: {"ORDERS": t["ORDERS"]})
