# VRF LITE

By default, all interfaces (physical or sub-interfaces) are assigned to a VRF known as the **global**, (i.e. the regular routing table).  
To create a new VRF, issue the command:
```
! create a vrf
ip vrf <VRF_NAME>

! define a RD (X and Y are 32-bit)
  rd <X>:<Y>

! Define static routes in the VRF
! Note: you could point to an interface in a different VRF (but don't)  
ip route vrf <NAME> PREFIX MASK [interface] [next-hop] 

! Set an interface in the vrf
interface <X>
  ip vrf forwarding <VRF_NAME>
!
! some show commands
show ip vrf
show ip route vrf <VRF_NANE>
show ip arp vrf <VRF_NAME>  

ping vrf <VRF_NAME> <IP> source <INTF>
```  

You must define a **route distinguisher (RD)**   numbers: a special 64-bit prefix prepended to every route in the respective VRF routing table.  
The common format for an RD is the combination ```ASN:NN```, where ASN is the autonomous system number and NN is the VRF number inside the router  
Alternatively, you may use the format ```IP-Address:NN```, where IP is the router’s IP address and NN is the VRF name. 


# MPLS

Multi-Protocol Label Switching, or MPLS tunnels, known as LSPs (Label Switching Paths), are similar to Frame-Relay or ATM PVCs. 

In MPLS a stack of labels is inserted between the original Layer 2 and the Layer 3 header.  
Per RFC, every MPLS label starts with a **20-bit value** but the actual **tag is 32 bits** due to special and reserved fields.  
If a packet carries the stack of MPLS labels, every router performs switching based on the **topmost** label based on the **Label FIB(LFIB)**, which maps incoming labels to their outgoing equivalents (**label lookup**).  
Flow:
* The first router on the edge of an MPLS cloud is known as a LER or **Label Edge Router**
* The LER is responsible for inserting (pushing) the initial label. 
* The routers inside the MPLS cloud are known as **LSRs** or **Label Switching Routers** 
* LSRs swap labels found in the packets (perform pop and push operations) and switch packets further. 
* The last LER along the LSP is responsible for popping the label and switching the packets further using traditional prefix lookup mechanics.

The fundamental core of MPLS centers on how the labels are assigned. A tunnel path is established for every IGP prefix found in the network. This allows us to replace packet switching based on destination prefix lookup with switching based on label swapping. 

## MPLS LDP
MPLS ( RFC3036) uses a protocol called **Label Distribution Protocol (LDP)** to exchange label values.  
By default, every router will generate a local label for every prefix found in its routing table and advertise it via LDP to its neighbors.  
This is the label that adjacent routers must use when switching for a prefix via the local router.   
* LDP broadcasts all local prefixes with their respective labels. 
* when a router learns the labels used by its neighbors for a prefixes, it programs the LFIB with respective label values:
* ```incoming label``` (locally generated) to  ```outgoing label``` (used by the neighbor)

Steps:
* MPLS is enabled on an interface:
  ```
  interface <X>
    mpls ip
  ```
  Note you can also enable it inside a routing protocol process on all interfaces with: ```mpls ldp autoconfig```
  * LDP sends hello to ```224.0.0.2:646```
* Neigbors learn about the new router; the router id is by dfault the highest loopback but can be set with: ```mpls ldp router-id <interface> force```
  * If the loopback are not reachable, TCP connection will not be established
  * You can use the IP of the physical itnerfaces for the connection, with: ```mpls ldp discovery transport-address interface```
* The TCP connection is established and possibly authenticated with:
```
! IP is the neighbor router ID
mpls ldp neighbor <IP> password <pwd>
mpls ldp password required
```    
* routers exchange prefixes/labels and populate the LFIB
  * Note: routers need to have the same prefixes in the routing tables which means be very careful with summarization.
* Run show commands:
  ```
  ! this output is pretty self explanatory
  # show mpls ldp neighbor [password]
  [...]
  !
  !
  ! Local Label is the label assigned locally and sent to the other routes
  ! Outgoing is the label pushed when sending out the packet
  ! Pop Label means remove the label (implicit null label)
  # show mpls forwarding-table
  Local      Outgoing   Prefix          Bytes Label    Outgoing      Next Hop  
  Label      Label      or Tunnel Id    Switched       Interface     
  19         Pop Label  150.1.4.4/32       0          Gi1.146    155.1.146.4
  21         16         150.1.5.5/32       0          Gi1.146    155.1.146.4
  27         Pop Label  155.1.0.0/24       0          Gi1.146    155.1.146.4
  
  ```
By default, LDP will generate and advertise labels for every prefix found in the local routing table. If you want to change this behavior and generate labels only for specific prefixes, you may use an access-list to select the prefixes eligible for label generation.
```
access-list 10 permit <prefix> <wildcard>
!
no mpls ldp advertise-labels
mpls ldp advertise-labels for 10
```

