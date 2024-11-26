import sys
from pathlib import Path

from pybatfish.datamodel.flow import HeaderConstraints

sys.path.append(f"{Path(__file__).parent.parent}")

from utils.bf_setup import create_bf_session

bf = create_bf_session("007_acls")

# Examples

# Take the first flow from the inputs and show the outcome
df = (
    bf.q.testFilters(
        nodes="/core/",
        filters="ACL-EXAMPLE",
        headers=HeaderConstraints(
            srcIps="10.2.10.1", dstIps="1.1.1.1", ipProtocols=["UDP"], dstPorts="123"
        ),
    )
    .answer()
    .frame()
)

# Show the first row
df.iloc[0]

# Perform the same operation but provide a network to show the outcome.
# i.e that the first IP is selected from the block.
df = (
    bf.q.testFilters(
        nodes="/core/",
        filters="ACL-EXAMPLE",
        headers=HeaderConstraints(
            srcIps="10.2.10.0/24", dstIps="1.1.1.1", ipProtocols=["UDP"], dstPorts="123"
        ),
        startLocation="@vrf(default)",
    )
    .answer()
    .frame()
)

# Show the first row
df.iloc[0]
