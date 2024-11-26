import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("003_control_plane")

# Session Status (connectivity, configuration summary)
# NOT_COMPATIBLE, NOT_ESTABLISHED, ESTBLISHED
bf.q.bgpSessionStatus().answer().frame()
bf.q.bgpSessionStatus(status="!ESTABLISHED").answer().frame()

# Session Compatability (configuration validation)
bf.q.bgpSessionCompatibility().answer().frame()
bf.q.bgpSessionCompatibility(status="!UNIQUE_MATCH").answer().frame()

# Filter BGP ASNs that are not in our ASN list
bf.q.bgpPeerConfiguration().answer().frame().query(
    "Remote_AS not in [64521, 64522, 64530]"
)