# MP-BGP VPNv4

MPLS VPNs establish a full-mesh of dynamic MPLS LSRs between and PE (Provider Edge) routers use them for tunneling VPN packets across the network core.  
To select the proper VRF instance on the endpoint PE router, an additional label is needed that selects the proper FIB entry associated with the target VRF. This requires two labels in the MPLS stack; one label **(the topmost)** is the **transport** label, swapped along the path, and the other label **(innermost)** is the **VPN** label, is used to select the outgoing VRF.  
BGP has been chosen as a universal prefix redistribution protocol.  
The address family **VPNv4 (VPN IPv4)** has been added. Every **VPNv4 prefix has the RD associated with it and the corresponding MPLS label**, in addition to the normal BGP attributes. This allows for transporting different VPN routes together and performing best-path selection independently for each different RD.  
The VPNv4 address-family capability is activated **per-neighbor** using the respective address-family configuration (if you don’t want the default ipv4 and only need the VPNv4 prefixes to be sent, you can disable the default behavior via the command ```no bgp default ipv4-unicast```).    
There are limitations for iBGP peering sessions for VPNv4 prefix exchange:
* They must be sourced from a Loopback interface
* This interface must have a /32 mask (this is not a strict requirement on all platforms). 

This is needed because:
* the BGP peering IP address is used as the NEXT_HOP for the locally originated VPNv4 prefixes. 
* When the remote BGP router receives those prefixes, it performs a recursive routing lookup for the NEXT_HOP value and finds a label in the LFIB. 
* This label is used as the transport label in the receiving router. Effectively, the NEXT_HOP is used to build the tunnel or the transport LSP between the PEs. 

The VPN label is generated by the BGP process on the advertising router and directly corresponds to the local VRF route.  
The /32 restriction is needed to guarantee that the transport LSP terminates on the particular PE router, and not some shared network segment.  
To inject a particular VRF’s routes into BGP, you must
* activate the respective VRF address-family under the BGP process 
* enable route redistribution (such as static or connected). 

All the respective routes belonging to that particular VRF will be injected into the BGP table with their RDs and have their VPN labels generated.   
The import process is a bit more complicated and is based on the concept of **Route Targets**.

A **Route Target (RT) is a BGP extended community attribute**. These BGP attributes are transitive and encoded as 64-bit values (as opposed to normal 32-bit communities). They are used for enhanced tagging of VPNv4 prefixes because you cannot just use Route Distinguishers for prefix importing/exporting, as prefixes could belong to different VRFs.  
* by default, all prefixes redistributed from a VRF into a BGP process are tagged with the extended community X:Y specified under the VRF configuration via the command ```route-target export X:Y```  
  * You can use as many ```export``` commands as you wan.
* On the receiving side, the VRF will import the BGP VPNv4 prefixes with RTs matching the local command ```route-target import X:Y``` 
* The use of the command: ```route-target both X:Y``` means import and export at the same time.

Example config:
```
 ! Note in this example, the RD convention used is <AS>:<VRF_ID> (so the same RD is used in both rotuers)
 ! I do prefer to use <AS>:<router_ID> tbh
R1:
ip vrf VPN_A
  rd 100:1
  route-target both 100:1
!
ip vrf VPN_B
  rd 100:2
  route-target both 100:2
!
router bgp 100
  no bgp default ipv4-unicast
  ! <X> is an intermediate router not aware of the VRFs (peering only as vpnv4)
  neighbor <X> remote-as 100
  neighbor <X> update-source Loopback0
!
  address-family vpnv4 unicast
    neighbor <X> activate
    neighbor <X> send-community extended
!
  address-family ipv4 vrf VPN_A
    redistribute connected
    redistribute static
!
  address-family ipv4 vrf VPN_B
    redistribute connected
    redistribute static
 


R2:
ip vrf VPN_A
  rd 100:1
  route-target both 100:1
!
ip vrf VPN_B
  rd 100:2
  route-target both 100:2
!
router bgp 100
  no bgp default ipv4-unicast
  neighbor <X> remote-as 100
  neighbor <X> update-source Loopback0
!
  address-family vpnv4 unicast
    neighbor <X> activate
    neighbor <X> send-community extended
!
  address-family ipv4 vrf VPN_A
    redistribute connected
    redistribute static
!
  address-family ipv4 vrf VPN_B
    redistribute connected
    redistribute static
 
```
You can check the VPN labels assigned; remember that there are 2 VPN labels:
* VPN label (identifies the prefix in the VRF), you can find this in the BGP table; Note that this is the label we receive from the peer
at the other side of the VPN
* Transport Label, you can find this by looking at the next hop for the prefix in the MPLS forwarding table
```
R1# show ip bgp vpnv4 vrf VPN_A <prefix>
(also: show bgp vpnv4 unicast vrf VPN_A <prefix>)
  
BGP routing table entry for <RD>:<prefix>/<mask>, version 8
   Paths: (1 available, best #1, table VPN_A)
  !
Not advertised to any peer
Refresh Epoch 1
Local
  <next-hop> (metric 3) (via default) from <adv router> (<adv_router_id>)
    Origin incomplete, metric 0, localpref 100, valid, internal, best
    Extended Community: RT:<route target>
Originator: <originator>, Cluster list: <cluster_list> mpls labels in/out nolabel/23    !<--- this is the label received by R2

# show mpls forwarding-table <next-hop>
[..] -> this will show the label under Local Label

# Note you can also see all together looking at the cef table:
# show ip cef vrf VPN_A <prefix> detail
<prefix>, epoch 0, flags rib defined all labels recursive via <next_hop> label <VPN/VRF label>
 nexthop <neigbor X> <outgoing interface> label <transport Label>
```

