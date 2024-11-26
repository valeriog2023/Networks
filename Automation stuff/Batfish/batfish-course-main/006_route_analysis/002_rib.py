import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("004_routing")

# Examples

# BGP RIB
bf.q.bgpRib().answer().frame().iloc[0]

# Filtering columns instead of Batfish inputs
bf.q.bgpRib(network="10.2.10.0/24", nodes="nxos-core1").answer().frame()[
    ["Node", "Next_Hop", "AS_Path"]
]
