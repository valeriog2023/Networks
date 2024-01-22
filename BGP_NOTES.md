# BGP NOTES
Notes: 
* AD is only for routing tables, it does not affect BGP selection process
 IBGP AD 200
 EBGP 20
* You can assigna prefix a 200 AD if you use a ```network <prefix> <mask> backdoor``` command. 
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

## NEIGHBORS
- TCP port 179; src IP is the interface
   - update-source can be used to change the src interface neighbor <X> update-source <intf>
- Staes are 
    Idle: up and good but no routes exchanged (starting)
    Connect: actively trying to connect
    Active: if the connection times out (the router will actively retry to conenct)
    OpenSent: Open message sent but no response or keep alive received yet
    OpenConfirm: Messages have been exchanged and parameters agreed
    Established: UP and running   
- Authentication in the TCP headers (option19 - Md5 hash)
- Established if AS match configurations/authentication/address families match
  - IBGP TTL is set to 255
  - EBGP TTL is set to 255 but only 254 is accepted (default) /  ebgp-multihop <hops> if TTL >1 is requried, it will accept TTL up to 255-<hops>
    disable-connected-check also allows for loopbacks to be used (but not further than that, i.e. no routers in between)
  - Use TTL security to set the TTL to <hop> counts instead: neighbor <IP> ttl-security hops <X>   
- next-hop self: for IBGP, changes the next-hop (remember next-hop does not usually change in IBGP 
                 or confederation (fake) EBGP); the value set is the on used for the TCP connection with the neighbor
   - next-hop can also be set (selectvely) via a route map applied to a neighbor (option set ip next-hop <IP>)       
- neighbors can be configured in BGP peer groups (optimizes resources, updates are computed per peer group and not per neighbor)    
- you can do conditional advertising with the syntax:
    neighor <IP> advertise-map <MAP1> exist-map/non-exist <MAP2>
  where <MAP1> is a route-map matching the prefixes to advertise and <MAP2> matches the prefix to monitor 
  They need to be (or not) in the BGP table to enable the advertisemnts.  Note that when we say match is any type of match
- you can limit the prefixes received from a neighbor with:
   neighbor <IP> maximum-prefix <Number> [<Threshold%>] [warning-only]|[restart <minutes>]
     - if restart is used, the rotuer will tear down the connection and wait <minutes> before re-establishing it
- A neighbor can present itself with a different AS Number by using: 
    neighbor <IP> local-as <AS2> [no-prepend [replace-as]]     
  <AS2> is sent in the OPEN message and it is prepended to routes sent to the neighbor: <AS2><AS> (this means the neighbor
  will see the prefix as transited through AS and received from AS2)
  no-prepend only applies to received routes!
  if replace-as is used, the original AS is completely removed (note: this can of course cause routing loops)
- neighbor <IP> remove-private-as : will remove all private AS in the beginning of the AS_PATH sequence for the prefixes
                                    SENT to the neighbor (it will not change values if they are not in the beginning)
- neighbor <IP> advertisement-interval <seconds> : sets the timers for neighbor updates     
- fast fallover for neighbor can be configured (I guess modern way would be to use bfd):
    - global bgp: bgp fast-external-fallover  is required (default).
    - command: neighbor <IP> fall-over 
    Note that this feature is only efficient when the peering session is established across the non-shared link; 
    when the IGP route to the peer disappear, the neighbor is considered down immediately
    Again probably we use BFD now..                              
- ALLOW-AS IN: use: ```neighbor <IP> allowas-in [count]``` 
  if you want to accept routes that have its local AS in the path 
  MPLS PE use (usually) as-override that replaces the incoming AS with the PE AS so that when the update is received it is not dropped                                  

## ROUTES EXCHANGES
- IGP synchronization: now nostlydisabled; it used to require that for every IBGP route a matching IGP route should be present)
                       the idea was to prevent black holes
    Note: BGP can have a route in rib failure if the same prefix is present in an IGP with better AD
          even if RIB failure they are still advertised (route is still present) but you can use suppress inactive to
          avoid that                   
- IBGP learned rotues can not be sent to other IBGP neighbours (full mesh requirement)   
  - ROUTE REFLECTOR are neighbours that reflect router to other IBGP peers
    the router reflector uses: neighbor <X> router-reflectr-client (to send traffic)
    routes learnt by a client are sent to everyone, routes learnt by non client(IBGP) are sent to clients
    EBGP routes are sent to everyone
    - attributes are not updated but 2 are added as loop prevention
        - Originitor ID: IBGP router originating the route
        - Cluster List: List of IBGP clusters (i.e. a cluster is a RR and its client) 
            - clusters are a way to optimize RR/clients distribution, e.g. keeping RR and its clients geographically local
            - RR in different clusters peer (but are not clients)
  - CONFEDERATIONS
    - router bgp <AS> refers to the confederation AS (usually private AS range (64512 – 65535))
    - confedration id refers to the actual main AS
    - use confiderations peers (other as in the same confederation id)          
    - peering between confederation peers use EBGP rules, inside the same confederation sub-AS IBGP (so RR still possible)
    - Atribute: AS_CONFED_SET: an unordered list of Sub-ASs that is prepended onto the normal AS-Path as the prefix 
               is passed between Sub-ASs. The value is stripped and replaced by the confederation id when a prefix 
               is advertised to a true EBGP pee
