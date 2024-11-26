import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session(snapshot="001_base")

# Examples

# Get the full result
bf.q.bgpProcessConfiguration().answer().frame()

# Filter based upon question parameters
bf.q.bgpProcessConfiguration(nodes="/core/").answer().frame()

# Filter based upon question parameters
(
    bf.q.bgpProcessConfiguration(nodes="/core/", properties="/Neighbors/")
    .answer()
    .frame()
)
