import logging
from pathlib import Path

import pytest
from pybatfish.client.session import Session

logging.getLogger("pybatfish").setLevel(logging.ERROR)

SNAPSHOT = "014_pytest"


@pytest.fixture(scope="session")
def bf_session():
    bf = Session(host="batfish.packetcoders.io")

    snapshot_path = f"{Path(Path.cwd())}/snapshots/{SNAPSHOT}"

    bf.init_snapshot(snapshot_path, name="base", overwrite=True)

    return bf