- Only the best path is installed in the routing table and sent to neighbors
- EBGP leanred routes keep the same value for the next-hop when sent to IBGP neighbors (by default)
- bgp redistribute internal is required to enable redistribution from BGP to IGP

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
     bgp dampening [<Half_Life> <ReuseLimit> <SuppressLimit> <MaximumSuppressTime> ]
     e.g. bgp dampening 4 750 2000 16
 - you can apply route dampening with a route-map and specify the dampening values inside the route-map 
Side Note that a way to reduce network instability is by using aggregation    


## ROUTES
- use network statement (mask can be omitted if classful)
  - the route needs to be in the routing table (possibly as null0)
  - auto-summary (bgp global will install the route as classful )
- BEST PATH SELECTION:
   - excludes prefix if next hop not resolvable
   - excludes prefixes if synchronization is enable and no IGP prefix present
   - excludes prefixes with its own AS number in AS path
   SELECTION PREFERENCE:
   - Highest wieght (Cisco) -  device local only
       - set via route-map
   - Highest Local preference - AS local
      - used to determine the way traffic leaves the AS 
   - Locally originated prefixes (via network, aggreagte-address, redistribute)
   - shortest AS PATH
      - used to influence incoming traffic
      - use AS PATH prepending (EBGP only) 
      - Sub-AS from a confederation do not count
      - can be disabled with: bgp bestpath as-path ignore
      - a max can be set before rejecting the route: bgp maxas-limit <N>
   - Lowest orgin type: IGP < EGP(legacy/unused) < INCOMPLETE (redistribution)
      - you can set the origin attribute.. but this is basically never used to determine best routes
   - Lowest MED (Multi Exit Discriminator/metric)
      - set to influence incoming traffic (it is non transitive/will not be propagated outside the AS when received)
      - the receivng AS router can ignore it
      - MED is used only if the prefixes come from the same AS (but can be configrued to always compare med)
      - Hot potato routing (do not care about med, just get the packet out of the AS)
      - Cold potato routing (route the packet inside the AS until it gets closer to the destination: lowest MED)
      - if missing you can set is as the highet value: bgp bestpath med missing-as-worst
      - can be non deterministic, use: bgp bestpath deterministic-med 
   - EBGP routes over IBGP routes
   - lowest IGP metric to next hop
   - lowest BGP router id

### DEFAULT ROUTE
  You may inject a default route into BGP by using the network 0.0.0.0 mask 0.0.0.0 command, if there is a default route in the RIB. 
  However, to selectively generate a default route, use the command: 
    neighbor <IP> default-originate [route-map <CONDITION>] . 
  Without the route-map parameter, this command will generate a default route and send it to the configured peer. 
  It is not required to have a matching default route in the BGP table or the RIB   

## FILTERING
  Filtering order is 
   INBOUND:  1. route-map, 2. filter-list,  3. prefix-list OR distribute-list
   OUTBOUND: 1. prefix-list OR distribute-list,  2. filter-list, 3. route-map
  - usually done with neighbor route-maps and prefix-lists 
  - also done with neighbor distribute-lsit and standard/extended acls
    Note that with extended acls, the logic is src subnet + wildcard and destination mask + wildcard
    e.g. permit ip 192.168.0.0 0.0.0.255 255.255.255.0 0.0.0.255 -> any subnet in 192.168.0 and any 
         mask option starting from 255.255.255.
  - AS_PATH filtering is done via regex, some examples:
      “^$”    - means an empty AS_PATH attribute, i.e. generated by the local AS.
      “^254_” - prefixes received from the directly adjacent AS 254. Note that using “_” is important to avoid matching with 2541 for instance
      "_254_" - prefixes transiting AS 254. 
      “_254$” - prefixes originated in the AS 254.
      “^([0-9]+)_254” - routes from the AS 254 when it’s just “one-hop” away.
      “^254_([0-9]+)” - prefixes from the clients of the directly connected AS 254.
      “^(254_)+([0-9]+)” - prefixes from the clients of the adjacent AS 254, accounting for the fact that AS 254 may do AS_PATH prepending.
      “^254_([0-9]+_)+”  - prefixes from the clients of the adjacent AS 254, accounting for the fact that the clients may do AS_PATH prepending.
      ^\(65100\) - prefixes learned from the confederation peer 65100, note: they are inside ().
    Create the regex in a as-path access-list:  ip as-path access-list <N> {permit|deny} <Regexp>   and apply it as a:
       - neighbor <IP> filter-list <as-path-acl-name> in/out
       - neighbor <IP> route-map <MAP with filter list applied with: match as path <as-path-acl-name> > in
       - test with show ip bgp regexp or show ip bgp quote-regexp 
  - OUTBOUND ROUTE FILTERING (OBF): used to push a filter to a neighbor
    It is a capability that needs support on both routers and needs to be enabled:
      neighbor <IP> capability orf prefix-list [send|receive|both]        (both peers need this)
      neighbor <IP> prefix-list <NAME> in                                 (on the router that pushes the filter)
  - SOFT RECONFIGURATION: use the command:
      neighbor <IP> soft-reconfiguration inbound
    without this, it is not possible to tell a neighbor to resend the updates, also allows to have an unfiltered copy
    of the prefixes received (double memory utilization though..) - different show commands, e.g. show ip bgp neigh <IP> routes vs received-routes  
         

