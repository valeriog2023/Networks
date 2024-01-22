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

# Short Notes on PTP

**Note:** while PTP is measured in nanoseconds, the actual accuracy is around a microsecond (for sub nanoseconds convergence you might need extension to ptp like white rabbit)
Also note, that other protocols are used in the time synch area like **PPS**
which is used not for time keeping but to give a precise measure of when a period starts 

**Two** separate delay values must be determined: 
*  the delay from the master to slave
*  the delay from the slave to master.

To calculate the delay from the master to slave:
*  T1 is the initial timestamp, and is the exact time the **sync** message is sent by the master. Since T1 is an accurate recording of when the sync message was transmitted via the Ethernet port, it is sent in the **follow-up** message.

*  T2 is the second timestamp, and is the exact time the slave receives the sync message.

Once both T1 and T2 are available at the slave, the delay value between the master and the slave can be determined through the calculation **T2 – T1**.

To calculate the delay from the slave to the master:
*  T3 is the third timestamp, and is the exact time the **delay request** message is sent from the slave. 
*  T4 is the fourth and final timestamp, and is the exact time the master receives the **delay request** message. T4 is notified to the client with a **delay response** message

Once both T3 and T4 are available at the slave, the delay value between the slave and the master can be determined through the calculation **T4 – T3**.

Once both the master to slave, and slave to master differences are available at the slave, the one-way delay can be determined.   
```
One-way delay = (master to slave difference + slave to master difference) / 2

This can be simplified as:
Offset = ((T2 - T1) - (T4 - T3)) / 2
```



By utilising this offset, the slave clock can adjust its time to ensure it matches the master clock.

<img src="PTP Message exchange.png" alt="PTP Message exchange" style="height: 500px; width:600px;"/>

