# BGP NOTES

These are notes for basic BGP protocol.
MP-BGP and different address families are not covered here..
See instead:
* Multicast Notes: multicast address family
* VRF Lite and MPLS notes: vpnv4 address family
* VXLAN notes: evpn address family

Notes: 
* AD is only for routing tables, it does not affect BGP selection process
 IBGP AD 200
 EBGP 20
* You can assign a prefix a 200 AD if you use a ```network <prefix> <mask> backdoor``` command. 
  Usually done so that IGP prefixes are preferred over EBGP (but only specific ones)
* BGP ASN:
  * Private AS numbers in the range 64512–65535 
  * Extended notation (4 bytes) is enabled with: bgp asnotation dot 
  * Confederations have the real ASN inside the router section (see later)
* BGP SCAN PROCESS:  
  Set with: ```bgp scan-time <5-60>```
  - Runs through all prefixes in BGP table and checks the validity and reachability of the BGP NEXT_HOP attribute.
  - Performs conditional advertisement and route injection.
  - Imports new routes into the BGP table from RIB (via network and redistribute commands).
  - Performs route dampening.   
* BGP KEEP ALIVE:  
  Keep alive times are set with: timers ```bgp <keepalive> <holdtime>```  
  Default values are 60 and 180 seconds
* BGP NEXT HOP TRIGGER: ```bgp nexthop trigger delay <seconds>```   
  it reacts to changes to IGP next-hop values, e.g. metric changes or next-hop becoming unreachable
* Well-Known Mandatory Attributes:
   - Origin
   - As-path
   - next-hop



## NEIGHBORS
* TCP port 179; src IP is the interface
   * update-source can be used to change the src interface: `neighbor <X> update-source <intf>`
* States are: 
   * **Idle**: up and good but no routes exchanged (starting)
   * **Connect**: actively trying to connect
   * **Active**: if the connection times out (the router will actively retry to conenct)
   * **OpenSent**: Open message sent but no response or keep alive received yet
   * **OpenConfirm**: Messages have been exchanged and parameters agreed
   * **Established**: UP and running   
* Authentication in the TCP headers (option19 - Md5 hash)
* Established if AS match configurations/authentication/address families match
  * IBGP TTL is set to 255
  * EBGP TTL is set to 255 but only 254 is accepted (default) /  `ebgp-multihop <hops>` if TTL >1 is requried, it will accept `TTL` up to `255-<hops>`  
    `disable-connected-check` also allows for loopbacks to be used (but not further than that, i.e. no routers in between)
  * Use TTL security to set the TTL to `<hop>` counts instead: `neighbor <IP> ttl-security hops <X>`   
* **next-hop-self**: for IBGP, changes the next-hop (remember next-hop does not usually change in IBGP 
    or confederation (fake) EBGP);  
    The value set for next-hop is the one used for the TCP connection with the neighbor.
   * The next-hop can also be set (selectvely) via a route map applied to a neighbor (option set ip next-hop <IP>)       
* **next-hop-unchanged**: this is basically the oppositeof next-hop-self. It will keep the next-hop as it has been received.
  (Used mainly in evpn setup..see related notes)   
* neighbors can be configured in **BGP peer groups** (optimizes resources, updates are computed per peer group and not per neighbor)    
* you can do conditional advertising with the syntax:  
    ``neighor <IP> advertise-map <MAP1> exist-map/non-exist <MAP2>``  
  where `<MAP1>` is a route-map matching the prefixes to advertise and `<MAP2>` matches the prefix to monitor.   
  They need to be (or not) in the BGP table to enable the advertisemnts.  Note that when we say match is any type of match supported by route-maps.
* you can limit the number of prefixes received from a neighbor with:  
  ` neighbor <IP> maximum-prefix <Number> [<Threshold%>] [warning-only]|[restart <minutes>]`  
     * if `restart` is used, the rotuer will tear down the connection and wait `<minutes>` before re-establishing it
