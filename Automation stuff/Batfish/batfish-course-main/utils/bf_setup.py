import logging
from pathlib import Path

from pybatfish.client.session import Session

logging.getLogger("pybatfish").setLevel(logging.ERROR)


def create_bf_session(snapshot: str):
    bf = Session(host="batfish.packetcoders.io")

    snapshot_path = f"{Path(Path.cwd())}/snapshots/{snapshot}"

    bf.init_snapshot(snapshot_path, overwrite=True)

    return bf
