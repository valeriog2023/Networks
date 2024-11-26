import logging
from pathlib import Path

from pybatfish.client.session import Session

logging.getLogger("pybatfish").setLevel(logging.ERROR)


# Build path for both snapshots
REFERENCE_SNAPSHOT = "001_base"
SNAPSHOT = "008a_diff_comparision"

REFERENCE_PATH = f"{Path(Path.cwd())}/snapshots/{REFERENCE_SNAPSHOT}"
SNAPSHOT_PATH = f"{Path(Path.cwd())}/snapshots/{SNAPSHOT}"

bf = Session(host="batfish.packetcoders.io")

# Initialize both snapshots
bf.init_snapshot(REFERENCE_PATH, name="reference", overwrite=True)
bf.init_snapshot(SNAPSHOT_PATH, name="snapshot", overwrite=True)

# Perform a diff between the two snapshots for BGP sessions
df = (
    bf.q.bgpSessionStatus()
    .answer(
        reference_snapshot="reference",
        snapshot="snapshot",
    )
    .frame()
)

df.iloc[0]

# Perform a diff between the two snapshots for interface properties
df = (
    bf.q.interfaceProperties()
    .answer(reference_snapshot="reference", snapshot="snapshot")
    .frame()
)
df[["Interface", "Reference_Incoming_Filter_Name", "Snapshot_Incoming_Filter_Name"]]
