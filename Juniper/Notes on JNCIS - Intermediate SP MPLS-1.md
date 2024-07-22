# Junos Intermediate SP MPLS-1

In Juniper, Label Switch routers (i.e. P routers) don't use inet.0 table to take forwarding decisions but the **mpls.0** table instead.
The PE routers instead (also known as Head end / Tail end) will use the **inet.3** table.
Note that in basic MPLS, the Penultime hop router will strip the labels off and send just the IP packet to the Tail end PE; this is called POP (Penultimate Hop Popping).
You can do instead ultimate Hop popping when you either want to test the full path (so test/admin traffic) or when you have multiple vrfs
at the destination and needs labels to determine the egress VRF

#### MPLS  HEADER:

<pre>
-----------------------------------------------------------------------------------------------------
|           8            |           16           |         24             |          32            |
|----------------------------------------------------------------------------------------------------
|              LABEL  VALUE (20 bit)                        | Exp (3)| S(1)|      TTL (8 bits)      |
-----------------------------------------------------------------------------------------------------
</pre>

<b>


In order to setup MPLS we need to:
 -   Enable it on the loopback and all interfaces that are going to be part of the MPLS path.  
    This enable interfaces to parse **mpls** packets (but does not enable mples globally yet)
    
     ```
     [edit]
     set interfaces lo0.0 family mpls
     set interfaces ge-0/0/0.0 family mpls
     set interfaces ge-0/0/1.0 family mpls
     set interfaces ge-0/0/2.0 family mpls
     set interfaces ge-0/0/3.0 family mpls

     set protocols mpls interface all   # on core devices or use
     set protocols mpls interface lo0.0
     set protocols mpls interface ge-0/0/0.0
     ```

 - You can now see the MPLS interfaces and the MPLS routing table: **mpls.0**
   ```
    # run show mpls interface 
    Interface        State       Administrative groups (x: extended)
    fxp0.0           Dn         <none>
    ge-0/0/0.0       Up         <none>
    ge-0/0/1.0       Up         <none>
    ge-0/0/2.0       Up         <none>
    ge-0/0/4.0       Dn         <none>
    
    
    # run show route 
    
    [...]
    
    mpls.0: 6 destinations, 6 routes (6 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both
    
    0                  *[MPLS/0] 00:00:19, metric 1
                           to table inet.0
    0(S=0)             *[MPLS/0] 00:00:19, metric 1
                           to table mpls.0
    1                  *[MPLS/0] 00:00:19, metric 1
                           Receive
    2                  *[MPLS/0] 00:00:19, metric 1
                           to table inet6.0
    2(S=0)             *[MPLS/0] 00:00:19, metric 1
                           to table mpls.0
    13                 *[MPLS/0] 00:00:19, metric 1
                           Receive
   ``` 

   Core / P routers will use the **mpls.0** table to router while PE routers will use **inet.3** (see later)


## Static LSP   

You can manually set an LSP path in a router inside the `protocols mpls` section; you need to:
- give a name to the path
- tell the router if it's going to be a transit or ingress/egress router
- specify the destination, i.e. what router should terminate the MPLS tunnel
- what is the next hop 
- specify what label to use (static LSP Path need to start from one milion)


Note that these path are unidirectional and only cover specific prefixes so they are **very rarely done**
```
edit protocols mpls
set static-label-switched-path R1-R2-R4 ingress to 10.100.100.4
set static-label-switched-path R1-R2-R4 ingress next-hop 10.100.12.2
set static-label-switched-path R1-R2-R4 ingress push 1000001
```

This will create an additional entry for the destination router in the **inet.3** table (as you can see we actually have it both tables now).  
Also note that they are pointing to different egress interfaces
```
10.100.100.4/32    *[OSPF/10] 02:05:18, metric 1
                    >  to 10.100.14.2 via ge-0/0/1.0
[...]
inet.3: 1 destinations, 1 routes (1 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both

10.100.100.4/32    *[MPLS/6/1] 00:00:11, metric 0
                    >  to 10.100.12.2 via ge-0/0/0.0, Push 1000001
```                    
but this is not actually enough because the endpoint router is still in the routing table.. so we also need to setup a static route
pointint to the name of the static LSP path we defined:
```
jcluser@R1# set routing-options static route 10.100.100.4/32 static-lsp-next-hop R1-R2-R4    


# run show route 10.100.100.4 
inet.0: 22 destinations, 23 routes (22 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both

10.100.100.4/32    *[Static/5] 00:01:12
                    >  to 10.100.12.2 via ge-0/0/0.0, Push 1000001    <<------ This is going to be preferred
                    [OSPF/10] 02:12:27, metric 1
                    >  to 10.100.14.2 via ge-0/0/1.0

inet.3: 1 destinations, 1 routes (1 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both

10.100.100.4/32    *[MPLS/6/1] 00:07:20, metric 0
                    >  to 10.100.12.2 via ge-0/0/0.0, Push 1000001

```

The configuration on the transit router and termination router is similar; in the transit router you need to specify:
- **transit** as type
- the **incoming** label and the new label to **swap** it with
- the next-hop

Before the MPLS packet actually reaches the termination router you want to pop the label, so the last configuration is actually done on the  
POP router (still consdier transit). In the snippet below bot configuration are shown 
```
[TRANSIT]
edit protocols mpls 
set static-label-switched-path R1-R2-R4 transit 1000001 swap 1000002 next-hop 10.100.24.2

[PEN ULTIMATE HOP]
edit protocols mpls 
set static-label-switched-path R1-R2-R4 transit 1000001 pop next-hop 10.100.24.2


```


## LDP
LDP automatically allocates labels for us and exchanges them between neighbours; First LDP will use hello UDP multicast packets (224.0.02 UDP/646)
to establish neighbours. Once neighbours are found it will switch start using TCP 646 toward the neighbours using the Loopbacks.
LDP will also look at every prefix in the routing tables IPv4 and IPv6 and assign labels locally and then advertise them to the niehgbours.

An underlying IGP is expected and every router is supposed to have full reachability and knowledge of every prefix in the network via IGP.
Note that information exchange in LDP happens in TCP so yo could have far away neighbours; this is technically possible and done in some specific cases.
Because LDP follows the underlying IGP you can't really do traffic engineering like you would do with RSVP.