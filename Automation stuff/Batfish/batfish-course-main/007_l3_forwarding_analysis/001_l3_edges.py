import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("005_l3_forwarding")

# Examples

# Layer 3 Edges
bf.q.edges(edgeType="layer3").answer().frame()

# No Layer 1 Edges
bf.q.edges(edgeType="layer1").answer().frame()
