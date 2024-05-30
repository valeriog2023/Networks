# Junos Intermediate SP Switching - 1

# Bridge domains, Access/Trunk ports and IRB

This is similar to an SVI in Cisco world (if you enable IRB).  
In the SP world you usually do L2 on routers so you need to configure vlans with Bridge domains.  
Note that:
- once a range of vlans is configured , e.g. 10-20 if you run a set command again it will extend the previous range and **NOT** reset it.  
  So for instance, if you have vlans `10-20` configured and use the command `set bridge-domain <name> vlan-id-list [ 5 100-200 ]`  
  The final result will see in the bridge domains the vlan list: **5,10-20,100-200**.  
  **Trunk ports behave the same**
- The family to use when assign an interface to a bridge group is: **bridge** on routers and **ethernet-swithing** on SRX or switches (QFX/EX)  
  `vlan-list` / `vlan-id` would be replaced instead by `vlan members`
- I don't think you can setup a native-vlan on a bridge domain.. The command for native vlan is applied at the physical interface level and not at the unit level, i.e.:  
      `set interface ge-0/0/0 native-vlan <id>`  
   while the bridge vlan information is setup at the unit level..  
- if you setup a bridge-domain for a range of vlans it will actually create unde the hood a bridge domain for all vlans (prepended with the same name)
- **If you create a bridge-domain with vlan-list you can't use IRB**


```
! L2 Bridge domain
! Create a bridge domain
set brige-domains <name> description <description>
!
set brige-domains <name> vlan-id 10
! Also supported (but nor for IRB):
! set brige-domains <name> vlan-id-list 10-20
! set brige-domains <name> vlan-id-list [ 5 10-20 100-200 ]
!
!
!
! ACCESS PORT
set interfaces ge-0/0/0.0 family bridge interface-mode access vlan-id 10
!
! TRUNK PORT
set interfaces ge-0/0/0.0 family bridge interface-mode trunk vlan-id-list [ 10 20 ]
!
!
! IRB Setup
!  - create a unit of the irb interface using the vlan id
!  - map the bridge-domain to the irb unit
set interfaces irb unit 10 family inet address <ip/mask>
set bridge-domain <name> routing-interface irb.10

```

### Bridge Domains - show commands
```
# run show bridge domain

# run show bridge domain interface ge-0/0/0.0

# run show brdige mac-table

# run show brdige statistics
```



# Spanning Tree

Notes: 
  - Default flavour is Rapid Spanning Tree **(RSTP)** but you can change it to Per-VLAN Spanning Tree **(VSTP)** or Multiple Spanning Tree **(MSTP)**
  - on Cisco, if you do `show spanning-tree` you can see if you are on the root bridge explicitely: `This bridge is the root`.  
Juniper will not show anything explicitely so you need to figure it out yourself using `show spanning-tre bridge`:
    - **Root port** and **Root Cost** are missing from 
    - Local paramters -> Bridge ID match the Root ID
  - Default port cost for GigabitEthernet is **20000**


```
==================================    [RSTP]
set protocols rstp
set protocols rstp bridge-priority 0       ! -> 0 becomes root, priority can be set as 0,4k,8k,12k,16k,..,64k
set protocols rstp interface ge-0/0/0      ! -> you need to specify all interfaces one by one ('all' does not work)
set protocols rstp interface ge-0/0/1      
[...]
set protocols rstp interface ge-0/0/8

!
! Global Tuning:
set protocols rstp force-version stp ! for backward compatibility (otherwise just don't)
set protocols rstp forward-delay
set protocols rstp hello-time
set protocols rstp max-age



==================================    [Per Vlan Spanning Tree]
!
set protocols vstp vlan 10 bridge-priority 0
set protocols vstp vlan 10 interfacel all


==================================    [Multiple Spanning Tree]
!
! confifuration name and revision-level 
! need to be the same on all switches
set protocols mstp configuration-name MSTP-1
set protocols mstp revision-level
!
! instance 0 is created by default for all vlans not explicitely assigned
set protocols mstp msti 1 vlan <start1>-<end1>                           ! -->  instance number 1
set protocols mstp msti 2 vlan <start2>-<end2>                           ! -->  instance number 2
!
set protocols mstp interface ge-0/0/0
set protocols mstp interface ge-0/0/1


==================================    [Interface Tuning and Security]
!
set protocols rstp interface ge-0/0/0 ?
Possible completions:
  access-trunk         Send/Receive untagged RSTP BPDUs on this interface
> bpdu-timeout-action  Define action on BPDU expiry (Loop Protect)
  cost                 Cost of the interface (1..200000000)
  edge                 Port is an edge port                                      ! ------> This is the setting for portfast
  mode                 Interface mode (P2P or shared)
  no-root-port         Do not allow the interface to become root (Root Protect)  ! ------> This is the setting for root-guard
  priority             Interface priority (in increments of 16 - 0,16,..240) (0..255)
[...]

set protocols rstp interface ge-0/0/1 bpdu-timeout-action ?                     ! ------> This is Loopguard (when we stop receiving a BPDU)
Possible completions:
  alarm                Generate an alarm                                        ! Alarm action
  block                Block the interface                                      ! Block port action
[...]                                                                           ! you can have both set    


!
set protocols layer2-control bpdu-block interface ge-0/0/0                      ! ------> BPDU filter
!


```

