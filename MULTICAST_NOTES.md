# MULTICAST

Multicast traffic distribution uses the concept of “constrained” flooding, i.e. 
traffic is flooded only on the links that lead to the actual group subscribers. 
The process has 2 parts:
  *  Building a multicast distribution tree for a group—aka Shortest Path Tree or SPT.
  *  Flooding the actual multicast packets down the SPT, while performing Reverse Path
     Forwarding (RPF) to avoid loops.


# PIM RPF CHECK AND FORWARDING
PIM uses the unicast routing table to perform RPF checks.
When the router receives a multicast packet, it looks at the source IP address for the packet.
The router looks up the source IP address in the unicast routing table and determines the 
outgoing interface for this packet. If this outgoing interface does not match the interface 
where the packet was received, the router drops the packet.

If the RPF check is passed, the router will determine the outgoing interface list (OIL) 
The OIL never includes the input interface; this is the well-known split horizon rule.
PIM needs to be globally enabled:
```
ip multicast-routing distributed
```

Note you can change RPF by adding:
- static routes: carefull as it actually change the routing path
- multicast route: ```ip mroute <SOURCE> <MASK> [RPF-IP-Address|<Interface-Name>] [distance]```
  This commands only change RPF check behaviour.
  Note: the mroute table is ordered based on the actul commands, so put the msot specific first

You can debug RPF using:
```
debug ip mfib pak

You might need these 2 as well to actually see the debug
no ip mfib cef input 
no ip mfib cef output
```

You can tunnel multicast to traverse networks that do not support it, however remember:
*  pim needs to be enabled in the tunnel interface
*  the tunnel needs to be in the RPF path



# PIM DENSE MODE

*  Does not use any explicit signaling to create the SPT
*  It floods a packet out of all the interfaces enabled for multicast (except the source interface)
*  if the downstream router does not have subscriber, it will send upstream a **PRUNE** message for the group
   *  as a consequence the link to the downstream router will be removed from OIL
   *  PRUNE MEssage is valid for 3 minutes (default), after that traffic is sent again
*  DM nees to be enabled interface per interface
   ```
   interface <X>
     ip pim dense-mode
   ```
*  Verify commands
   ```
   show ip pim neighbor
   show ip pim interface
   show ip mroute   
   show ip pim rp mapping

   Note that in show ip mroute, 
     - the (*,G) will have all the interfaces in the OIL, this entry will have the D flag
     - the (S,G) will have the T bit (traffic in shortest Path)
     - the RP value is 0.0.0.0 (RPF not used)
     - the RPF value is all 0 if the source is directly connected, otherwise it's the upstream neighbor

   show ip rpf <source>
   will get the information about the RPF interface for a specific source 
   ```



# PIM SPARSE MODE
PIM SM builds explicit multicast distribution trees from the receivers to the sources. 
It uses Rendezvous Point (RP)to faciliate discovery of endpoints (sources/destinations):
*  An RP is a known to both sources and receivers. 
   *  A Receiver (for a group: G) router first builds a tree to the RP; this is called **SHARED TREE** or (*,G)
      This is done by sending upstream **PIM JOIN** messages toward the RP
   *  When a source appears in the network, the **closest multicast router** will contact the RP 
      using **PIM Register** messages; these messages are encapsulated in a unicast packet and sent to the RP. 
      **Note:** a dynamic (non configurable) Tunnel interface is created on all routers in the PIM network to 
      encapsulate the register messages to the RP
      **Note:** PIM should be enabled along the shortest path to the RP, or the RPF check for the RP will fail 
      and the registration will not be completed.
   *  The RP builds a new SPT toward the source using **PIM Join** messages and starts forwarding traffic down 
      the (*,G) tree. 
   *  When the SPT to the source is created (by the RP) the RP sends a **Register Stop** message 
      TRaffic does not need to be incapsulated anymore, it can just follow the SPT to the RP
   *  **SPT switchover**: when the receivers see traffic going down the (*,G) tree from a source, they initiate 
       a **PIM Join** toward the source, building another SPT designated as the (S,G) (falt will be set to T)
      Also a **Prune** message is sent to the RP as we don't need the traffic from (*,G) anymore 
      Nete: you can set a threshold for the switchover to happen (and possibly disable it completely):
      ```ip pim spt-threshold [<Rate in Kbps>|infinity]```


## PIM SPARSE MODE - STATIC RP
You can configure the RP in a static way (note: static takes precendence over dynamic here):

```
ip pim rp-address <IP> [<ACL>] [override] .
```
The ACL parameter lists the groups that are mapped to this particular RP. 
The **override** parameter will force the router to retain static information even if a different RP for the group 
is learned via Auto-RP/BSR.



## PIM SPARSE MODE - DR ELECTION
If there are multiple multicast routers on the same Multi-access segment, a DR needs to be elected.
The goal of the DR is:
*  To signal the SPT and forward packets when there are receivers on the segment
*  To register active sources on the segment with the regional RP;
   *  When the DR hears multicast packets on the segment, it will check if the group has an RP
   *  If it does, the data packets are encapsulated into **PIM Register** messages and sent to the RP. 
   *  The RP will start forwarding them down the shared tree (if there are subscribers) and build the SPT 
      to the DR
