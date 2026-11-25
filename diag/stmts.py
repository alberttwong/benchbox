from clickhouse_driver import Client

c = Client("localhost", port=9000, password="benchbox")
print("VERSION", c.execute("SELECT version()"))
c.execute("CREATE TABLE IF NOT EXISTS default.p (id Int32, v Nullable(Int32)) ENGINE=MergeTree ORDER BY id")
for s in [
    "BEGIN",
    "BEGIN TRANSACTION",
    "START TRANSACTION",
    "SET TRANSACTION ISOLATION LEVEL READ COMMITTED",
    "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT s1",
]:
    try:
        print("STMT", s, "OK", c.execute(s))
    except Exception as e:
        print("STMT", s, "FAIL", str(e).split("Stack trace")[0].strip()[:400].replace("\n", " "))
