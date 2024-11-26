import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("003_control_plane")

# Get all OSPF Sessions
bf.q.ospfSessionCompatibility().answer().frame()

# Get all OSPF Sessions that are not ESTABLISHED
bf.q.ospfSessionCompatibility(statuses="!ESTABLISHED").answer().frame()

# Filter OSPF interfaces to show dead interval values
bf.q.ospfInterfaceConfiguration(
    nodes="/core1|aggr2/", properties="OSPF_Dead_Interval"
).answer().frame()