* A neighbor can present itself with a different AS Number by using:  
    `neighbor <IP> local-as <AS2> [no-prepend [replace-as]] `    
  `<AS2>` is sent in the **OPEN** message and it is prepended to routes sent to the neighbor: `<AS2><AS>`  
  This means that the neighbor will see the prefix as transited through **AS** first then **AS2**.  
  The option `no-prepend` only applies to received routes; by default, local-as would prepend the **AS2**
  to the routes received, but if *no-prepend* is used, this does not happen.  
  The option `replace-as` is used to completely hide the original AS which is not added to the path list(Note: this can of course cause routing loops)
* `neighbor <IP> remove-private-as` : will remove all private AS in the beginning of the AS_PATH sequence
   of the prefixes sent to the neighbor (it will not change values if they are not in the beginning)
* `neighbor <IP> advertisement-interval <seconds>` : sets the **timers** for neighbor updates     
* **fast fallover** for neighbor can be configured possibly using **bfd**):
    * global bgp: `bgp fast-external-fallover`  is required (default).
    * per-neighbor command: `neighbor <IP> fall-over`  
    **Note** that this feature is only efficient when the peering session is established across the non-shared link or when an IGP detects the change: 
    when the IGP route to the peer disappear, the neighbor is considered down immediately
    * you can also map the fall-over to  **BFD** with : ```neighbor <IP> fall-over bfd  [check-control-plane-failure]```  
    The last option is checking something called **Cbit** (control-plane bit) and it determines a different behavior for data-plane vs control-plane failure
    * BFD is configured at the interface level with a syntax like: ```bfd interval 50 min_rx 50 multiplier 3```   
    The syntax specifies the **transmit** interval, the **min receive** interval (not to overload the router) and the numpber of packets that can be lost.
      *  For multi hop bfd you actually need a bfd tempalte and bfd map
      *  Also BFD can be used for static routes, OSPF, ISIS etc..       
* **allowas-in**: use: ```neighbor <IP> allowas-in [count]```   
  if you want to accept routes that have its local AS in the path 
  **MPLS PE** use (usually) **as-override** that replaces the incoming AS with the PE AS so that when the update is received it is not dropped      
* **Dynamic Neighbours**: BGP does support dynamic neighbours IP (one side) with the commands below. You will have to specify:
  * A peer group with the properties to use for the neighbours (ASN, etc..) 
  * The range to match (optional)
  * The max number of dynamic neighbours you want to allow (optional)     
  ```
  bgp listen range <network/mask> peer-group <peer-group-name>
  bgp listen limit <max-number>
  ```                              

## ROUTES EXCHANGES

* IGP synchronization: now mostly disabled by default; it used to require that for every IBGP route a matching IGP route should be present; the goal was to prevent black holes.  
  **Note:** BGP can have a route in **rib failure** (e.g. if the same prefix is present in an IGP with better AD) but even if RIB failure they are still advertised (route is still present).  
  You can use:`suppress inactive` to avoid advertising prefixes in rib failures,                   
* IBGP learned rotues can not be sent to other IBGP neighbours, so a full IBGP mesh is required, or:   
  * **ROUTE REFLECTOR** are neighbours that reflect router to other IBGP peers.
    The router reflector creates a **client** with the command: `neighbor <X> router-reflectr-client` :
    *  routes learnt by a **client** are sent to everyone
    *  routes learnt by non client(IBGP) are sent to clients (and EBGP)
    *  EBGP routes are sent to everyone

    Attributes are not updated by a RR but 2 are added as loop prevention:
      * Originitor ID: IBGP router originating the route (not the RR)
      * Cluster List: List of IBGP clusters (note: a cluster is a RR and its client).   
          * **clusters** are a way to optimize RR/clients distribution, e.g. keeping RR and its clients geographically local.  
          The cluster id can be set with the command `bgp cluster-id <id>` otherwise it's the Router ID. If a prefix is received with the local cluster ID it's **dropped**.
          * you can have multiple **RR** in the same cluster but in that case you have to specify the same **cluster id** explicitely
          * RR in different clusters are **peers** but they are **not** each other clients
          * If in a cluster all RR clients are meshed with each other (unlikely) you can disable client-to-client reflection with the command: `no bgp client-to-client reflection`
  * **CONFEDERATIONS** are a way to split a big AS domain into small sub-domains.
    * `router bgp <AS>` refers to the confederation AS (usually private AS range (64512 – 65535))
    * confedration id refers to the actual main AS
    * use confiderations peers (other as in the same confederation id)          
    * peering between confederation peers use **EBGP** rules; inside the same confederation sub-AS IBGP  rules are in place (so RR still possible)
    * Attribute: **AS_CONFED_SET** is added; it is an unordered list of Sub-ASs that is prepended onto the normal AS-Path as the prefix. 
    It is passed between Sub-ASs but the attribute is stripped and replaced by the confederation id when a prefix it is advertised to a true EBGP peer (double check this..)
