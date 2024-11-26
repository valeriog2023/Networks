import sys
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}")


from utils.bf_setup import create_bf_session

bf = create_bf_session("002_config")

# Examples

# Node Configuration
bf.q.nodeProperties().answer().frame()

# Filter based upon question parameters
bf.q.nodeProperties(nodes="/core/").answer().frame()
bf.q.nodeProperties(nodes="/core/", properties="/Interfaces/").answer().frame()
bf.q.nodeProperties(nodes="/core/", properties="/NTP_Servers/").answer().frame()

# Validate NTP servers are correct

# Get the full result
df = bf.q.nodeProperties().answer().frame()

# Define expected NTP servers
expected_ntp_servers = {"10.1.30.101", "10.1.30.102"}

# Define function to validate NTP servers
def is_ntp_valid(ntp_servers):
    return expected_ntp_servers == set(ntp_servers)


# Apply function to dataframe
df["ntp_valid"] = df["NTP_Servers"].apply(is_ntp_valid)

# Show results
print(df[["Node", "ntp_valid"]])
