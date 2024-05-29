# Junos Intermediate Routing - 4 - BASIC BGP

Not going to repeat here basic BGP facts... only Juniper specific notes

Preference for EBGP routes: 170

To configure BGP you have to setup bgp groups which are similar to Cisco peer groups as
in you can set the attributes in the group and have more than one peer in the group


## Best Path Selection
This is a bit different from the Cisco Best Path selection so reporting it here:
- **next-hop rechable via the lowest route preference**  :  Static >  OSPF > ISIS ( > means better)
- Highest **Local Preference** (default 100) wins
- Smallest **AS Path** length
- **Origin** Code: IGP > ?  :   where > means better and ? is the origin for redistributed routes (or unknown)
- Lowest **MED** is preferred (same service provider) or use the command: `always-compare-med`
- **EBGP over IBGP**  wins
- **Lowest IGP cost** wins
- **Shortest Route Reflection Cluster List** wins
- **Lowest router ID** wins
- **Lowest peer IP** wins

Notes:
- Juniper does not support **weight** 
- you can enable **ECMP** for rotues received by a BGP group by:
   - using the command: `set protocols bgp group <name> multipath`
   - applying the routing-policy we've seen already to the **forwarding-table export**


## BGP External Peering
```
R1#
R1# set routing-options router-id 1.1.1.1
R1# set routing-options autonomous-system 65000
R1#
R1# ! you need to createa group, give it name and specify the type of BGP neighbours
R1# ! for external peer use inerface address
R1# set protocol bgp group ExtBGP_PEER1 type external
R1# set protocol bgp group ExtBGP_PEER1 local-address <IP>
R1# set protocol bgp group ExtBGP_PEER1 neighbor <PEER_IP> peer-as <PEER_AS>
R1#
R1#
R1# run show bgp neighbor

```



## BGP Internal Peering
```
R1#
R1# set routing-options router-id 1.1.1.1
R1# set routing-options autonomous-system 65000
R1#
R1# ! you need to createa group, give it name and specify the type of BGP neighbours
R1# ! for external peer use inerface address and Loopback for internal
R1# ! for internal no AS on the peer is required
R1# set protocol bgp group IntBGP_PEER1 type internal
R1# set protocol bgp group IntBGP_PEER1 local-address <LO_IP>
R1# set protocol bgp group IntBGP_PEER1 neighbor <PEER1_IP>
R1# set protocol bgp group IntBGP_PEER1 neighbor <PEER2_IP>
R1#
R1#
```


## BGP Policies

BGP Policies **import** and **export** can be set at different levels: 
- **global** 
- **Group**
- **Peer** 

The more specific logic takes priority, i.e. only the most explicit policy is applied. 
Also remember that:
- The default for each policy is the default behaviour of the router on that feature.. i.e. it's not always a deny/reject..
- The first term matched in a policy with a termination action, is executed and all the other terms ignored.  
  Note that:
    - some terms have an implicit termination action
    - you can change the behaviour using keywords like `next-term`, etc..
- You can more than one policy applied at the same level, however remember they are scanned in sequence, i.e. first all terms  
  in the first policy, then all terms in the second one and so on.. if a termination action is matched, the process is stopped
- You can create **subroutine**, i.e. policies that are not applied directly (and usually have only match conditions) and reference  
  them inside other policy (to avoid replicate the same match conditions..)


### BGP Policy: Inject routes
Inject routes into BGP from local:

```
!
set policy-options policy-statement extBGP term 1 from protocol local direct 
set policy-options policy-statement extBGP term 1 then accept
!
! this tells the router to take routes from the Routing engine and export them into BGP group: extBGP_PEER1
set protocols bgp group extBGP_PEER1 export extBGP
```

### BGP Policy: Next-hop self
In order to enable **next-hop self**, you actually need to write a routing policy and apply it
to the BGP group with the peers (internal):
```
set policy-options policy-statement NHS term 1 from protocol BGP
set policy-options policy-statement NHS term 1 then next-hop ?
  <address>
  discard
  next-table
  peer-address
  reject
  self                      <------ this is what we use

!
! This is an export policy as it's taking routes from routing table and adding/changing attributes
!
set protocol bgp group IntBGP_PEER1 export NHS
```

### BGP Policy: Set Local Preference
```
set policy-options policy-statement set-preference term 1 from route-filter <network/mask> [exact|orlonger|..]
set policy-options policy-statement set-preference term 1 then local-preference 110
!
! We apply the policy as export for IBGP peer group
!
set protocol bgp group IntBGP_PEER1 export set-preference
```

### BGP Policy: AS PATH Manipulation
Here we show how to maniuplate the number of AS in ingress, i.e. prepend an AS to a prefix we receive:
```
set policy-options policy-statement add_AS_in term 1 from route-filter <prefix/mask> exact
set policy-options policy-statement add_AS_in term 1 then as-path-expand ?
Possible completions:
   <aspath>               AS path string
>  last-as                Prepend last AS   

set policy-options policy-statement add_AS_in term 1 then as-path-expand <AS>
!
!
! Note that this is an import policy. We tell the RE to set an attribute on something we want in the routing table
!
set protocol bgp group Ext_Group import add_AS
```
Here we show how to maniuplate the number of AS for a prefix we send out to a peer:
```
set policy-options policy-statement add_AS_out term 1 from route-filter <prefix/mask> exact
set policy-options policy-statement add_AS_out term 1 then as-path-prepend <AS>
!
! Note this time the policy is applied as export because we manipulate a route that comes from the routing table
!
set protocol bgp group Ext_Group export add_AS
```


### BGP Policy: MED
This is used to set the value for MED for prefixes leaving the AS; it is usally done at the neighbor level more than group level.
```
set protocols bgp group Ext_Group neighbor <PEER_1> metric-out 10  ! preferred as lower
!
set protocols bgp group Ext_Group neighbor <PEER_2> metric-out 100
```
This can be set as well in a routing policy matching some condition and applied as **export**




### BGP Policy: Route reflectors
Route-Reflectors need to be setup with a **cluster-ID**

```
R1# set routing-options router-id 1.1.1.1
R1# set routing-options autonomous-system 65000
R1#
R1# set protocol bgp group IntBGP_PEER1 type internal
R1# set protocol bgp group IntBGP_PEER1 local-address <LO_IP>
R1# set protocol bgp group IntBGP_PEER1 neighbor <PEER1_IP>
R1# set protocol bgp group IntBGP_PEER1 neighbor <PEER2_IP>
R1#
R1# set protocols bgp group IntBGP cluster 5.5.5.5   <---- this enables the router R1 as route-reflector for this group of peers
R1#
```


## BGP Show commands
```
#
#
###### SHOW COMMANDS
#
#
R1# run show bgp summary

R1# run show bgp neighbor

R1# run show route advertising-prtocol bgp <PEER_IP>

R1# run show route receive-prtocol bgp <PEER_IP>

R1# run show route protocol bgp 

R1# run show route protocol bgp hidden  !-> it will show unusable routes received

```