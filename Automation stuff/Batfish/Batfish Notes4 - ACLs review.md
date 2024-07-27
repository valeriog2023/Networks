# BATFISH NOTES 4


# BATFISH NOTES ACL ANALYSIS

Batfish allows to run tests on ACLS; in particular there 4 actions available:
- **filterLineReachability** : returns filter entries that will never be hit due to other entries further up in the filter.  
  The use case is typically for AC cleanup and maintenance
- **testFilters** : this is used for validation of a single flow
- **searchFilters** : returns the first flow within a **flow block** to match an action;  
   You can use it for instance passing the flow block that you think should be denied and check if something is instead allowed
- **findMatchingFilterLines** : returns entries within a filter that match any packet within a set of flows (Audit reporting);  
  For instance you could give a host as source and get back all flows allowed for that specific host

- **compareFilters**: used to compare filters between snapshots
  
---
**The following tests are run against the snapshot in site3; the topology is cloned by PacketCoders repo and only a limted set of flows is allowed:**  

Sources:
- 10.2.10.0/24
- 10.2.20.0/24
- 10.2.30.0/24

Destinations:
 - 8.8.8.8, 8.8.4.4
 - 216.239.25.0
 - 216.239.35.4

 Protocol/Ports:
 - TCP/443
 - UDP/53
 - UDP/123

```
[LOADING TEST TOPOLOGY]
BF_SNAPSHOT_PATH3 = f"snapshots/site3"
import sys
sys.path.append("./")

from pybatfish.datamodel.flow import (  # isort:skip noqa
    HeaderConstraints,
    PathConstraints,
    )

bf.init_snapshot(BF_SNAPSHOT_PATH3, overwrite=True)    
```