The winner is decided based on:
*  highest priority 
*  highest IP address;
*  The process is preemptive 


## PIM SPARSE MODE - ASSERT

If multiple multicast routers share a single segment, only will one will send traffic to avoid duplication, i.e.
the downstream router would see, accept and forward packets from both.  
*  A router detects that someone is sending traffic for the same (S,G), that is also locally active (S,G)  
   so it originates a PIM Assert message.  
   The message contains the source IP, the group, and the path cost to the source (AD, Metric).  
*  The Messge is evaluated: best (lowest) AD value wins the assertion 
   *  metric and router ip on the segment are used as possible tie breaker if required 
*  The loser  will remove the (S,G) state on its interface and stop flooding traffic.
*  The winner, it will emit a superior PIM Assert message (so the other router will stop)
**Notes:** 
*  PIM Assert procedure might be dangerous on NBMA interfaces.  
   E.g. e a hub-and-spoke DMVPN; if for the Spoke wins, the hub stops sending multicast;
   The Hub will also not send the traffic to the other spokes as that would violate RPF so
   all other spokes stop receiving traffic.
   Solutions:
   *  use PIM NBMA mode (sparse mode only)
   *  make sure that the hub always wins the PIM Assert.
*  if you use an mroute, the AD advertised is 1 (so it basically always wins)



## PIM SPARSE MODE - ACCEPT RP
This is a security feature (for all routers):
```
ip pim accept-rp [<rp-address> | auto-rp] [<access-list-name>]
```
When configured the router will only accept **join/prune** messages for  (*,G) the specific RP
This means a client can't creat a SPT through this router if the RP is not the one allowed.
The access-list is used, then only **Join/Prune** messages for the groups in the acl are accepted.
**Notes:** 
*  (S,G) join/prune are not affected
*  auto-rp: when used it means only RP learnt via auto-rp


## PIM SPARSE MODE - ACCEPT REGISTER
This is a security feature (for the RP) :
```
ip pim accept-register [list <Extended-ACL | route-map <Route-Map>]
```
You can specify the sources that are allowed to register with the RP. If the RP denies the registration, 
it sends a **PIM Register-Stop** to the DR immediately and never builds the SPT toward the source. 
**NOTE:** registration is performed by the PIM DR router; every message contains the original  
          multicast packet, which includes the IP address of the multicast source and the group. 



## PIM SPARSE MODE - AUTO-RP
This is actually quite an old protocol, replaced by BSR.
Auto-RP works based on:
*  Candidate RP (cRP) : any router that wants to become an RP
*  Mapping Agents (MA): will forward information about groups and RP

CRP are configured with:
```
ip pim send-rp-announce <Interface> scope <TTL> [group-list <Std-ACL>] [interval <seconds>]
```
These routers will send UDP packets to the IP/Port 224.0.1.39/496 with the list of groups (default is 60 seconds). 
*  <TTL> is used to limit the scopeThe interface
*  <Interface> must be enabled for PIM and its IP address will be used as the RP’s IP. 
*  <Std-ACL> lists the groups for which we want to become the RP
   Notes: 
   *  wildcard masks are converted to prefix-lengths, so you cannot use discontinuous masks. 
   *  “deny” statements are interpreted as groups that should be trated as "dense" mode
The cRP announcements are flooded across the network and reach the Mapping Agents that lsiten for 224.0.0.39. 
You configure these routers using the command:
```
ip pim send-rp-discovery <Interface> scope <TTL> interval <Seconds> . 
```
Mapping Agents compile a list of **Group to RP mappings** and send **“RP discovery”** messages to **224.0.1.40:496**. 
**Notes:** 
*  if there are multiple MAs, they will hear each other, and all of them, except the one with the highest IP address, 
   will cease sending discoveries.
*  if the same group is mapped to multiple RP, the MA will select the the highest RP IP address.
*  if there are two announcements where one group is a subset of another but the RPs are different, both will be sent.
*  All regular routers join the multicast group 224.0.1.40 and listen to the discovery messages and use them to populate
   their cache
   * Negative entries in the cache/discovery are considered first, groups in negative message will be 
     seen as DENSE and RP info ignored. 
   * Positive Entries are selected based on longest match
   * Note that a single negative entry could blacklist multiple positive (as it is considered first)
*  Groups: 224.0.1.39, 224.0.1.40 are propagated across in **dense mode** thorugh the network. (there is no RP)
   This requires: ```pim sparse-dense-mode``` on all interfaces within the multicast domain. You may also
   want to use the ```no ip dm-fallback``` global command.
   *  An alternative to **spare-dense** mode for 224.0.1.39, 224.0.1.40, is to use **Auto-RP Listener**  
      It will only allows those 2 groups to work in **dense** mode and it does not use sparse-dense on the interface 
      (only normal sprse mode)
   *  In NBMA, you ned to place MA in the Hub because **ip pim nbma** only works in sparse mode but the 2 groups
      forward traffic in dense mode (the RP can still be some place else)  