* Only the best path is installed in the routing table and sent to neighbors
* **EBGP** leanred routes keep the same value for the next-hop when sent to IBGP neighbors (by default)
* `bgp redistribute internal` is required to enable redistribution from BGP to IGP

## DAMPENING
You can suppress a prefix based on how often it flaps and un-suppress it after an exponentially decaying timer expires. 
Every time a prefix flaps, it is assigned an additive penalty value, 1000 by default; (halved:500 if it is only an attribute change) 
It also still tracked if it becomes uavailable (in case it comes back). 
If the penalty value exceeds the Suppress Limit (default 2000), the BGP process will mark the route as damped and not advertise it to any peer
Notes:
 - every 5 seconds the BGP process decreases the penalty value assigned to the prefix. 
   The decay process has one parameter, Half-Life time period, i.e the amount of time needed to decrease the penalty to half. 
   Default Half_Life time of 15 minutes. 
 - when the penalty falls below the Reuse Limit (default=750), the router will unsuppress the prefix and start advertising it again. 
   The decision to unsuppress a prefix is made every 10 seconds.
   Now, the BGP command to apply the dampening parameters is:  
     `bgp dampening [<Half_Life> <ReuseLimit> <SuppressLimit> <MaximumSuppressTime> ]`  
     e.g. `bgp dampening 4 750 2000 16`
 - you can apply route dampening with a route-map and specify the dampening values inside the route-map 
**Side Note:** that a way to reduce network instability is by using **aggregation**    


## ROUTES
* use `network` statement (mask can be omitted if classful) to advertise a (locally known) prefix.
  * the route needs to be in the routing table (possibly as null0)
  * if `auto-summary` bgp global command is used, the prefix will be installed the route as classful
* **BEST PATH SELECTION:**
   * **excludes** prefix if next hop not resolvable
   * **excludes** prefixes if synchronization is enable and no IGP prefix present
   * **excludes** prefixes with its own AS number in AS path

   **SELECTION PREFERENCE ORDER**:
   - **Highest wieght** (Cisco) -  device local only
       - set via route-map or on the neighbor
   - **Highest Local preference** - AS local
      - used to determine the way traffic leaves the AS 
      - this attrribute is forarded inside the same AS
   - **Locally originated** prefixes (via network, aggreagte-address, redistribute)
   - **shortest AS PATH**
      - used to influence incoming traffic
      - use AS PATH prepending (EBGP only) 
      - Sub-AS from a confederation do not count
      - can be disabled with: `bgp bestpath as-path ignore`
      - a max can be set before rejecting the route: `bgp maxas-limit <N>`
   - **Lowest orgin type**: **IGP** < **EGP**(legacy/unused) < **INCOMPLETE** (redistribution)
      - you can set the origin attribute.. but this is basically never used to determine best routes
   - **Lowest MED** (Multi Exit Discriminator/metric)
      - set to influence incoming traffic (it is non transitive/will not be propagated outside the AS when received)
      - the receivng AS router can ignore it
      - MED is used only if the prefixes come from the same AS (but can be configrued to always compare med)
      - Hot potato routing (do not care about med, just get the packet out of the AS)
      - Cold potato routing (route the packet inside the AS until it gets closer to the destination: lowest MED)
      - if missing you can set is as the highet value: `bgp bestpath med missing-as-worst`
      - can be non deterministic, use: `bgp bestpath deterministic-med` 
   - **EBGP** routes over **IBGP** routes
   - **Lowest IGP metric** to next hop
   - **Lowest BGP router id**