## IMPORT/ EXPORT MAPS
If a granualr control over VRF import ad xport is required you can use import and export maps inside the vrf definition
You can use the export map to:
* limit the prefixes advertised to BGP by matchin prefixes-lists, access-lsits or extended communities
* selectively tag with specific **route targets** some prefixes

```
! this configuration will tag the prefixes matched by pl2 with a different RT
route-map VPN_A_EXPORT permit 10
 match ip address prefix-list <pl1>
 set extcommunity rt <rt1>
!
route-map VPN_A_EXPORT permit 20
 set extcommunity rt <rt2>
!
ip vrf VPN_A
 export map VPN_A_EXPORT
 route-target import 100:66

You can check the RT in the receiving routers with:
! on the receiving routers
# show ip route vrf VPN_A <prefix>

! on the transit vpnv4 router
show ip bgp vpnv4 rd <rd> <prefix>
```

# PE-CE Routing with OSPF
The MP-BGP cloud is to be considered somethig like a **“super area 0”** that is used to link all OSPF areas at different sites.  
This special “virtual area” is called the **OSPF super-backbone**, and it is emulated by passing OSPF VRF routing information in MP-BGP updates.  
**The use of the super-backbone allows us to avoid using area 0 at all**, so you can have non-zero OSPF aras connected to the backbone directly without the need for an area 0 at any site. 
Of course it’s also ok to have area 0 at different sites with non-zero areas attached to the super-backbone as well.  

The **main design principle**: all areas are connected to the super-backbone in a loopless start-like manner.  

OSPF routes redistributed into MP-BGP are:
* treated  like **Type 3 summary LSAs**, as they enter the super-backbone from other areas. This is true even if they are
  coming from the same area in different sites, because they traverse a super backbone area 0
* two extended-community attributes attached to them plus one normale attribute: 
  * **domain-id**, this is either the OSPF process numbers on the local router OR 
    explicitly configured with: ```domain-id``` under the OSPF process. 
    The assumption is that all OSPF processes within the same VPN using the same domain-id. 
    * If routes between use different domain-ids, the OSPF process will interpret them as **Type-5 External LSAs**
  * **OSPF route-type**, which has three significant fields: ```source area, route-type, and option```. 
     Usually depicted as triple X:Y:Z.  
     Y can be 2(intra-are), 3(inter-area), 5 (external), 7 (NSSA). 
     Z is the metric type for Y=5/7 or it’s the value 1,2 for E1,E2
  * **MED or metric**, copies the original route’s metric from the routing table. Note also that the metric is not incrememented
    by travelling in the MP-BGP cloud (unless the MED is manually modified)
  
