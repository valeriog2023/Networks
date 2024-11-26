import sys
from pathlib import Path

# Update sys.path so we can install the utils package
sys.path.append(f"{Path(__file__).parent.parent}")

from pybatfish.client.session import Session
from pybatfish.datamodel.flow import HeaderConstraints

from utils.bf_pprint import pprint_diff_reachability

# Update sys.path so we can install the utils package
sys.path.append(f"{Path(__file__).parent.parent}")

bf = Session(host="batfish.packetcoders.io")

# Build path for both snapshots
SNAPSHOT = "012_impact_analysis"

SNAPSHOT_PATH = f"{Path(Path.cwd())}/snapshots/{SNAPSHOT}"

bf = Session(host="batfish.packetcoders.io")

# Initialize both snapshots
bf.init_snapshot(SNAPSHOT_PATH, name="base", overwrite=True)

# View Snapshots
bf.list_snapshots()

# Get active snapshot
bf.get_snapshot()

# Single device failure
bf.fork_snapshot(
    "base",
    name="failure-snapshot",
    deactivate_nodes=["nxos-aggr1"],
    overwrite=True,
)

# Dual device failure
# bf.fork_snapshot(
#    "base",
#    name="failure-snapshot",
#    deactivate_nodes=["nxos-aggr1", "nxos-aggr2"],
#    overwrite=True,
# )

# View Snapshots
bf.list_snapshots()

# Perform differential reachability
reach_diff = (
    bf.q.differentialReachability(
        headers=HeaderConstraints(dstIps="10.2.10.1, 10.2.20.1, 10.2.30.1")
    )
    .answer(snapshot="failure-snapshot", reference_snapshot="base")
    .frame()
)

# Header restricted to dst ip of servers
pprint_diff_reachability(reach_diff)
