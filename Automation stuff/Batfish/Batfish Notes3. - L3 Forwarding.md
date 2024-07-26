# BATFISH NOTES 3


## BATFISH L3 FORWARD ANALYSIS

Batfish allows you to validate flows for the simulated topology through some **reachability tests** or virtual traceroutes.

Again, as a reminder Batfish is mainly L3 so there are limitations and caveats for L2

Because it is simulated, you can potentially test reachability between every single endpoint (IP address) in the network with a single question, and of course this by passes the complexity to run these tests in an actual network.

The questions available are:
- **Tracertoute**: suited to test individual flows
- **Bi-directional Traceroute**
- **Reachability**: suited to test flow blocks more than individual flows
- **Bi-drectional Reachability**
- **Loop Detection**
- **Multipath Consistency**


## L3 EDGES

How does Batfish know how the network devices are connected together? 

The Batfish builds the topology is via **L3 Edges**; it figures out the edges based on the IP addresses.. unfortunately this has an issue
with the L2 parts of the networks (because they have no IP addresses).  
This means that by default L2 is ignored, i.e. if there is a L2 switch in between one hop and the destination, Batfish will not know about that.


```
>>> bf.q.edges().answer()
          Interface                 IPs Remote_Interface          Remote_IPs
0   h1[Ethernet0/0]     ['192.168.9.1']  r9[Ethernet0/2]   ['192.168.9.254']
1   r1[Ethernet0/1]    ['192.168.12.1']  r2[Ethernet0/1]  ['192.168.12.254']
2   r2[Ethernet0/0]    ['192.168.23.2']  r3[Ethernet0/3]    ['192.168.23.3']
3   r2[Ethernet0/1]  ['192.168.12.254']  r1[Ethernet0/1]    ['192.168.12.1']
4   r2[Ethernet0/2]    ['192.168.24.2']  r4[Ethernet1/0]    ['192.168.24.4']
5   r3[Ethernet0/0]    ['192.168.34.3']  r4[Ethernet0/0]    ['192.168.34.4']
6   r3[Ethernet0/2]    ['192.168.35.3']  r5[Ethernet0/0]    ['192.168.35.5']
7   r3[Ethernet0/3]    ['192.168.23.3']  r2[Ethernet0/0]    ['192.168.23.2']
8   r4[Ethernet0/0]    ['192.168.34.4']  r3[Ethernet0/0]    ['192.168.34.3']
[...]
```



## HEADER SPACE AND HEADER CONTRAINTS
If you want to check multiple flows at the same time, you need to work with **Header Spaces** and you can think of it as a 3-dimension structure given by: **(Protocol, IP, Ports)**

When you start, the 3-dimensional will cover all Protocols/IPs and ports and you can start reducing it via: **Header Contraints**

**Note that you will use these both for forward analysis and also for ACL analysis**


## REACHABILITY
Batfish has a reachability question available: `bf.q.reachability()`, see: https://pybatfish.readthedocs.io/en/latest/notebooks/forwarding.html#Reachability

The main inputs we can use for the question are:
 - **Path Constraints**: here you can specify start locations, end locations, transit locations and forbidden locations 
 - **Header Constraints**: IP, Ports, Protocols
 - **Action**: Permit/Deny