If the areas are not connected in a star manner, you can have routing loops and to reduce the risks OSPF implements some **loop preventions rules**:
* All summary LSAs generated from the routes redistributed from BGP have a special **“Down”** bit set in the LSA headers.  
  *If a router receives a summary-LSA with the down bit set on an interface that belongs to a VRF, it simply drops this LSA*.  
  This is to prevent the case when a summary LSA is flooded across the CE site and delivered back to another PE. 
  * This feature may have to be disabled with the command: ```capability vrf-lite``` if you have CE routers configured with multiple VRFs
  * If ```capability vrf-lite``` is not supported, configure the PE routers with **different domain-IDs**: redistributed routes become **external** and bypass the down-bit check.  
  Note: this is true only for older router; in new ones, the down bit check is also applied to Type-5 (but they do support the capability command.
* Use **route tagging**. All routes redistributed via a particular PE will carry the OSPF route tag with the **BGP AS number**   
  If a PE gets a route tagged with the same it may believe it comes from abother PE in the same site and drop the route. If
  you want to disable this behaviour, just have the PE redistribute into OSP with a different TAG using:
  ```redistribute BGP <ASN> subnets tag Y``` .


## OSPF Sham-Links
OSPF prefixes learnt via the MPLS VPN become either **type-3** summary LSAs or **type-5** external LSAs. This can be a problem  if there is a backdoor link connecting two sites directly.   
The **backdoor link**  is supposed to be used as a backup but if the link is in the same area as the PE/CE routers, the PE routers will prefer the path across the back-door link.  
The solution is called an **OSPF sham-link**, which is similar to a virtual-link **connecting two PE routers** and configured in the same area as the PE routers:
*  This link is used to establish an OSPF adjacency and for the exchange of LSAs. 
*  The LSAs are then loaded in the OSPF database and the sham-link is used for intra-area path computations. 
   Note however thta the path is still established via MPLS LFIB.

The configuration of sham links is as follows:
* actual interfaces (usually loopbacks) in the respective VRF are used (no router-id like in virtual-links). 
* The IP addresses for these interfaces should be advertised into the VRF routing table **NOT BY OSPF** (usually BGP).
  The sham-link’s endpoints should not be advertised into OSPF
* Once the endpoints are reachable across the MPLS VPN, you may configure the sham-link using the command:
  ```
  area 1 sham-link <SRC><DST> cost X
  ```  
  Where <SRC> and <DST> are the IP addresses for the sham-link source and destination. The cost <X> is the OSPF metric value associated with traversing the MPLS core.


# PE-CE Routing with BGP
Configuring BGP for PE-CE routing requires only activating the respective VRF’s address family under the global BGP process and configuring the BGP peering sessions under this VRF. 
**There is no need to configure redistribution** : routes are propagated into the VPNv4 table automatically. 
**Prefix import and export is controlled by the route-target** .

A common problem is the reuse of the same **ASN** number but there are two solutions:
* Configure the ```allowas-in``` option inbound for the CE peering session. 
* Configure the ```as-override``` option on the PE routers ( the peering with the CE).  
  This compares the remote-AS (CE) with the AS number stored in the end of the AS_PATH attribute. If they match, the AS number in AS_PATH is replaced with the local PE router’s AS number ( the AS PATH length does not change so best path selection still works as usal).
  * To avoid prefixes where the original AS was over-ridden going back to the initial AS you should use the attribute: **Site-Of-Origin** **SoO** (similar to the out applied with a site-map in EIGRP)
  ```neighbor <IP> soo <VALUE>``` (you can also use a route map to apply it via a ```set extcommunity soo <VALUE> [additive]```)
  If **soo** is applied at all PE (with the same value) loops are prevented 

# DEFAULT ROUTING AND INTERNET ACCESS

In this (simple) case we inject a default route from the GLOBAL ROUTING TABLE into the VRFs.
If you instead want to leak a default from a different VRF you can just use the normal **import/export** approach using **RT**.  
In this case we also setup a NAT configuration (though usually you might want to do that in a Firewall or other device). The overall steps are:
* Create a special default VRF route that resolves via the global routing table: 
```ip route vrf <NAME> 0.0.0.0 0.0.0.0 <NEXT_HOP> global``` .   
* Redistribute this route into MP-BGP to propagate it to all VPN sites.
* Enable NAT on the Internet and Internal VRF links. 
* Create a global NAT address pool if needed. This address pool should be reachable via the global routing table.
* Configure a source NAT translation rule that matches the VPN source IP addresses and specifies either the global pool or the global interface for address translation.   
Use the keyword ```vrf <VRF_NAME>``` , which selects the source only from the particular VRF. 

Configuration Example:

```
R6:
interface <X>
 ! To the internet (no VRF: global routing table)
 ip address 160.1.106.1 255.255.255.0
 ! if we are doing NAT on the router.. (unlikely)
 ip nat outside
!
! default global route in vrf: VPN_A
ip route vrf VPN_A 0.0.0.0 0.0.0.0 GigabitEthernet <X> <GW> global
!
router bgp 100
 neighbor <GW> remote-as <PUBLIC_AS>
!
! we get to the internet by peering with a public GW
address-family ipv4
 neighbor <GW> activate
!
! inside the vrf we activate a default (redistribute the static)
address-family ipv4 vrf VPN_A
 default-information originate
 redistribute static
!
! if we are doing NAT on the router
interface <Y>
  ip vrf forwarding VPN_A 
  ip nat inside
!
ip access-list standard VPN_PREFIXES
 permit 150.1.0.0 0.0.255.255
!
ip nat inside source list VPN_PREFIXES interface GigabitEthernet<X> vrf VPN_A overload

!
! some show commands:
show ip route
show ip nat translation [verbose]
show ip route bgp !in the peers to check they get the default

```
