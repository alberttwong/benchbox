import duckdb, pymysql, benchbox
from decimal import Decimal
from benchbox.platforms.starrocks import StarRocksAdapter
b = benchbox.TPCDS(scale_factor=1.0)
sr = StarRocksAdapter(host="localhost", database="x")._get_dialect_queries(b, benchmark_slug="tpcds", connection=None)["51"]
dk = b.get_queries(dialect="duckdb")["51"]
norm = lambda rows: [tuple(float(v) if isinstance(v, Decimal) else str(v) if v is not None and not isinstance(v, (int, float)) else v for v in r) for r in rows]
cx = pymysql.connect(host="localhost", port=9030, user="root", autocommit=True, init_command="SET sql_mode = CONCAT(@@sql_mode, ',PIPES_AS_CONCAT')")
cu = cx.cursor(); cu.execute("SHOW DATABASES"); dbs = [r[0] for r in cu.fetchall() if r[0].startswith("te_")]
cols = {"store_sales": "ss_item_sk,ss_sold_date_sk,ss_sales_price", "web_sales": "ws_item_sk,ws_sold_date_sk,ws_sales_price", "date_dim": "d_date_sk,d_date,d_month_seq"}
res = {}
print("SQL", sr)
for db in dbs:
    cu.execute(f"USE {db}"); cu.execute(sr); res[db] = norm(cu.fetchall())
    sums = []
    for t, c in cols.items():
        k = c.split(",")
        cu.execute(f"SELECT COUNT(*), COUNT(DISTINCT {k[0]}), SUM({k[2]}), COUNT({k[1]}) FROM {t}"); sums.append(cu.fetchone())
    print(db, len(res[db]), "table checks", sums)
    con = duckdb.connect()
    for t, c in cols.items():
        cu.execute(f"SELECT {c} FROM {t}"); rows = cu.fetchall()
        import pyarrow as pa
        con.register(t, pa.table({n: [r[i] for r in rows] for i, n in enumerate(c.split(","))}))
    res[db + "/duckdb"] = norm(con.execute(dk).fetchall())
    print("  matches DuckDB on the same rows:", res[db] == res[db + "/duckdb"])
for db in dbs:
    a, d = res[db], res[db + "/duckdb"]
    bad = [(i, x, y) for i, (x, y) in enumerate(zip(a, d)) if x != y]
    print(db, "differing rows vs DuckDB:", len(bad)); [print("   ", r) for r in bad[:3]]
for db in dbs:
    cu.execute(f"USE {db}"); cu.execute("EXPLAIN " + sr)
    print("## PLAN", db); print("\n".join(r[0] for r in cu.fetchall())[:6000])