### DEFAULT ROUTE
  You may inject a default route into BGP by using the `network 0.0.0.0 mask 0.0.0.0` command, **if there is a default route in the RIB**.   
  However, to selectively generate a default route, use the command: 
    `neighbor <IP> default-originate [route-map <CONDITION>] `.  
  Without the `route-map` parameter, this command will generate a default route and send it to the configured peer. 
  It is **not** required to have a matching default route in the BGP table or the RIB   

## FILTERING
Filtering order INBOUND in:  
   1. route-map 
   1. filter-list  
   1. prefix-list OR distribute-list

Filtering order OUTBOUND in:   
   1. prefix-list OR distribute-list  
   1. filter-list 
   1. route-map
   
Usually done with neighbor `route-maps` and `prefix-lists` but can also be done with: `neighbor distribute-list` and **standard/extended acls**.  
Note that with **extended** acls, the logic is *src subnet + wildcard* and *destination mask + wildcard*  
**E.g.**  
`permit ip 192.168.0.0 0.0.0.255 255.255.255.0 0.0.0.255` means any subnet in **192.168.0.0** and any mask option starting from 255.255.255.

  * **AS_PATH** filtering is done via regex, some examples:
    *  `“^$”`  means an empty AS_PATH attribute, i.e. generated by the local AS.
    *  `“^254_”` means prefixes received from the directly adjacent AS 254.  
       Note that using `“_”` is important to avoid matching with 2541 for instance
    *  `"_254_"`  means prefixes transiting AS 254. 
    *  `“_254$”`  means prefixes originated in the AS 254.
    *  `“^([0-9]+)_254”` means routes from the AS 254 when it’s just “one-hop” away.
    *  `“^254_([0-9]+)”` means prefixes from the *clients* of the directly connected AS 254.
    *  `“^(254_)+([0-9]+)”` means prefixes from the *clients* of the adjacent AS 254, accounting for the fact that AS 254 may do AS_PATH prepending.
    *  `“^254_([0-9]+_)+”`  means prefixes from the *clients* of the adjacent AS 254, accounting for the fact that the clients may do AS_PATH prepending.
    *  `^\(65100\)` means prefixes learned from the confederation peer 65100, note: they are inside `()`
    
    Create the regex in a **as-path** access-list:  `ip as-path access-list <N> {permit|deny} <Regexp> `  and apply it as a:
     * `neighbor <IP> filter-list <as-path-acl-name> in/out`
     * `neighbor <IP> route-map <MAP>`  
        where `<MAP>` has the filter list applied with: `match as path <as-path-acl-name> in`  

    Test what match you get with the commands:  `show ip bgp regexp` or `show ip bgp quote-regexp `

  * **OUTBOUND ROUTE FILTERING** (OBF): used to push a filter to a neighbor.  
    It is a capability that needs support on both routers and needs to be enabled:
    ```
    neighbor <IP> capability orf prefix-list [send|receive|both]  ! both peers need this
    neighbor <IP> prefix-list <NAME> in                           ! on the router that pushes the filter
    ```      
  
  * **SOFT RECONFIGURATION**: Technically not a filter but allows to check routes before and after a filter is applied.  
    Use the command:  `neighbor <IP> soft-reconfiguration inbound`  
  Without soft-reconfiguraiton, it is not possible to tell a neighbor to resend the updates without tearing down the connection. It also allows to have an *unfiltered* copy of the prefixes received 
  Of course this means it will have double memory utilization though.. 
  Different show commands show the routes and received routes: `show ip bgp neigh <IP> routes` vs `show ip bgp neigh <IP> received-routes`
         

# EQUAL/UNEQUAL COST PATH LOAD BALANCING
  Requriements for equal cost multipath:
  - same attributes up to MED
  - same type (either iBGP or eBGP)
  - same IGP cost to next-hop
  - command: ```maximum path [eibgp] <number>```
  
  Requirements for unequal cost multipath:
  - command: `maximum path [eibgp] <number>`
  - enabled on border router with:
     - global bgp command:  ```bgp dmzlink-bw```
     - per neighbor: ```neigbor <IP> dmzlink-bw``` to select which neighbor load balance with 
  - the ebgp prefixes will carry a new attribute (ext community) with the bandwith of the link to the neighbors
    so ```send-community extend``` is required   

