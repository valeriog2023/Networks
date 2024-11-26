import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")

from pybatfish.client.asserts import (HeaderConstraints, assert_flows_succeed,
                                      assert_no_duplicate_router_ids,
                                      assert_no_incompatible_bgp_sessions,
                                      assert_no_incompatible_ospf_sessions,
                                      assert_no_unestablished_bgp_sessions)

from utils.bf_setup import create_bf_session

bf = create_bf_session("013_assertions")

# Raise an exception if there are unestablished BGP sessions
assert_no_unestablished_bgp_sessions(session=bf)

# Raise an exception if incompatible BGP sessions are found
assert_no_incompatible_bgp_sessions(session=bf)

# Raise an exception if there incompatible OSPF sessions
assert_no_incompatible_ospf_sessions(session=bf)

# Raise an exception if there are duplicate router IDs
assert_no_duplicate_router_ids(session=bf)

# Raise an exception if any of the flows fail
assert_flows_succeed(
    session=bf,
    startLocation="/core1/",
    headers=HeaderConstraints(
        srcIps="0.0.0.0/0",
        dstIps="10.2.10.0/24, 10.2.20.0/24, 10.2.30.0/24, 10.2.40.0/24",
    ),
)
