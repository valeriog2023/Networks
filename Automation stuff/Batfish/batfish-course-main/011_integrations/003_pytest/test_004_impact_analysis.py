import pandas as pd
import pytest
from pybatfish.datamodel.flow import HeaderConstraints

NODES = [
    "nxos-core1",
    "nxos-core2",
    "nxos-aggr1",
    "nxos-aggr2",
    "qfx-access1",
    "ios-access2",
    "eos-access3",
]

pd.set_option("display.max_colwidth", None)


@pytest.mark.parametrize("node", NODES)
def test_impact_analysis_node(bf_session, node):
    bf_session.fork_snapshot(
        "base",
        name="failure-snapshot",
        deactivate_nodes=[node],
        overwrite=True,
    )

    reach_diff = (
        bf_session.q.differentialReachability(
            headers=HeaderConstraints(dstIps="10.2.10.1, 10.2.20.1, 10.2.30.1")
        )
        .answer(snapshot="failure-snapshot", reference_snapshot="base")
        .frame()
    )

    if not reach_diff.empty:
        raise AssertionError(reach_diff.Flow)
