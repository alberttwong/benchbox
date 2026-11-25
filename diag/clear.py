import os
import benchbox
from benchbox.core.tuning.metadata import TuningMetadataManager
from benchbox.core.tuning.interface import UnifiedTuningConfiguration
from benchbox.platforms.starrocks import StarRocksAdapter
a = StarRocksAdapter(host="localhost", port=9030, http_port=8040, database="cleartest")
c = a.create_connection(); m = TuningMetadataManager(a, connection=c)
assert m.save_unified_tunings(UnifiedTuningConfiguration()); assert m.write_tuned_run_marker()
def n():
    k = c.cursor(); k.execute("SELECT COUNT(*) FROM benchbox_tuning_metadata"); return k.fetchone()[0]
print("CLEAR before", n()); ok = m.clear_tunings(); print("CLEAR ok", ok, "after", n())
assert ok and n() == 0