```
>>> from pybatfish.datamodel.flow import (  
    HeaderConstraints,
    PathConstraints,
)

>>> df = bf.q.reachability(
   pathConstraints=PathConstraints(startLocation="r1"),       # this could be a list of devices or a regex match, e.g. startLocation = "/core/"
   headers=HeaderConstraints(
       srcIps="0.0.0.0/0", dstIps="6.6.6.6/32"                # you could have multiple values e.g.  dstIps="6.6.6.6/32, 5.5.5.5/32"
       ),
   actions="SUCCESS").answer().frame()                        # Alternative is FAILURE


>>> df.iloc[0]
                                                Flow                                             Traces TraceCount
0  start=r1 [10.0.0.0->6.6.6.6 ICMP (type=8, code...  [((ORIGINATED(default), FORWARDED(Forwarded ou...          2   


>>> df.iloc[0]['Flow']
Flow(dscp=0, dstIp='6.6.6.6', dstPort=None, ecn=0, fragmentOffset=0, icmpCode=0, icmpVar=8, ingressInterface=None, ingressNode='r1', ingressVrf='default', ipProtocol='ICMP', packetLength=512, srcIp='10.0.0.0', srcPort=None, tcpFlagsAck=0, tcpFlagsCwr=0, tcpFlagsEce=0, tcpFlagsFin=0, tcpFlagsPsh=0, tcpFlagsRst=0, tcpFlagsSyn=0, tcpFlagsUrg=0)

>>> df.iloc[0]['Traces']
ListWrapper([((ORIGINATED(default), FORWARDED(Forwarded out interface: Ethernet0/1 with resolved next-hop IP: 192.168.12.254, Routes: [static (Network: 0.0.0.0/0, Next Hop: ip 192.168.12.254)]), TRANSMITTED(Ethernet0/1)), (RECEIVED(Ethernet0/1), FORWARDED(Forwarded out interface: Ethernet0/2 with resolved next-hop IP: 192.168.24.4, Routes: [ospf (Network: 6.6.6.0/24, Next Hop: interface Ethernet0/2 ip 192.168.24.4)]), TRANSMITTED(Ethernet0/2)), (RECEIVED(Ethernet1/0), FORWARDED(Forwarded out interface: Ethernet0/1 with resolved next-hop IP: 192.168.46.6, Routes: [ospf (Network: 6.6.6.0/24, Next Hop: interface Ethernet0/1 ip 192.168.46.6)]), TRANSMITTED(Ethernet0/1)), (RECEIVED(Ethernet0/0), ACCEPTED(Loopback0))), ((ORIGINATED(default), FORWARDED(Forwarded out interface: Ethernet0/1 with resolved next-hop IP: 192.168.12.254, Routes: [static (Network: 0.0.0.0/0, Next Hop: ip 192.168.12.254)]), TRANSMITTED(Ethernet0/1)), (RECEIVED(Ethernet0/1), FORWARDED(Forwarded out interface: Ethernet0/2 with resolved next-hop IP: 192.168.24.4, Routes: [ospf (Network: 6.6.6.0/24, Next Hop: interface Ethernet0/2 ip 192.168.24.4)]), TRANSMITTED(Ethernet0/2)), (RECEIVED(Ethernet1/0), FORWARDED(Forwarded out interface: Ethernet0/2 with resolved next-hop IP: 192.168.46.134, Routes: [ospf (Network: 6.6.6.0/24, Next Hop: interface Ethernet0/2 ip 192.168.46.134)]), TRANSMITTED(Ethernet0/2)), (RECEIVED(Ethernet0/1), ACCEPTED(Loopback0)))])

``` 
**NOTE THAT, THE WAY IT WORKS, YOU ONLY GET BACK THE FIRST FLOW THAT IS A SUCCESS (OR IS DENIED) FOR EACH OF THE START LOCATIONS**

**YOU WILL NOT GET BACK ALL THE ALLOWED/DENIED FLOWS!!**

Also as you can see, the **output** is kinda nested:
- First you **flows** 
- inside a **flow** you are going to se the **Traces**, one for each row and this will include different paths if for instance you have ECMP
- Each **Trace** represent a Path and inside paths you have **Hops** which are nodes
- for Each node, you have **Steps**, e.g.
  
```
>>> df.iloc[0]['Traces'][0]  # <---------- Trace zero, gives me a list of Hops
Hop(node='r1', steps=[Step(detail=OriginateStepDetail(originatingVrf='default'), action='ORIGINATED'), Step(detail=RoutingStepDetail(routes=[RouteInfo(protocol='static', network='0.0.0.0/0', nextHop=NextHopIp(ip='192.168.12.254', type='ip'), nextHopIp=None, admin=1, metric=0)], forwardingDetail=ForwardedOutInterface(outputInterface='Ethernet0/1', resolvedNextHopIp='192.168.12.254', type='ForwardedOutInterface'), arpIp='192.168.12.254', outputInterface='Ethernet0/1'), action='FORWARDED'), Step(detail=ExitOutputIfaceStepDetail(outputInterface='Ethernet0/1', transformedFlow=None), action='TRANSMITTED')])  


#
# for the first (and only) trace are 4 hops
>>> len(df.iloc[0]['Traces'][0]) 
4
#
# In the first hop there are 3 steps
# Step1: action ORGINATED
>>> df.iloc[0]['Traces'][0][0][0]Step(detail=OriginateStepDetail(originatingVrf='default'), action='ORIGINATED')
#
# Step2: action FORWARDED
>>> df.iloc[0]['Traces'][0][0][1]
Step(detail=RoutingStepDetail(routes=[RouteInfo(protocol='static', network='0.0.0.0/0', nextHop=NextHopIp(ip='192.168.12.254', type='ip'), nextHopIp=None, admin=1, metric=0)], forwardingDetail=ForwardedOutInterface(outputInterface='Ethernet0/1', resolvedNextHopIp='192.168.12.254', type='ForwardedOutInterface'), arpIp='192.168.12.254', outputInterface='Ethernet0/1'), action='FORWARDED')

[...]
```

As you can see this is quite hard to read so I've copied a nicer print version function from PacketCoders Repo on Batfish:
See: 
- https://www.packetcoders.io/
- https://github.com/packetcoders/batfish-course/

that you can find the **utils** folder and we can use it to print a nicely formatted version of the DataFrame returned.. (of course you need to add it to the path and import it)

