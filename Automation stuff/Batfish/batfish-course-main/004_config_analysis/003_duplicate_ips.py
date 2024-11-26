import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("002_config")

# Examples

# Show all IP Owners
bf.q.ipOwners().answer().frame()

# Show only duplicates
bf.q.ipOwners(duplicatesOnly=True).answer().frame()

# IP Checker
def check_ip(ip: str):
    return bf.q.ipOwners().answer().frame().query(f"IP == '{ip}'")


check_ip("10.2.30.1")
