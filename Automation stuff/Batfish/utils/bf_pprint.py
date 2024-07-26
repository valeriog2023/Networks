# pretty prints the answer from bfq.traceroute()
#
# Courtesy of PacketCoders, from: https://github.com/packetcoders/batfish-course/blob/main/utils/bf_pprint.py
#

import itertools

from rich import box, print
from rich.console import Console
from rich.table import Table

console = Console()


def pprint_traceroute(answer):
    for flow_n, flow in enumerate(answer["Flow"]):
        print("# FLOW = {}\n".format(flow))
        for trace_n, trace in enumerate(answer["Traces"][flow_n]):
            print("\n-- TRACE{}".format(trace_n))
            for steps in trace:
                print(steps)


# pretty prints the answer from bfq.differentialReachability()
# newly updated
def pprint_diff_reachability(answer):
    # Print flow summary
    for flow_n, flow in enumerate(answer["Flow"]):
        print(f"{flow}")

    # Loop over flows
    for flow_n, flow in enumerate(answer["Flow"]):
        # Create table
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column(
            "[bold magenta]FLOW: [/bold magenta][blue]{}[/blue]".format(flow), width=100
        )
        reference_traces = list(answer["Reference_Traces"][flow_n])
        snapshot_traces = list(answer["Snapshot_Traces"][flow_n])

        # Add trace counts
        table.add_row(
            "[bold white]Reference Traces (count={})[/bold white]".format(
                str(answer.iloc[flow_n].Reference_TraceCount)
            ),
            "[bold white]Snapshot Traces (count={})[/bold white]".format(
                str(answer.iloc[flow_n].Snapshot_TraceCount)
            ),
        )

        # Zip traces and add to rows
        for zipped_flow_traces in list(
            itertools.zip_longest(reference_traces, snapshot_traces, fillvalue="")
        ):
            table.add_row("", "")
            table.add_row(str(zipped_flow_traces[0]), str(zipped_flow_traces[1]))

        console.print(table)


# pretty prints the answer from bfq.reachability()
def pprint_reachability(answer):
    print(f"Flow Summary")
    for index, row in answer.iterrows():
        print(f"Flow: {row['Flow']} (Trace Count:{row['TraceCount']})")
    print("==========")
    for index, row in answer.iterrows():
        print(f"Flow: {row['Flow']} (Trace Count:{row['TraceCount']})")
        for count, trace in enumerate(row["Traces"], start=1):
            print(f"\nTrace #{count}")
            print(f"{trace}")
        print("----")
