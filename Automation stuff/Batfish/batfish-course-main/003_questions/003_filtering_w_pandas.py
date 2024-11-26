import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("001_base")

# Examples

# Convert Pandas DF into different dataformts
bf.q.bgpProcessConfiguration().answer().frame().to_csv()
bf.q.bgpProcessConfiguration().answer().frame().to_html()
bf.q.bgpProcessConfiguration().answer().frame().to_dict(orient="records")

# Show row using row index.
bf.q.bgpProcessConfiguration().answer().frame().iloc[0]

# Return Boolean to show if DF is empty (or not)
bf.q.bgpProcessConfiguration().answer().frame().empty

# Return rows only that match a Router_ID of 192.168.1.1
bf.q.bgpProcessConfiguration().answer().frame().query("Router_ID == '192.168.1.1'")

# Pandas display options
import pandas as pd

pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)
pd.set_option("display.width", 1000)
pd.set_option("display.max_colwidth", None)
