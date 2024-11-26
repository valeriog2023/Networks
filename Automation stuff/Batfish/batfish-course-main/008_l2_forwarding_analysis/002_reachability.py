import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("006_l2_forwarding")

from pybatfish.datamodel.flow import (  # isort:skip noqa
    HeaderConstraints,
    PathConstraints,
)

# Examples

from utils.bf_pprint import pprint_reachability

# Shows reachability from all nodes to all server.
# Shows 1st flow for each start location that is SUCCESSFUL.
df = (
    bf.q.reachability(
        pathConstraints=PathConstraints(startLocation="/core/"),
        headers=HeaderConstraints(
            srcIps="0.0.0.0/0", dstIps="10.2.10.0/24, 10.2.20.0/24, 10.2.30.0/24"
        ),
        actions="SUCCESS",
    )
    .answer()
    .frame()
)

pprint_reachability(df)

# Shows reachability from all nodes to all server.
# Shows 1st flow for each start location that FAILS.
df = (
    bf.q.reachability(
        pathConstraints=PathConstraints(startLocation="/core/"),
        headers=HeaderConstraints(
            srcIps="0.0.0.0/0", dstIps="10.2.10.0/24, 10.2.20.0/24, 10.2.30.0/24"
        ),
        actions="FAILURE",
    )
    .answer()
    .frame()
)

pprint_reachability(df)

# Validate against not using a layer 1 topology file
bf = create_bf_session("005_l3_forwarding")

df = (
    bf.q.reachability(
        pathConstraints=PathConstraints(startLocation="/core/"),
        headers=HeaderConstraints(
            srcIps="0.0.0.0/0", dstIps="10.2.10.0/24, 10.2.20.0/24, 10.2.30.0/24"
        ),
        actions="FAILURE",
    )
    .answer()
    .frame()
)

pprint_reachability(df)
