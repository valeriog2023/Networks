#!/usr/bin/env python3

try:
    import IPython
except ModuleNotFoundError:
    import code

import logging
import os

import click
import pandas as pd
from pybatfish.client.session import Session

from pybatfish.datamodel.flow import (  # isort:skip noqa
    HeaderConstraints,
    PathConstraints,
)

from tenacity import before_nothing  # isort:skip noqa

from bf_pprint import pprint_reachability, pprint_diff_reachability  # isort:skip

os.environ["PYTHONINSPECT"] = "TRUE"

logging.getLogger("pybatfish").setLevel(logging.WARN)

BF_HOST = "batfish.packetcoders.io"


@click.command()
@click.option(
    "--snapshot_path",
    "-p",
    type=click.Path(),
    required=True,
    help="Snapshot path.",
)
@click.option(
    "--bf_host",
    "-a",
    required=False,
    default=BF_HOST,
    show_default=True,
    help="Batfish host.",
)
def main(snapshot_path, bf_host):
    """Batfish Snapshot Importer"""
    bf = Session(host=bf_host)

    bf.init_snapshot(snapshot_path, overwrite=True)

    if globals().get("IPython"):
        IPython.embed()
    else:
        code.interact(local=dict(globals(), **locals()))


# def delete_bf_data():
#    for snapshot in bf_session.list_snapshots():
#        bf_session.delete_snapshot(snapshot)
#    for network in bf_session.list_networks():
#        bf_session.delete_network(network)


def update_pd_display():
    # pd.set_option("display.max_rows", 500)
    # pd.set_option("display.max_columns", 15)
    # pd.set_option("display.width", 300)
    pd.set_option("display.max_colwidth", 1)


if __name__ == "__main__":
    # delete_bf_data()
    update_pd_display()
    main()
