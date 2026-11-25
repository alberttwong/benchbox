import sys
from benchbox.core.transaction_primitives.benchmark import TransactionPrimitivesBenchmark as B
from benchbox.sql_compat.rules.execution_filter.starrocks_transaction_primitives import STARROCKS_TRANSACTION_PRIMITIVES_OPERATION_SKIPS as S
skipped = set(S); S.clear()
orig = B.execute_operation; seen = {}
def run(self, operation_id, connection, **kw):
    r = orig(self, operation_id, connection, **kw)
    ok = r.success and not r.status
    tag = "PASS" if ok else (r.status or "FAIL")
    print(f"OP {operation_id} was_skipped={operation_id in skipped} {tag} cleanup_ok={r.cleanup_success} :: {str(r.error or r.skip_reason or '')[:420]}", flush=True)
    for v in r.validation_results:
        if not v["passed"]: print("   VALIDATION", v["query_id"], "expected", v["expected_rows"], "actual", v["actual_rows"], v["sql"][:200].replace("\n", " "), flush=True)
    if not ok:
        try: self.reset(connection)
        except Exception as e: print("   RESET FAILED", str(e)[:200], flush=True)
    return r
B.execute_operation = run
sys.argv = ["benchbox", "run", "--platform", "starrocks", "--benchmark", "transaction_primitives", "--scale", "0.01", "--phases", "generate,load,power", "--platform-option", "port=9030", "--platform-option", "http_port=8040", "--non-interactive"]
from benchbox.cli.app import main
main()
