import os

from benchbox.platforms.base.sql_execution import join_explain_rows
from benchbox.platforms.clickhouse.adapter import ClickHouseAdapter
from tests.integration import test_plan_capture_synthetic_parsers_live as t

a = ClickHouseAdapter(
    deployment_mode="server",
    host="localhost",
    port=9000,
    username="default",
    password="benchbox",
    database="default",
    capture_plans=True,
)
c = a.create_connection()
for _ in t._plan_tables_fixture(c.execute, t._CLICKHOUSE_DDL):
    for shape in t._SHAPES:
        for kind, stem in (("PLAN", "clickhouse_captured"), ("PIPELINE", "clickhouse_pipeline_captured")):
            raw = join_explain_rows(list(c.execute(f"EXPLAIN {kind} {t.shape_query(shape)}")))
            with open(os.path.join(os.environ["PLAN_OUT"], f"{stem}_{shape}.txt"), "w", encoding="utf-8") as f:
                f.write(raw)
