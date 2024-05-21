# Junos Intermediate Routing

<img src="pictures/Basic 4 Routers.png" alt="Basic 4 routers jlab topology" style="height: 600px; width:600px;"/>

## Basic static routing
```
[R1]
set interfaces ge-0/0/0 unit 0 description "To R2"
set interfaces ge-0/0/0 unit 0 family inet address 100.100.100.1/24

set interfaces lo0.0 family inet address 10.10.10.1/32
set interfaces lo0.0 family inet address 10.10.10.2/32
set interfaces lo0.0 family inet address 10.10.10.3/32
set interfaces lo0.0 family inet address 10.10.10.4/32

set routing-options static route 10.10.20.1/32 next-hop 100.100.100.2
set routing-options static route 10.10.20.0/29 next-hop 100.100.100.2

show routing-options
run show route

[R2]
set interfaces ge-0/0/0 unit 0 description "To R1"
set interfaces ge-0/0/0 unit 0 family inet address 100.100.100.2/24

set interfaces lo0.0 family inet address 10.10.20.1/32
set interfaces lo0.0 family inet address 10.10.20.2/32
set interfaces lo0.0 family inet address 10.10.20.3/32
set interfaces lo0.0 family inet address 10.10.20.4/32

set routing-options static route 10.10.10.1/32 next-hop 100.100.100.1
set routing-options static route 10.10.10.0/29 next-hop 100.100.100.1

show routing-options
run show route

run ping 10.10.10.1 source 10.10.20.1
```

## Qualified Next-Hop (or Floating Static routing)
Used as a backup in case the primary fails
it's just a way to associate an additional next-hop to the same route 

This is a normal static route and additional static route with next hop 
via different interface with higher preference (default preference is 5)
```
[R1]
set routing-options static route 10.10.10.1/32 next-hop 100.100.100.1
set routing-options static route 10.10.10.1/32 qualified-next-hop 100.100.200.1 preference 6


# show routing-options static
route 10.10.10.1/32 {
    next-hop 100.100.100.1;
    qualified-next-hop 100.100.200.1 {
        preference 6;
    }
    preference 5;
}
```

## Static Route Default Options
This will setup different defaults for all new static routes.  
Examples:
 - change the default **metric** values (when redistributed) 
 - change the **preference** value (this is the Cisco AD)
 - set BGP AS or community
 - set **no-readvertise** to prevent any redistribution into routing protocols
 - set **resolve** to allow for recursive reoslution of next-hop
 - set: **tags** (same as Cisco route rags)
 - set: **color** for traffic engineering

```
edit routing-options static default
@R1# set ?
Possible completions:
  active               Remove inactive route from forwarding table
+ apply-groups         Groups from which to inherit configuration data
+ apply-groups-except  Don't inherit configuration data from these groups
> as-path              Autonomous system path
> color                Color (preference) value
> color2               Color (preference) value 2
+ community            BGP community identifier
  install              Install route into forwarding table
  longest-match        Always use longest prefix match to resolve next hops
> metric               Metric value
> metric2              Metric value 2
> metric3              Metric value 3
> metric4              Metric value 4
  no-install           Don't install route into forwarding table
  no-longest-match     Don't always use longest prefix match to resolve next hops
  no-readvertise       Don't mark route as eligible to be readvertised
  no-resolve           Don't allow resolution of indirectly connected next hops
  no-retain            Don't always keep route in forwarding table
  passive              Retain inactive route in forwarding table
> preference           Preference value
> preference2          Preference value 2
  readvertise          Mark route as eligible to be readvertised
  resolve              Allow resolution of indirectly connected next hops
  retain               Always keep route in forwarding table
> tag                  Tag string
> tag2                 Tag string 2
[edit routing-options static defaults]
```
The defaults can all be **over-ridden** by specific route attributes when configuring the specific routes

## Aggregated Routes

If we have a set of static routes we can build an aggreagte route (default preference is 130 vs 5)
Notes:
- you need contributing routes for the aggregate to show up
- Use: **show routing-options aggregate [detail]** to check what you aggregate
- The state of the aggregate is **reject**(Sends ICMP unreachable) or **discard** (silent).  
  This is the same as  **Null0** for Cisco: most specific routes are used to reach actual destinations. 
- to generate a **DEFAULT ROUTE** the command is `set routing-options generate route 0/0`
  - In this case, the next-hop is actually set to an IP coming from the **primary** contributing route
  - You can generate other routes.. not necessarily a default..
  - **generate routes** will need actual contributing routes.. local interfaces routes do not count
- This is done mainly to redistribute to specific routing protocols
```
[R1]
set routing-options static route 10.10.20.1/32 next-hop 100.100.100.2
set routing-options static route 10.10.20.2/32 next-hop 100.100.100.2
set routing-options static route 10.10.20.3/32 next-hop 100.100.100.2
set routing-options static route 10.10.20.4/32 next-hop 100.100.100.2

set routing-options aggregate route 10.10.20.0/30 


R2# run show route

inet.0: 11 destinations, 11 routes (11 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both
[...]
10.10.20.0/30      *[Aggregate/130] 00:00:08
                       Reject        <------ Note: it's rejecting it.. it would drop traffic


R1# run show route protocol aggregate detail 

inet.0: 11 destinations, 11 routes (11 active, 0 holddown, 0 hidden)
10.10.20.0/30 (1 entry, 1 announced)
        *Aggregate Preference: 130
                Next hop type: Reject, Next hop index: 0
                Address: 0xc4b4eb4
[...]
                Contributing Routes (3):
                10.10.20.1/32 proto Direct  <- route that generate the aggregate
                10.10.20.2/32 proto Direct  <- route that generate the aggregate
                10.10.20.3/32 proto Direct  <- route that generate the aggregate

#
#
#############################################
# To generate a default route 
 
R2# set routing-options generate route 0/0

R2# run show route protocol aggregate detail

inet.0: 11 destinations, 12 routes (11 active, 0 holddown, 0 hidden)
0.0.0.0/0 (2 entries, 1 announced)
         Aggregate Preference: 130
                Next hop type: Router, Next hop index: 580
                Address: 0xc4b5a14
                Next-hop reference count: 4
                Next hop: 100.100.100.1 via ge-0/0/0.0, selected
[...]
                Contributing Routes (1):
                10.10.10.1/32 proto Static

```

