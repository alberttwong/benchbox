import json
import os
import sys

from benchbox.core.transaction_primitives.benchmark import TransactionPrimitivesBenchmark
from benchbox.core.write_primitives.benchmark import WritePrimitivesBenchmark
from benchbox.sql_compat.rules.execution_filter.clickhouse_write_primitives import (
    CLICKHOUSE_WRITE_PRIMITIVES_OPERATION_SKIPS as SKIPS,
)

skipped = set(SKIPS)
SKIPS.clear()
out = open(os.environ["PROBE_OUT"], "a", encoding="utf-8")


def wrap(cls):
    original = cls.execute_operation

    def execute_operation(self, operation_id, connection, **kwargs):
        r = original(self, operation_id, connection, **kwargs)
        out.write(
            json.dumps(
                {
                    "op": operation_id,
                    "was_skipped": operation_id in skipped,
                    "status": r.status,
                    "success": r.success,
                    "error": str(r.error or "")[:600],
                    "skip": str(r.skip_reason or "")[:300],
                }
            )
            + "\n"
        )
        out.flush()
        return r

    cls.execute_operation = execute_operation


wrap(WritePrimitivesBenchmark)
wrap(TransactionPrimitivesBenchmark)
from benchbox.cli.app import main

sys.exit(main())
