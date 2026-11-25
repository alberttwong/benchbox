import pymysql
x=pymysql.connect(host="localhost",port=9030,user="root",autocommit=True,database="probe").cursor()
for n,s in [("RETURNING insert","INSERT INTO p VALUES(50,1) RETURNING id"),("RETURNING update","UPDATE p SET v=3 WHERE id=1 RETURNING id"),("RETURNING delete","DELETE FROM p WHERE id=1 RETURNING id"),
 ("MERGE","MERGE INTO p t USING q s ON t.id=s.id WHEN MATCHED THEN UPDATE SET v=s.v WHEN NOT MATCHED THEN INSERT (id,v) VALUES (s.id,s.v)"),("COPY","COPY p FROM '/tmp/a.csv'")]:
    try: x.execute(s); print("PROBE",n,"OK",x.fetchall())
    except Exception as e: print("PROBE",n,"FAIL",str(e)[:300])
