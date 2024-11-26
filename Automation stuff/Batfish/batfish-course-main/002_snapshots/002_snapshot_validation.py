import logging
import sys
from pathlib import Path

from pybatfish.client.session import Session
from rich import print as rprint

BF_SNAPSHOT_NAME = "001_base"
BF_SNAPSHOT_PATH = f"{Path(__file__).parent.parent}/snapshots/{BF_SNAPSHOT_NAME}"

logging.getLogger("pybatfish").setLevel(logging.ERROR)

bf = Session(host="batfish.packetcoders.io")

bf.init_snapshot(BF_SNAPSHOT_PATH, overwrite=True)

# Snapshot validation

# File Parse Status
file_parse_status = bf.q.fileParseStatus().answer()

# Parse Warnings
parse_warnings = bf.q.parseWarning().answer()

# Init Issues
init_issues = bf.q.initIssues().answer()

# Exit if any issues found
if not init_issues.frame().empty:
    rprint(":cross_mark: Validation issues found. Exiting.")
    sys.exit(1)