### Spanning Tree - show commands
The show commands are the same for the protocol **rstp**, **vstp** and **mstp**.
```
# run show spanning-tree 


# run show spanning-tree bridge [detail]

STP bridge parameters 
Routing instance name               : GLOBAL
Context ID                          : 0
Enabled protocol                    : RSTP
  Root ID                           : 32768.2c:6b:f5:b4:10:d0
  Hello time                        : 2 seconds
  Maximum age                       : 20 seconds
  Forward delay                     : 15 seconds
  Message age                       : 0 
  Number of topology changes        : 0
  Local parameters 
    Bridge ID                       : 32768.2c:6b:f5:b4:10:d0
    Extended system ID              : 0


!
! my ports are blocked because they are currently down
# run show spanning-tree interface 

Spanning tree interface parameters for instance 0
Interface                  Port ID    Designated         Designated         Port    State  Role
                                       port ID           bridge ID          Cost
ge-0/0/0                   128:490      128:490  32768.2c6bf5b410d0        20000    BLK    DIS   <-- DIS == DISABLED
ge-0/0/1                   128:491      128:491  32768.2c6bf5b410d0        20000    BLK    DIS  



# run show spanning-tree statistics bridge
STP Context  : default
STP Instance : 0  
Number of Root Bridge Changes: 0         
Number of Root Port Changes:   0      


# run show spanning-tree statistics interface 
Interface     BPDUs       BPDUs        Next BPDU       TCs        Proposal    Agreement 
              Sent        Received     Transmission    Tx/Rx      Tx/Rx       Tx/Rx    
ge-0/0/0         0           0             0           0/0         0/0         0/0   
ge-0/0/1         0           0             0           0/0         0/0         0/0   


====================== MSTP ONLY
#
#
# run show shapping-tree mstp configuration
```



# 802.1q vs 802.1ad (q in q tunneling)
Dot1q only allows for 12 bits to be used for vlan identifier. In Juniper you could work around that having the vlans mapped to different  
route-engines (so you would have 4096 vlans per route-engine) but in the Service Provider world, you also don't want to:
- learn customer mac addresses if possible
- run spanning tree with the customer vlans

We can use use the **q-in-q** tunneling that uses two tags:
- **Inner** customer 802.1q header: Customer **C-tag**
- **Outer** Service Provider 802.1q header:  **S-tag**

Note: the SP will still have to learn the mac addresses from the vlans that are tunnelled by better control is possible (and also enforce  
limitations on number of vlans nad mac address on the customer side).  
In the SP deployment for **q-in-q** devices have a naming conventions that basically is the same as the one used in **MPLS**: 
 - CE,PE routers
 - **S-vlan bridges**: these are the same a P-routers in MPLS and are only interested in the **S-Tag**; they will forward frames coming from PE devices  
   based on their external S-Tag 
 - Customer, Network interfaces (the latter being the interface on a PE toward the SP network). The way the frame flows is as follows:  
   -  We expect the CE to have their interface toward the PE trunked; they will send out the frame with their own C-Tag  
   -  The PE Customer port will be set to **access** using the S-Tag assigned to the customer
   -  The Network interface on the PE will be set as trunk and it will send out the Customer Frame (inclunding the C-Tag) encapsulate in 
      the S-Tag
   - On the receiving side, the destination PE will receive the frame from the **S-vlan bridge** on its network port with the S-tag; they will  
     remove the S-tag and forward the frame to the Customer port with the initial C-Tag 

```
[Customer - CE]
! This is just configured to be a trunk port toward the PR
! We asusme they send vlan 10 tagged but any vlan would work

[SP - PE]
! Traffic will:
!  - come from customer CE on interface ge-0/0/0.0
!  - go to S-Vlan bridge out of interface ge-0/0/1.0
set bridge-domain Cust1 vlan-id 100
!
set interfaces ge-0/0/0.0 family bridge interface-mode access  
set interfaces ge-0/0/0.0 family bridge vlan-id 100
!
set interfaces ge-0/0/0.0 family bridge interface-mode trunk
set interfaces ge-0/0/0.0 family bridge vlan-id 100


[SP - S-vlan bridge]
! Notes:
!  - Traffic will come from PE1 on interface ge-0/0/0 and leave to PE-2 from interface ge-0/0/1
!  - The S-Vlan bridge needs to have q-in-q encapsulation enabled with flexible-vlan-tagginf
!
set bridge-domain Cust1 vlan-id 100
!
! we enable q-in-q on the ports toward the PE (but the same would be to a different core S-vlan bridge)
set interfaces ge-0/0/0 flexible-vlan-tagging
set interfaces ge-0/0/0 encapsulation flexible-ethernet-services
set interfaces ge-0/0/1 flexible-vlan-tagging
set interfaces ge-0/0/1 encapsulation flexible-ethernet-services
!
! we configure the ports as trunk with the customer S-Tag vlan id
set interfaces ge-0/0/0.0 family bridge interface-mode trunk
set interfaces ge-0/0/0.0 family bridge vlan-id 100
set interfaces ge-0/0/1.0 family bridge interface-mode trunk
set interfaces ge-0/0/1.0 family bridge vlan-id 100

```