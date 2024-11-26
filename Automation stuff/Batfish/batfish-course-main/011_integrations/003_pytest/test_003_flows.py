from pybatfish.client.asserts import HeaderConstraints, assert_flows_succeed


# Raise an exception if any of the flows fail
def test_flows_succeed_to_server(bf_session):
    assert_flows_succeed(
        session=bf_session,
        startLocation="/core|aggr/",
        headers=HeaderConstraints(
            srcIps="0.0.0.0/0",
            dstIps="10.2.10.0/24, 10.2.20.0/24, 10.2.30.0/24",
        ),
    )


def test_flows_succeed_from_server(bf_session):
    assert_flows_succeed(
        session=bf_session,
        startLocation="/server/",
        headers=HeaderConstraints(
            srcIps="10.2.10.0/24, 10.2.20.0/24, 10.2.30.0/24",
            dstIps="0.0.0.0/0",
        ),
    )
