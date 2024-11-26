import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("002_config")

# Examples

# BGP Peers that are nhave a local AS of 64522 and a remote IP of 192.168.1.3
bf.q.bgpPeerConfiguration().answer().frame().query(
    "Local_AS == 64522 & Remote_IP == '192.168.1.3'"
).iloc[0]

# OSPF Interfaces that are not passive
bf.q.ospfInterfaceConfiguration().answer().frame().query("OSPF_Passive == False")
