import pymysql
P=[("UPDATE in txn",["BEGIN","UPDATE p SET v=2 WHERE id=1","COMMIT"]),("DELETE in txn",["BEGIN","DELETE FROM p WHERE id=2","COMMIT"]),
("two INSERTs same table",["BEGIN","INSERT INTO p VALUES(10,1)","INSERT INTO p VALUES(11,1)","COMMIT"]),
("read own write",["BEGIN","INSERT INTO p VALUES(12,1)","SELECT COUNT(*) FROM p","COMMIT"]),
("insert-select own write",["BEGIN","INSERT INTO p VALUES(13,1)","INSERT INTO q SELECT * FROM p","COMMIT"]),
("SAVEPOINT",["BEGIN","SAVEPOINT sp1","ROLLBACK"]),("CREATE TEMP TABLE",["BEGIN","CREATE TEMP TABLE t1 (id INT)","ROLLBACK"]),("TRUNCATE in txn",["BEGIN","TRUNCATE TABLE q","COMMIT"]),
("DELETE WHERE TRUE",["DELETE FROM d WHERE TRUE"]),("DELETE IS NOT NULL",["DELETE FROM d WHERE id IS NOT NULL"])]
def c(db=None): return pymysql.connect(host="localhost",port=9030,user="root",autocommit=True,database=db)
x=c().cursor(); x.execute("SELECT current_version()"); print(x.fetchone()); x.execute("CREATE DATABASE IF NOT EXISTS probe")
x=c("probe").cursor()
for t in("p","q"): x.execute(f"CREATE TABLE IF NOT EXISTS {t}(id INT NOT NULL,v INT) PRIMARY KEY(id) DISTRIBUTED BY HASH(id) BUCKETS 1 PROPERTIES('replication_num'='1')"); x.execute(f"INSERT INTO {t} VALUES(1,1),(2,2)")
x.execute("CREATE TABLE IF NOT EXISTS d(id VARCHAR(9) NOT NULL,v INT) DUPLICATE KEY(id) DISTRIBUTED BY HASH(id) BUCKETS 1 PROPERTIES('replication_num'='1')"); x.execute("INSERT INTO d VALUES('a',1)")
for n,ss in P:
    k=c("probe").cursor(); r="OK"
    for s in ss:
        try: k.execute(s); k.fetchall()
        except Exception as e: r=f"FAIL at [{s}]: {e}"; break
    print(f"PROBE {n}: {r}")
x.execute("SELECT COUNT(*) FROM d"); print("rows left in d:",x.fetchone())
