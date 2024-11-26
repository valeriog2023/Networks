from pathlib import Path

from pybatfish.client.session import Session

bf = Session(host="batfish.packetcoders.io")

# Build path for both snapshots
REFERENCE_SNAPSHOT = "009a_acl_compare"
SNAPSHOT = "009b_acl_compare"

REFERENCE_PATH = f"{Path(Path.cwd())}/snapshots/{REFERENCE_SNAPSHOT}"
SNAPSHOT_PATH = f"{Path(Path.cwd())}/snapshots/{SNAPSHOT}"

# Initialize both snapshots
bf.init_snapshot(REFERENCE_PATH, name="reference", overwrite=True)
bf.init_snapshot(SNAPSHOT_PATH, name="snapshot", overwrite=True)

# Perform a diff of ACLs between the two snapshots
df = (
    bf.q.compareFilters()
    .answer(snapshot="snapshot", reference_snapshot="reference")
    .frame()
)

# Save the diff to an HTML file
df.to_html("acl_diff.html")
