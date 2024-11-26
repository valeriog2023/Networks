import sys
from pathlib import Path

from rich import print as rprint

# Update sys.path so we can install the utils package
sys.path.append(f"{Path(__file__).parent.parent}")

import pandas as pd
from pybatfish.client.session import Session
from pybatfish.datamodel.flow import HeaderConstraints

# Update sys.path so we can install the utils package
sys.path.append(f"{Path(__file__).parent.parent}")

pd.set_option("display.max_colwidth", None)

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


for node in bf.q.nodeProperties().answer().frame().Node:
    bf.fork_snapshot(
        "base",
        name="failure-snapshot",
        deactivate_nodes=[node],
        overwrite=True,
    )

    reach_diff = (
        bf.q.differentialReachability(
            headers=HeaderConstraints(dstIps="10.2.10.1, 10.2.20.1, 10.2.30.1")
        )
        .answer(snapshot="failure-snapshot", reference_snapshot="base")
        .frame()
    )

    if reach_diff.empty:
        rprint(f":white_check_mark: Deactivating node {node} has no impact")
    else:
        rprint(
            f":cross_mark: Deactivating node {node} | Flow differences: \n {reach_diff.Flow}"
        )


for interface in bf.q.interfaceProperties().answer().frame().Interface:
    bf.fork_snapshot(
        "base",
        name="failure-snapshot",
        deactivate_interfaces=[interface],
        overwrite=True,
    )

    reach_diff = (
        bf.q.differentialReachability(
            headers=HeaderConstraints(dstIps="10.2.10.1, 10.2.20.1, 10.2.30.1")
        )
        .answer(snapshot="failure-snapshot", reference_snapshot="base")
        .frame()
    )

    if reach_diff.empty:
        rprint(f":white_check_mark: Deactivating interface {interface} has no impact")
    else:
        rprint(
            f":cross_mark: Deactivating node {interface} | Flow differences: \n {reach_diff.Flow}"
        )
