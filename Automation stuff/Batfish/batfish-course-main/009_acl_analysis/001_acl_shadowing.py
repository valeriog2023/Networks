import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")

from utils.bf_setup import create_bf_session

bf = create_bf_session("007_acls")

# Examples

df = bf.q.filterLineReachability().answer().frame()
