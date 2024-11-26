from pybatfish.datamodel.flow import (  # isort:skip noqa
    HeaderConstraints,
    PathConstraints,
)

import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")

from utils.bf_setup import create_bf_session

bf = create_bf_session("007_acls")

# Examples

df = (
    bf.q.findMatchingFilterLines(
        headers=HeaderConstraints(srcIps="10.2.10.1"), action="permit"
    )
    .answer()
    .frame()
)

# Set display options of column width
import pandas as pd

pd.set_option("display.max_colwidth", None)

# Show/filter entries matched
df[["Node", "Line"]]
