import logging
from pathlib import Path

from pybatfish.client.session import Session
from rich import print as rprint

BF_SNAPSHOT_NAME = "001_base"
BF_SNAPSHOT_PATH = f"{Path(__file__).parent.parent}/snapshots/{BF_SNAPSHOT_NAME}"

logging.getLogger("pybatfish").setLevel(logging.ERROR)

bf = Session(host="batfish.packetcoders.io")

bf.init_snapshot(BF_SNAPSHOT_PATH, overwrite=True)

rprint(bf)
