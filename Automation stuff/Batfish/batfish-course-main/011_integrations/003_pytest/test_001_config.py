from pybatfish.client.asserts import assert_no_duplicate_router_ids


def test_config_interface_mtu(bf_session):
    df = (
        bf_session.q.interfaceProperties(properties="MTU", nodes="/core/")
        .answer()
        .frame()
        .query("MTU != 1500")
    )
    if not df.empty:
        raise AssertionError(df)


def test_config_ntp(bf_session):
    expected_ntp_servers = {"10.1.30.101", "10.1.30.102"}

    def is_ntp_valid(ntp_servers):
        return expected_ntp_servers == set(ntp_servers)

    df = bf_session.q.nodeProperties(properties="NTP_Servers").answer().frame()
    df["ntp_valid"] = df["NTP_Servers"].apply(is_ntp_valid)

    df = df.query("ntp_valid == False")

    if not df.empty:
        raise AssertionError(df[["Node", "ntp_valid", "NTP_Servers"]])


def test_config_duplicate_ips(bf_session):
    df = bf_session.q.ipOwners(duplicatesOnly=True).answer().frame()
    if not df.empty:
        raise AssertionError(df)


def test_config_unused_structures(bf_session):
    df = bf_session.q.unusedStructures().answer().frame()
    if not df.empty:
        raise AssertionError(df)


def test_config_ospf_hello_interval(bf_session):
    df = (
        bf_session.q.ospfInterfaceConfiguration()
        .answer()
        .frame()
        .query("OSPF_Hello_Interval != 10")
    )
    if not df.empty:
        raise AssertionError(df)


def test_config_bgp_ebgp_multipath(bf_session):
    df = (
        bf_session.q.bgpProcessConfiguration()
        .answer()
        .frame()
        .query("Multipath_EBGP != True")
    )
    if not df.empty:
        raise AssertionError(df)


def test_config_no_duplicate_router_ids(bf_session):
    assert_no_duplicate_router_ids(session=bf_session)
