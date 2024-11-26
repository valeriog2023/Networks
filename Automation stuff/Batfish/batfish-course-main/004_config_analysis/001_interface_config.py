import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("002_config")


# Interface Properites.
bf.q.interfaceProperties().answer().frame()

# Interface Properties filtered using question parameters.
bf.q.interfaceProperties(properties="MTU", nodes="/core/").answer().frame()

# Interface Properties filtered using question parameters and Pandas querying.
bf.q.interfaceProperties(properties="MTU", nodes="/core/").answer().frame().query(
    "MTU != 1500"
)


# Filtering Access VLANs to show uniqye VLANs in network.
set(bf.q.interfaceProperties().answer().frame().Access_VLAN)

# Filtering Interfaces to show only trunk interfaces.
bf.q.interfaceProperties().answer().frame().query(
    "Switchport_Mode == 'TRUNK'"
).Interface