---
## ACL SHADOWING
This example will detect the following problem in the configuration of site3/nxos-core1:
```
(base) vale6811@tc2:~/Desktop/Networks/Automation stuff/Batfish$ cat snapshots/site3/configs/nxos-core1.cfg | grep -A 10 access-list
ip access-list ACL-EXAMPLE
  permit udp addrgroup OBJ-GRP-SERVERS addrgroup OBJ-GRP-DNS eq 53
  permit udp addrgroup OBJ-GRP-SERVERS addrgroup OBJ-GRP-NTP eq 123
  deny ip any any
  permit tcp addrgroup OBJ-GRP-SERVERS any eq 443         <---------------  can't be reached


!end
```
We just need to run the question and printout the details of the result (in this case it's a single row which maps to our issue)


```
>>> df = bf.q.filterLineReachability().answer().frame()


>>> df.iloc[0]
Sources                                        ['nxos-core1: ACL-EXAMPLE']
Unreachable_Line           permit tcp addrgroup OBJ-GRP-SERVERS any eq 443
Unreachable_Line_Action                                             PERMIT
Blocking_Lines                                         ['deny ip any any']
Different_Action                                                      True
Reason                                                      BLOCKING_LINES
Additional_Info                                                       None
Name: 0, dtype: object
```
---
## TEST FILTERS
This is used to test a single flow trough all the devices 
**Note: it's only going to take the first flow so you have to be very specific**

```
>>> df = bf.q.testFilters(nodes="/core/",
                      filters="ACL-EXAMPLE",
                      headers=HeaderConstraints(
                          srcIps="10.2.10.1", 
                          dstIps="1.1.1.1", 
                          ipProtocols=["UDP"], 
                          dstPorts="123"
                      )).answer().frame()


>>> df
         Node  Filter_Name                                               Flow Action     Line_Content                           Trace
0  nxos-core2  ACL-EXAMPLE  start=nxos-core2 vrf=management [10.2.10.1:491...   DENY  deny ip any any  - Matched line deny ip any any
1  nxos-core1  ACL-EXAMPLE  start=nxos-core1 vrf=management [10.2.10.1:491...   DENY  deny ip any any  - Matched line deny ip any any
2  nxos-core1  ACL-EXAMPLE  start=nxos-core1 [10.2.10.1:49152->1.1.1.1:123...   DENY  deny ip any any  - Matched line deny ip any any
3  nxos-core2  ACL-EXAMPLE  start=nxos-core2 [10.2.10.1:49152->1.1.1.1:123...   DENY  deny ip any any  - Matched line deny ip any any


>>> df = bf.q.testFilters(nodes="/core/",
                      filters="ACL-EXAMPLE",
                      headers=HeaderConstraints(
                          srcIps="10.2.10.0/24",       # <------- Full /24 network
                          dstIps="1.1.1.1", 
                          ipProtocols=["UDP"], 
                          #startLocation="@vrf(default)",     # <------ You can possibly specify a start location 
                          dstPorts="443-1024"                 # <------ Port range

                      )).answer().frame()


>>> df                          # <------- we still get only 4 flows.. because only one flow per block is tested per start location
         Node  Filter_Name                                               Flow Action     Line_Content                           Trace
0  nxos-core2  ACL-EXAMPLE  start=nxos-core2 vrf=management [10.2.10.0:491...   DENY  deny ip any any  - Matched line deny ip any any
1  nxos-core1  ACL-EXAMPLE  start=nxos-core1 vrf=management [10.2.10.0:491...   DENY  deny ip any any  - Matched line deny ip any any
2  nxos-core1  ACL-EXAMPLE  start=nxos-core1 [10.2.10.0:49152->1.1.1.1:443...   DENY  deny ip any any  - Matched line deny ip any any
3  nxos-core2  ACL-EXAMPLE  start=nxos-core2 [10.2.10.0:49152->1.1.1.1:443...   DENY  deny ip any any  - Matched line deny ip any any

>>> df.iloc[0]['Flow']
Flow(dscp=0, dstIp='1.1.1.1', dstPort=443, ecn=0, fragmentOffset=0, icmpCode=None, icmpVar=None, ingressInterface=None, ingressNode='nxos-core2', ingressVrf='management', ipProtocol='UDP', packetLength=512, srcIp='10.2.10.0', srcPort=49152, tcpFlagsAck=0, tcpFlagsCwr=0, tcpFlagsEce=0, tcpFlagsFin=0, tcpFlagsPsh=0, tcpFlagsRst=0, tcpFlagsSyn=0, tcpFlagsUrg=0)
>>> 
```

#### **Note on Batfish grammar:** 
In the last example we use a `startLocation=@vrf(default)` (commented out), **@vrf** is an interface specifier, which means select interfaces from this vrf.  
In other places we have used some form of **pattern matching**  with the format: `/<pattern>/` ; both are examples of Batfish grammar and the related information is available here: https://batfish.readthedocs.io/en/latest/specifiers.html

---
## SEARCH FILTERS

Similar to test filters this is instead used to test block of flows. The idea here is that you might want to test what **SHOULD NOT BE PERMITTED** and if what you get back is **NOT EMPTY** then you have a set of flows that should be closed

```
df = bf.q.searchFilters(
        headers=HeaderConstraints(
            srcIps="0.0.0.0/0 \ 10.2.10.0-10.2.30.255",   #  <---- the \ gives us a difference, i.e. everything (0.0.0.0/0) minus that range
            dstIps="8.8.8.8,8.8.4.4",
            applications="udp/53",
        ),
        nodes="/nxos-core/",
        filters="ACL-EXAMPLE",
        action="permit",
    ).answer().frame()


>>> df.iloc[0]
Node                                                   nxos-core1
Filter_Name                                           ACL-EXAMPLE
Flow            start=nxos-core1 [10.2.0.0:49152->8.8.8.8:53 UDP]
Action                                                     PERMIT
Line_Content    permit udp addrgroup OBJ-GRP-SERVERS addrgroup...
Trace           - Matched line permit udp addrgroup OBJ-GRP-SE...
Name: 0, dtype: object    
```

Note that the line content shows:
```
>>> df.iloc[0]['Line_Content']
'permit udp addrgroup OBJ-GRP-SERVERS addrgroup OBJ-GRP-DNS eq 53'
```
and the problem is that the source object ggroup has been defined incorrectly (the /16 mask is too wide):
```
[NXOS1-CORE]
object-group ip address OBJ-GRP-SERVERS
  10.2.0.0/16
```  

---
## FIND MATCHING LINES

This is used to audit what is the access, i.e. the entries matched, by a specific flows.. Usually you would specify just a src ip/subnet and see what they are matching
```
# Set display options of column width
import pandas as pd
pd.set_option("display.max_colwidth", None)


df = bf.q.findMatchingFilterLines(
        headers=HeaderConstraints(srcIps="10.2.10.1"), action="permit"
       ).answer().frame()


>>> df
         Node       Filter                                                               Line Line_Index  Action
0  nxos-core1  ACL-EXAMPLE   permit udp addrgroup OBJ-GRP-SERVERS addrgroup OBJ-GRP-DNS eq 53          0  PERMIT
1  nxos-core1  ACL-EXAMPLE  permit udp addrgroup OBJ-GRP-SERVERS addrgroup OBJ-GRP-NTP eq 123          1  PERMIT
2  nxos-core1  ACL-EXAMPLE                    permit tcp addrgroup OBJ-GRP-SERVERS any eq 443          3  PERMIT
3  nxos-core2  ACL-EXAMPLE   permit udp addrgroup OBJ-GRP-SERVERS addrgroup OBJ-GRP-DNS eq 53          0  PERMIT
4  nxos-core2  ACL-EXAMPLE  permit udp addrgroup OBJ-GRP-SERVERS addrgroup OBJ-GRP-NTP eq 123          1  PERMIT
5  nxos-core2  ACL-EXAMPLE                    permit tcp addrgroup OBJ-GRP-SERVERS any eq 443          2  PERMIT

```