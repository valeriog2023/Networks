from pybatfish.client.asserts import (assert_no_incompatible_bgp_sessions,
                                      assert_no_incompatible_ospf_sessions,
                                      assert_no_unestablished_bgp_sessions)


def test_no_unestablished_bgp_sessions(bf_session):
    assert_no_unestablished_bgp_sessions(session=bf_session)


def test_no_incompatible_bgp_sessions(bf_session):
    assert_no_incompatible_bgp_sessions(session=bf_session)


def test_no_incompatible_ospf_sessions(bf_session):
    assert_no_incompatible_ospf_sessions(session=bf_session)