# EQUAL/UNEQUAL COST PATH LOAD BALANCING
  requriements (equal cost path lo):
  - same attributes up to MED
  - same type (either iBGO or eBGP)
  - same IGP cost to next-hop
  - command: maximum path [ibgp] <number>
  unequal cost:
  - command: maximum path [ibgp] <number>
  - enabled on border router with:
     - global bgp command:  bgp dmzlink-bw
     - per neighbor: neigbor <IP> dmzlink-bw to select which neighbor load balance with 
  - the ebgp prefixes will carry a new attribute (ext community) with the bandwith of the link to the neighbors
    so send-community extend is required   

## AGGREGATION
  - to aggreagte IGP routes you can create a static route to null 0 and use the newtok command
  - Autosummary is always an option (not a great one) 
  - aggreagte-address <prefix> <mask> , requires one subnet in the range to be in the BGP table (not neessarily the routing table)
    Note that:
     - the original sub prefixes are still advertised by default, unless you use: 
        - aggregate-address <prefix> <mask> summary-only
           - prefixes can be unsuppressed per neighbor with: neighbor <IP> unsuppress-map <route-map>        
        - aggreagate-address <prefix> <mask> suppress-map <route_map>: selectively supree prefix with prefix-lists in route-maps             
     - a null route is created
     - the new prefix will:
        - have empty bgp as-list (default) 
           - a list of AS from the summarized prefixes can be generated with the command: as-set
             aggregate-address <prefix> <mask> as-set (only used for loop prevention)
             Note: with as-set, all the other attributes are also inherited including communities!
             You can remove the attributes with an attribute-map or you can
             decide which prefixes should be used to generate the attributes using an: advertise-map ,e.g
               aggregate-address <IP> <MASK> summary-only as-set advertise-map ADVERTISE_MAP
        - have extra attributes: 
          - ATOMIC_AGGREGATE (to inform it's an aggregate and some other attributes are missing)
          - AGGREGATOR: AS number and router id of the router generating the aggreagte
        - be seen as originated by the local AS
  - CRI: Conditional route injection, can be used to un-suppress prefixes from an aggregate; the difference
    with unsuppress-map is that, this is NOT DONE ON THE AGGREGATOR ROUTER BUT ANY ROUTER CAN DO IT.
    It requires 2 route-maps; the first specifies the prefixes to be injected (you may/should also set other BGP attributes
    or it will have none), AS_PATH attribute is reset to an empty list. The second route-map defines the conditions to meet 
    for the new prefixes to be injected: bgp inject-map <MAP1> exist-map <MAP2>

## COMMUNITIES
BGP communities are optional transitive attributes used mainly to associate an administrative tag to a route. 
32 bit, either completely numeric or in <ASN>:<number> format using: ip bgp-community new-format
 - neighbor can exchange communitiies if configured with: neighbor <IP> send-community extended
     - you can set community inside a route map and apply that to neighbors: in/out
 - aggregate prefixes using as-set will inheirt all communities
   - communities can also be set in aggregate routes with: attribute-map
     in particular you might want to remove some communities, use: set community none
     inside a route map and pply it to aggregate command as attribute map
 - communities are set via route-maps
    - set community <community-list> [additive]
 - communities can be matched with community-list
    - wildcards can be used in community-lists    
 - you can delete some communities from a lsit of communities by:
     - creating a community list with prefixes to remove, e.g. COM1
     - creating a route-map and using the command: set comm-list COM1 delete
       Note that in the same route-map entry you can add other community using: set community <AS:new> additive
 - well known communities:
    - no-export: the prefix will not be advertised to the neighbor AS, only to IBGP peers       
    - no-advertise: the prefix will not be advertised to any peer
                    note: if you set it via a neigh route-map inbound, all prefixes received will not be advertised
    - no-export-subconfed/local-as: same as no export but for confederation, prefixes are forwarded only to peers in the same confederation as
    