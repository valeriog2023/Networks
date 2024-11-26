import sys
from pathlib import Path

# Update sys.path so we can install the utils package
sys.path.append(f"{Path(__file__).parent.parent}")


from pybatfish.client.session import Session

bf = Session(host="batfish.packetcoders.io")

# Build path for both snapshots
SNAPSHOT = "011_snapshot_forking"

SNAPSHOT_PATH = f"{Path(Path.cwd())}/snapshots/{SNAPSHOT}"

bf = Session(host="batfish.packetcoders.io")

# Initialize both snapshots
bf.init_snapshot(SNAPSHOT_PATH, name="base", overwrite=True)

# View Snapshots
bf.list_snapshots()

# Get active snapshot
bf.get_snapshot()

# View L3 edges
bf.q.edges(edgeType="layer3").answer().frame()

# Single Device Failuer
bf.fork_snapshot(
    "base",
    name="failure-snapshot-core1",
    deactivate_nodes=["nxos-core1"],
    overwrite=True,
)

# View Snapshots
bf.list_snapshots()

# Get active snapshot
bf.get_snapshot()

# View L3 edges (no core1 edges)
bf.q.edges(edgeType="layer3").answer().frame()
