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
To select the proper VRF instance on the endpoint PE router, an additional label is needed that selects the proper FIB entry associated with the target VRF. This requires two labels in the MPLS stack; one label (the topmost) is the transport label, which is being swapped along the entire path between the PEs, and the other label (innermost) is the VPN label, which is used to select the proper outgoing VRF CEF entry.
When a tunneling solution was found, a way to distribute VPN routes between the sites was needed. You cannot normally establish IGP protocol adjacencies across
You must load the initial configuration files for the section, MPLS MP BGP VPNv4, which can be found in CCIE R&S v5 Topology Diagrams & Initial Configurations.
  
MPLS LSRs because they are unidirectional. And even if a bi-directional tunneling solution such as mGRE were in use, establishing hundreds of adjacencies for OSPF across a network core would not work well from a scaling perspective. Because of these factors, BGP has been chosen as a universal prefix redistribution protocol.
To support these new features, BGP functionality has been enhanced to handle the VRF specific routes. A new special MP-BGP (multiprotocol BGP) address family named VPNv4 (VPN IPv4) has been added to BGP along with a new NLRI format. Every VPNv4 prefix has the RD associated with it and the corresponding MPLS label, in addition to the normal BGP attributes. This allows for transporting different VPN routes together and performing best-path selection independently for each different RD. The VPNv4 address-family capability is activated per-neighbor using the respective address-family configuration. By default, when you create a new BGP neighbor using the command neighbor <IP> remote-as <NR> , the default IPv4 unicast address-family is activated for this neighbor. If for some reason you don’t want this behavior and only need the VPNv4 prefixes to be sent, you may disable the default behavior via the command no bgp default ipv4-unicast .
There are special limitations for iBGP peering sessions that you want to enable for VPNv4 prefix exchange. First, they must be sourced from a Loopback interface, and second, this interface must have a /32 mask (this is not a strict requirement on all platforms). This is needed because the BGP peering IP address is used as the NEXT_HOP for the locally originated VPNv4 prefixes. When the remote BGP router receives those prefixes, it performs a recursive routing lookup for the NEXT_HOP value and finds a label in the LFIB. This label is used as the transport label in the receiving router. Effectively, the NEXT_HOP is used to build the tunnel or the transport LSP between the PEs. The VPN label is generated by the BGP process on the advertising router and directly corresponds to the local VRF route. The /32 restriction is needed to guarantee that the transport LSP terminates on the particular PE router, and not some shared network segment.
To inject a particular VRF’s routes into BGP, you must activate the respective address-family under the BGP process and enable route redistribution (such as static or connected). All the respective routes belonging to that particular VRF will be injected into the BGP table with their RDs and have their VPN labels generated. The import process is a bit more complicated and is based on the concept of Route Targets.

A Route Target is a BGP extended community attribute. These BGP attributes are transitive and encoded as 64-bit values (as opposed to normal 32-bit communities). They are used for enhanced tagging of VPNv4 prefixes. The need for route-target arises from the fact that you cannot just use Route Distinguishers for prefix importing/exporting, because routes with the same RD may eventually belong to multiple VRFs, when you share their routes.
Here is how route-target-based import works. By default, all prefixes redistributed from a VRF into a BGP process are tagged with the extended community X:Y specified under the VRF configuration via the command route-target export X:Y . You may specify as many export commands as you want to tag prefixes with multiple attributes. On the receiving side, the VRF will import the BGP VPNv4 prefixes with the route-targets matching the local command route-target import X:Y . The import process is based entirely on the route-targets, not the RDs. If the imported routes used to have RDs different from the one used by the local VRF, they are naturalized by having the RD changed to the local value. Theoretically, you may assign a route-target to every VPN site, and specify fine-tune import policies, to select the remote site routes accepted locally. Finally, notice that the use of the command route-target both X:Y means import and export statements at the same time.