```
# Assuming we run this from the Batfish Folder
import sys
sys.path.append("utils")
from utils.bf_pprint import pprint_reachability


>> pprint_reachability(df)
Flow Summary
Flow: start=r1 [10.0.0.0->6.6.6.6 ICMP (type=8, code=0)] (Trace Count:2)   <-- note Count: 2 it means there are 2 paths so 2 Traces
==========
Flow: start=r1 [10.0.0.0->6.6.6.6 ICMP (type=8, code=0)] (Trace Count:2)

Trace #1
ACCEPTED
1. node: r1
  ORIGINATED(default)
  FORWARDED(Forwarded out interface: Ethernet0/1 with resolved next-hop IP: 192.168.12.254, Routes: )
  TRANSMITTED(Ethernet0/1)
2. node: r2
  RECEIVED(Ethernet0/1)
  FORWARDED(Forwarded out interface: Ethernet0/2 with resolved next-hop IP: 192.168.24.4, Routes: )
  TRANSMITTED(Ethernet0/2)
3. node: r4
  RECEIVED(Ethernet1/0)
  FORWARDED(Forwarded out interface: Ethernet0/1 with resolved next-hop IP: 192.168.46.6, Routes: )
  TRANSMITTED(Ethernet0/1)
4. node: r6
  RECEIVED(Ethernet0/0)
  ACCEPTED(Loopback0)

Trace #2                                                                <--- Second Trace: we have ECMP between R4 - R6 
ACCEPTED
[...]

```


**Note:** Depending on the kind of test you want to run you might just want to check if the response is empty or not..

If there are DENIED flows, you will not probably 



## BATFISH L2 FORWARD ANALYSIS

**Note, I use the topology from site2 which is copied from PacketCoders repo**

To deal with the lack of information at L2 we can add a **layer1_topology.json** file to **Batfish** that contains the L1 connection details and results in the population of L1 edges.

Batfish then combines the L1 and L3 edges allowing L2 domain to be included in the model.  
An example of a layer1 topology file would be something like this:
```

{
    "edges": [
        {
            "node1": {
                "hostname": "r3",
                "interfaceName": "eth0/0"
            },
            "node2": {
                "hostname": "sw7",
                "interfaceName": "Ethernet0/0"
            }
        },
        {
            "node1": {
                "hostname": "r4",
                "interfaceName": "eth0/0"
            },
            "node2": {
                "hostname": "sw7",
                "interfaceName": "Ethernet0/1"
            }
        },
[...]
    ]
}

```
And this would have to be added under `snapshots/<site>/` so this would have to be at the same level as the `configs/` folder.  
If you have a source of truth for network connectivity, like for instance Netbox, it should be relatively easy to automatically generate this file..

In our test topology we have 3 layer2 unmanaged switches called **sw7, sw9** and **sw_net**; but because they are overall just used for point-to-point connectivity they are ignored anyway by Batfish... but you can still see them using the question: `bf.q.userProvidedLayer1Edges()`
```
>>> bf.q.userProvidedLayer1Edges().answer().frame()
         Interface     Remote_Interface
0  r9[Ethernet0/2]  sw_net[ethernet0/1]
1  h1[Ethernet0/0]  sw_net[ethernet0/0]
>>> 
```


Layer1 edges are listed with all the other edges and are also available under `bf.q.layer1Edges().answer().frame()`

```
>>> bf.q.layer1Edges().answer()
                          Interface                 Remote_Interface
0            eos-access3[Ethernet2]                    server3[eth0]
1       eos-access3[Port-Channel30]       nxos-aggr1[port-channel30]
2       eos-access3[Port-Channel30]       nxos-aggr2[port-channel30]
3   ios-access2[GigabitEthernet0/2]                    server2[eth0]


>>> bf.q.edges().answer()
                          Interface                 Remote_Interface
0            eos-access3[Ethernet2]                    server3[eth0]
1       eos-access3[Port-Channel30]       nxos-aggr1[port-channel30]
2       eos-access3[Port-Channel30]       nxos-aggr2[port-channel30]
3   ios-access2[GigabitEthernet0/2]                    server2[eth0]


#################### NOW we can test L2 reachability

>>> import sys
>>> sys.path.append("./")
>>> from utils.bf_pprint import pprint_reachability
>>> from pybatfish.datamodel.flow import (  # isort:skip noqa
    HeaderConstraints,
    PathConstraints,
    )


>>> df = (
    bf.q.reachability(
        pathConstraints=PathConstraints(startLocation="/core/"),
        headers=HeaderConstraints(
            srcIps="0.0.0.0/0", dstIps="10.2.10.0/24, 10.2.20.0/24, 10.2.30.0/24"
        ),
        actions="FAILURE",
    )
    .answer()
    .frame()
)


Trace #1
NEIGHBOR_UNREACHABLE
1. node: nxos-core2
  ORIGINATED(default)
  FORWARDED(Forwarded out interface: Ethernet1/1 with resolved next-hop IP: 10.2.1.2, Routes: )
  TRANSMITTED(Ethernet1/1)
2. node: nxos-aggr2
  RECEIVED(Ethernet1/4)
  FORWARDED(Forwarded out interface: Vlan20, Routes: )
  TRANSMITTED(Vlan20)
  NEIGHBOR_UNREACHABLE(Output Interface: Vlan20, Resolved Next Hop IP: 10.2.20.1)

Note: that a failure is detected because in the snapshots/site2/configs/ios-access2.cfg a vlan is pruned but Batfish will still not show you exactly what went wrong
```

Finally as L2 be aware that:
- spanning tree is not supported
- ACLs on layer2 interfaces are ignored (they are considerd on layer3 interfaces only)
- Port mode, admin state and allowed VLANs are considered and processed by Batfish


