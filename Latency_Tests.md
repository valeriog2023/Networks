# PING
Ping is a standard latency test tool available on all operating systems.
It measures the round trip time (RTT) between your PC and the target you specify (domain or IP address).
RTT is the time it takes for the ping packet to reach the target plus the time it takes to return the result,
so it measures the total latency to get a response from a server, PC, router or internet site.

By default, a ping command tests latency by sending four ICMP Echo Request packets
to the destination which responds back with ICMP Echo Reply packets which are then used to calculate latency.
Note: Most linux use UDP PING and they set the TTL in the packet

Advantages
The main advantage of this method is its simplicity.

Limitations
ICMP packets may be blocked by an intermediate firewall.
ICMP protocol may be handled with low priority by intermediate routers.
Round Trip Measure does not allow to get differentiate either direction latency.


# One-Way Active Measurement Protocol (OWAMP RFC 4656)
It is basically a tool used to measure one way latency between two endpoint
It requires:
- both endpoints to be connected to a reliable time source (ideally GPS/ptp/pps)
- same owamp software installed in both endpoints

Compared to ping/traceroute, OWAMP tests network latency in one direction and
does not rely on the ICMP protocol to calculate latency.

How OWAMP works
OWAMP provides more precise network latency measurements by using UDP packets to test latency in one direction.
You can fine tune your latency tests to better align with your specific requirements and use case.
For example, you can define the size of latency test packets,
the interval between two consecutive packets in a test, as well as the number of packets per test.

OWAMP latency test results are also more detailed than ping or traceroute. It provides the minimum, median,
and maximum value of the network latency between your source and the targeted destination
(as well as other useful data like one-way jitter and packet loss).
OWAMP latency testing also supports security authentication mechanisms.

One more limitation: OWAMP does not properly support NAT (Network Address Translation)

Advantages:
- One way network latency measurement
- High accuracy latency results
Limitations:
- Need OWAMP latency test capabilities at both ends
- Requires proper clock synchronization to measure one-way latency
- No NAT support

# Two-Way Active Measurement Protocol (TWAMP RFC 5357)
TWAMP for bidirectional latency testing, is a variation of OWAMP.

How TWAMP works
TWAMP tests latency by first using TCP to establish a connection between the source and destination, then uses UDP packets to monitor the latency.
It also uses a client/server architecture and requires that the endpoints support the TWAMP latency test protocol.

As a variation of OWAMP, TWAMP share the same latency test advantages and disadvantages.


# Packet capture
You can setup a 2 scenario where packets are sniffed by a TAP switch at the entrance/exit
of a network and timestamped.
Assuming the timestamp is from a reliable time source you can check latency by analysing the
caputres and comparing the timestamps (this will require some analysis tool or scripting,
like wireshark, pandas, etc..)