## Martian Addresses
These are routes that Juniper **will not allow in the routing table.**  
Some these IPs are internal and even if they don't show up as **martians** you really should not use them.  

```
R2# run show route martians 

inet.0:
             0.0.0.0/0 exact -- allowed           <-- this is allowed
             0.0.0.0/8 orlonger -- disallowed
             127.0.0.0/8 orlonger -- disallowed
             192.0.0.0/24 orlonger -- disallowed
             240.0.0.0/4 orlonger -- disallowed
             224.0.0.0/4 exact -- disallowed
             224.0.0.0/24 exact -- disallowed

inet.1:
  [...] # pretty much the same repeated for all inet routing instances
```
You can possibly change the martian addresses, e.g. you can allow class E: 224.0.0.0/4 and disallow 8.8.8.0/24 or longer prefixes, you can do this:public range
```
[edit]
R2# set routing-options martians 224.0.0.0/4 exact allow    
R2# set routing-options martians 8.8.8.0/24 orlonger
R2#
R2# show | compare 
[edit routing-options]
+  martians {
+      224.0.0.0/4 exact allow;
+      8.8.8.0/24 orlonger;
+  }
```

## Load Balance
By dfault Juniper does not allow load balancing because in the forwarding table, it will install a single route, however you can setup a routing-policy and tell Juniper to move every route that can be load balanced into the FIB.
Once this is set, it can be used by any routing protocols so that if they have equal cost path they will use it automatically.

Notes:
- Juniper does not do load balancing per packet but **per flow** i.e. `source address, destination address, protocol` (possibly even L4 information)
  The commands howeve still refer to this as **per-packet**
- Load Balancing is unidirectional.. i.e. it does not control how the traffic comes back on the same link and you could have asymmetrical routing..
  This should be fixed if it is setup in the same way at both sides of the link
  
```
set interfaces ge-0/0/0 unit 0 family inet address 100.100.100.2/24
set interfaces ge-0/0/1 unit 0 family inet address 100.100.200.2/24

set routing-options static route 10.10.10.1/32 next-hop 100.100.100.1
set routing-options static route 10.10.10.1/32 next-hop 100.100.200.2

R1# run show route 
[...]
10.10.10.1/32      *[Static/5] 00:00:09
                       to 100.100.100.1 via ge-0/0/0.0
                    >  to 100.100.200.1 via ge-0/0/1.0
```
to enable multiple routes, below we:
-  setup the routing policy
-  apply it to the forwarding table

Note:
- in the routing table it will still show a single path but in the forwarding table it will show both
- you can actually use a **from** statement in the routing-policy to specify exactly what route you want to load-balance (e.g. something like:  
 `set policy-options policy-statement Load-Balance term 1  from route-filter 1.1.1.1/32 exact `)

```
R1# set policy-options policy-statement Load-Balance term 1 then load-balance ?
Possible completions:
  consistent-hash      Give a prefix consistent load-balancing
  destination-ip-only  Give a destination based ip load-balancing
  per-packet           Load balance on a per-packet basis
  random               Load balance using packet random spray
  source-ip-only       Give a source based ip load-balancing

R1# set policy-options policy-statement Load-Balance term 1 then load-balance per-packet  
R1# set routing-options forwarding-table export Load-Balance


###########################################
# show route and forwarding table

R1# run show route 
[...]
10.10.10.1/32      *[Static/5] 00:00:09
                       to 100.100.100.1 via ge-0/0/0.0
                    >  to 100.100.200.1 via ge-0/0/1.0  # only 1 path here

R1# run show route forwarding-table 
Routing table: default.inet
[...] 
# both paths enabled here
10.10.10.1/32      user     0                    ulst  1048574     2
                              100.100.100.1      ucst      580     3 ge-0/0/0.0 
                              100.100.200.1      ucst      594     3 ge-0/0/1.0
```
Note you can also **edit the forwarding options** to setup Layer3 and Layer4 for the load balancing algorithm (they need to be both present)
```
R1# edit forwarding-options hash-key family inet   

[edit forwarding-options hash-key family inet]
jcluser@R1# set ?
Possible completions:
+ apply-groups         Groups from which to inherit configuration data
+ apply-groups-except  Don't inherit configuration data from these groups
> layer-3              Include Layer 3 (IP) data in the hash key
> layer-4              Include Layer 4 (TCP or UDP) data in the hash key
> symmetric-hash       Create symmetric hash-key with source & destination ports

R1# set layer-3
R1# set layer-4
R1# top show compare
[edit]
+  forwarding-options {
+      hash-key {
+          family inet {
+              layer-3;
+              layer-4;
+          }
+      }
+  }

```
