import sys
from pathlib import Path

# Update sys.path so we can install the utils package
sys.path.append(f"{Path(__file__).parent.parent}")

from pybatfish.client.session import Session

from utils.bf_pprint import pprint_diff_reachability

bf = Session(host="batfish.packetcoders.io")

# Build path for both snapshots
REFERENCE_SNAPSHOT = "010a_diff_reachability"
SNAPSHOT = "010b_diff_reachability"

REFERENCE_PATH = f"{Path(Path.cwd())}/snapshots/{REFERENCE_SNAPSHOT}"
SNAPSHOT_PATH = f"{Path(Path.cwd())}/snapshots/{SNAPSHOT}"

# Initialize both snapshots
bf.init_snapshot(REFERENCE_PATH, name="reference", overwrite=True)
bf.init_snapshot(SNAPSHOT_PATH, name="snapshot", overwrite=True)

df = (
    bf.q.differentialReachability()
    .answer(snapshot="snapshot", reference_snapshot="reference")
    .frame()
)

pprint_diff_reachability(df)
