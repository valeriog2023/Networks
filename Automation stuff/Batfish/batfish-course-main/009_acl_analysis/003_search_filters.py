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
    bf.q.searchFilters(
        headers=HeaderConstraints(
            srcIps="0.0.0.0/0 \ 10.2.10.0-10.2.30.255",
            dstIps="8.8.8.8,8.8.4.4",
            applications="udp/53",
        ),
        nodes="/nxos-core/",
        filters="ACL-EXAMPLE",
        action="permit",
    )
    .answer()
    .frame()
)