*  If you define a static RP for 224.0.1.39 and 224.0.1.40. This will require you to use the ```override```
   By default, Auto-RP announcements override a statically configured RP so uf you want them to persist, use
   the override keyword along with the ip pim rp-address command.
*  You can do load balancing and redundnacy by setting:
   * RP1 primary for longest match set of prefixes(1), secondary for summarized set of prefixes(2)
   * RP2 primary for longest match set of prefixes(2), secondary for summarized set of prefixes(1)
* you can filter (on Mapping Agents) Auto-RP announcements with:
  ```ip pim rp-announce-filter [group-list <access-list> | rp-list <access-list>]  ```


## PIM Bootstrap Router
BSR, is a standards-based solution available with PIMv2 that performs the same function as Auto-RP.  
BSR does not use any dense-mode groups to distribute RP-to-group mapping information but instead it  
floods information using PIM messages, on a hop-by-hop basis:
*  a router receives a candidate RP announcement inside a PIM message
*  it applies an RPF check, validating that the announcement is on the SPT to the RP
*  If the RPF check succeeds, the message is flooded out of all PIM-enabled interfaces.
To configure a candidate RP, use the command:
```
ip pim rp-candidate <PIM-Enabled-Interface> [group-list <Standard-ACL>] [interval <Seconds>] [priority <0-255>] .
```
**Notes:**
*  If you omit all arguments, the router will start advertising itself as the RP for all groups. 
*  You may specify a list of groups using the group-list argument (you cannot use “negative”groups).  
*  Priority value is used when the routers select the best RP for a given group (lower is prefered, default is zero)
   You can change the priority of an RP if you want to gracefully shut it down
*  you can filter BSR messages with the interface command: ```ip pim bsr-border```: message will not be flooded or
   accepted on that link 

The BSR (similar to MA agent) router builds, for every group range a set of candidate RPs called: the group range  
to RP set mapping. The resulting array of group range to RP set mappings is distributed by the BSR using PIM messages  
and the same flooding procedure described above.  
The command to configure a router as a **BSR** is:
```
ip pim bsr-candidate <Interface-Name> [hash-mask-length] [priority] . 
```
By default, the priority of zero is advertised in all BSR messages. The **higher** the priority value, the **more preferred**  
the BSR. The IP address of the interface used to source the BSR messages is used as a tie-breaker; if two priorities match,  
the higher IP is preferred. 
If there are multiple BSRs, they all listen to other potential BSR messages. If a BSR hears a message with a higher priority  
or IP address, it immediately stops its own BSR advertisements.  
To facilitate RP load-balancing, routers may use a special **hash** function to select the best RP from a set that services  
the same group range.


## PIM MULTICAST BOUNDARY
This feature applies filtering to both the control plane traffic (IGMP, PIM, AutoRP) and 
the data plane (installing multicast route states out of the configured interface). 
You can use it to contain multicast by applying:
```
ip multicast boundary <access-list> [filter-autorp] 
```
to an interface; the following rules apply:
*  If the access-list is a standard ACL, any ingress **IGMP or PIM** messages are inspected 
   to see if the group being joined or tree being built has a match in the ACL. The interface
   can be used for a group in the ACL
*  If the access-list is an extended ACL, it specifies both multicast sources and groups, using  
   the format permit ip ```<src-ip> <src-wildcard> <group-address> <group-mask>```; PIM/IGMP is inspected
   and matched against the ACL to see if they are allowed. Same for actual traffic.
*  **unicast PIM Register** messages are not affected by the multicast-boundary configuration and must be 
   filtered using the respective feature.



# PIM SPARSE DENSE MODE
PIM Sparse-Dense mode is a hybrid of the Sparse and Dense mode operations. When you apply the command:  
```ip pim sparse-dense-mode``` to an interface, the router will forward traffic for both sparse and 
dense groups out of this interface.  
This means, if you hav an RP for a group it will use SPARSE mode otherwise it will use DENSE mode.  
(This is useful in cases where the RP is learn dynamically, but overall **DO NOT USE IT**)  
Use the command: ```no ip pim dm-fallback``` on all PIM SM/DM routers to prevent the DM fallback behavior 
and only allow forwarding for sparse-mode groups.


# STUB MULTICAST AND IGMP HELPER
You can use this feature on spoke routers with low resources where you don't want to handle PIM messages.  
A router cab configure to just forward the **IGMP Messages** they see locally to a **HUB** router.
The **HUB** router will see IGMP requests and handle **PIM state**
**NOTES:**
*  The spoke router is configured with 
   ```
   interface <X>
     description multicast uplink
     ip pim dense-mode
     ip igmp helper-address <HUB IP ON THE LINK>
   ```
*  The HUB router is configured with:
   ```
   interface <Y>
     description link to spoke
     ip pim sparse-mode
     ip pim neighbor-filter <standard_acl>
   ```   
   the filter is applied to avoid to create a neighbor with the spoke (the acl should have a deny for the spoke ip)


# IGMP FILTERING   