## AGGREGATION
  - to aggreagte IGP routes you can create a **static route** to **null0** and use the `network` command
  - **Autosummary** is always an option (not a great one) 
  - `aggreagte-address <prefix> <mask>` , requires one subnet in the range to be in the **BGP table** (not neessarily the routing table).  
    Note that:
     * By default, the original sub prefixes are still advertised unless you use **summary-only**: 
       `aggregate-address <prefix> <mask> summary-only`
     * If you use `summary-only` prefixes can be **unsuppressed** per neighbor with: `neighbor <IP> unsuppress-map <route-map>`        
     * you can selectively suppress prefixes matched ina route-map with the option **suppress-map**: `aggreagate-address <prefix> <mask> suppress-map <route_map>`
  * a **null0** route is created for the aggregated prefix created.
  * The new aggregated prefix is seen as originated by the local AS
  * The new aggregated prefix will have:
    * an empty **bgp as-list** (by default) or a list of AS generated from the *summarized prefixes* if the option: `as-set` is used:  
    `aggregate-address <prefix> <mask> as-set` (only used for loop prevention)  

      **Note:**  
      With `as-set`, all the other attributes are also inherited including **communities!**  
      You can remove the attributes with an `attribute-map` or you can decide which prefixes should 
      be used to generate the attributes using an: `advertise-map` ,e.g
      ```
      aggregate-address <IP> <MASK> summary-only as-set advertise-map ADVERTISE_MAP
      ```
    * The extra attributes: 
        * **ATOMIC_AGGREGATE** (to inform it's an aggregate and some other attributes are missing)
        * **AGGREGATOR**: AS number and router id of the router generating the aggreagte
        
**Conditional route injection (CRI)** can be used to **un-suppress** prefixes from an **aggregate**; the difference with `unsuppress-map` is that, this is **NOT DONE ON THE AGGREGATOR ROUTER BUT ANY ROUTER CAN DO IT**.  
It requires **2** `route-maps`:
*  the first specifies the prefixes to be injected. Note that you may/should also set other BGP attributes in this route-map or it will have none. AS_PATH attribute is reset to an empty list. 
* The second route-map defines the conditions to meet for the new prefixes to be injected, e.g.: matching some prefixes  

The overall command is: `bgp inject-map <MAP1> exist-map <MAP2>`

## COMMUNITIES
BGP communities are **optional transitive attributes** used mainly to associate an administrative tag to a route. 
32 bit, either completely numeric or in `<ASN>:<number>` format using: `ip bgp-community new-format`  
The major points for communities:
 - **neighbor** can exchange communitiies if configured with: `neighbor <IP> send-community extended`  
   You can then set community inside a route map and apply that to neighbors: **in/out**   
   Note: if you **set** a community, you **replace** the existing communities.. so you probably want to
   use the `additive` option just to add a new community. 
 - **aggregate** prefixes using as-set will inheirt all communities
   - communities can also be set in aggregate routes with: `attribute-map`
     in particular you might want to remove some communities, use: set community none
     inside a route map and pply it to aggregate command as attribute map
 - communities are set via route-maps
    - set community <community-list> [additive]
 - communities can be matched with community-list
    - wildcards can be used in community-lists    
 - you can **delete** some communities from a list of communities:
     - create a community list with prefixes to remove, e.g. COM1
     - create a route-map and using the command: `set comm-list COM1 delete`
       Note that in the same route-map entry you can add other community using: set community `<AS:new>` additive
 - well known communities:
    - **no-export**: the prefix will not be advertised to the neighbor AS, only to IBGP peers       
    - **no-advertise**: the prefix will not be advertised to any peer.
      Note: if you set it via a `neigh route-map inbound`, all prefixes received will not be advertised
    - **no-export-subconfed/local-as**: same as no export but for confederation, prefixes are forwarded only to peers in the same confederation as
    

## Route withdraw
BGP (Border Gateway Protocol) withdraws a prefix in order to ensure that BGP routing information accurately reflects the current state of the network.
This happens in the following cases:

1. **Prefix Withdrawal**: When a BGP router no longer has a valid route to a specific prefix (destination network), it withdraws the previously advertised route for that prefix. This can happen due to network failures, route changes, or changes in routing policies. When a BGP router withdraws a prefix, it informs its BGP neighbors by sending a BGP UPDATE message with the withdrawn prefix.

2. **Path Attribute Changes**: If there's a change in the path attributes associated with a prefix (such as AS Path, Next Hop, Local Preference, etc.) that makes the previously advertised route invalid or less preferable, BGP may withdraw the prefix and advertise a new route with updated path attributes.

3. **Administrative Configuration**: BGP prefix withdrawal can also occur due to administrative configuration changes. For example, if a network administrator manually removes a prefix advertisement from BGP configuration, the router will withdraw the corresponding prefix from BGP updates sent to its neighbors.

4. **Route Flap Damping**: In some BGP implementations, route flap damping mechanisms may cause BGP to withdraw prefixes. Route flap damping is a technique used to mitigate the impact of route flapping (frequent route changes) by penalizing unstable routes. If a prefix flaps too frequently, BGP may dampen the route by withdrawing it temporarily from BGP updates.

5. **Prefix Aggregation**: BGP routers may withdraw more specific prefixes (subnets) when they start advertising a less specific prefix (aggregate route) that covers them. This process is known as prefix aggregation or route summarization.


## BGP Additional Paths
By default BGP advertises the best path knwon to a destination; **if a better path is discovered, the previous NLRI will be withdrawn**.  
These has a few disadvantages:
- Next-Hop failure means BGP has to reconverge before traffic can be forwarded again
- Possible sub-optimal routing.  
  This happens especially when you have route-reflectors: they will pick the best route for them and advertise that but not for the RR clients 
  there might be better/different options
- Can't use **BGP Multipath**
- Possible MED Oscillation

It is however possible to configure BGP to advertise Additional Paths so that peers will see all path options. This is done by adding a **Path Identifier**: `<path id>` to the NLRI (similar in a way to the RD), however this only works for **IBGP Peers** .  
The steps to configure Additional Paths are:
 1.  Enable the additional path feature globally on the routers
 1.  Configure a global selection criterion to chose the extra paths:
     - Best N: this is the Best Path and the N-1 other  Best Paths using BGP selection process.
     - Group-Best: this will select the best path for each AS and group them together; e.g. if you receive the same route from 3 AS with different paths
       you will get the a group made by the best route from each AS.
     - All: all paths that have a unique next-hop can be used as an additional path
 1.  Configure the specific neighbours/peer groups so that you send them the additional paths; note that the neighbour statement should 
     match the global policy for consistency..

```
R1(config)# router bgp 100
R1(config-router)# address-family ipv4
R1(config-router-af)# bgp additional-paths send receive
R1(config-router-af)# bgp additional-paths select group-best all/<N>
R1(config-router-af)# ! 
R1(config-router-af)# ! alternatives
R1(config-router-af)# ! bgp additional-paths select best <N>
R1(config-router-af)# ! bgp additional-paths select best all
R1(config-router-af)#
R1(config-router-af)# neighbor 192.168.2.2 advertise additional-paths group-best all  <- this should match or be a smaller set than the global command
R1(config-router-af)# ! neighbor 192.168.2.2 advertise additional-paths disable       <- if you want to disable it in an address family


``` 
Yu can also optionally use a **route map** to filter the additional paths advertised by matching on the tags; these tags are the **advertise-sets** configured with the command: `bgp additional-paths select`.  
The route map will match the paths tags against the ones in the command:  `match additional-paths advertise-set` 

Of course in the route map, you can also set one or more actions, e.g.: `set metric`

```
route-map additional_path1 permit 10
  match additional-paths advertise-set best 3   ! -> assuming this is the advertise tag, i.e. the selected criteria
  set metric 500
```

