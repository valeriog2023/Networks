import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("004_routing")

# Examples

# Centrlized route analysis
bf.q.routes().answer().frame()

# Filter routes based on network
bf.q.routes(network="10.2.2.0/24").answer().frame()

# Filter routes based on protocol
bf.q.routes(protocols="ospf").answer().frame()

# Filter routes based on protocol, count number of routes
len(bf.q.routes(protocols="ospf").answer().frame())

# Filter for loopbacks learnt via OSPF
df_ospf_lo = (
    bf.q.routes(
        protocols="ospf", network="192.168.1.0/16", prefixMatchType="LONGER_PREFIXES"
    )
    .answer()
    .frame()
)

# Will show 12 routes, should be 14.
len(df_ospf_lo)
