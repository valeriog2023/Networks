# BATFISH NOTES 2


## BATFISH CONFIG ANALYSYS 

### VALIDATING NODE PROPERTIES
General node properties can be inspected via the `bf.q.nodeProperties()` question; 
The fields available are presented below (single row from the Pnadas DF):
```
>>> df = bf.q.nodeProperties().answer().frame()
>>> df.iloc[0]
Node                                                                        h1
AS_Path_Access_Lists                                                        []
Authentication_Key_Chains                                                   []
Community_Match_Exprs                                                       []
Community_Set_Exprs                                                         []
Community_Set_Match_Exprs                                                   []
Community_Sets                                                              []
Configuration_Format                                                 CISCO_IOS
DNS_Servers                                                                 []
DNS_Source_Interface                                                      None
Default_Cross_Zone_Action                                               PERMIT
Default_Inbound_Action                                                  PERMIT
Domain_Name                                                               None
Hostname                                                                    h1
IKE_Phase1_Keys                                                             []
IKE_Phase1_Policies                                                         []
IKE_Phase1_Proposals                                                        []
IP6_Access_Lists                                                            []
IP_Access_Lists                                                             []
IPsec_Peer_Configs                                                          []
IPsec_Phase2_Policies                                                       []
IPsec_Phase2_Proposals                                                      []
Interfaces                   ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2', ...
Logging_Servers                                                             []
Logging_Source_Interface                                                  None
NTP_Servers                                                                 []
NTP_Source_Interface                                                      None
PBR_Policies                                                                []
Route6_Filter_Lists                                                         []
Route_Filter_Lists                                                          []
Routing_Policies                                       ['~RESOLUTION_POLICY~']
SNMP_Source_Interface                                                     None
SNMP_Trap_Servers                                                           []
TACACS_Servers                                                              []
TACACS_Source_Interface                                                   None
VRFs                                               ['VRF1', 'VRF2', 'default']
Zones                                                                       []
```
We can for instance check if the ntp server is set correctly by creating a simple python function and running it against the **Pandas Dataframework**:
```
#
# define the list of expecte ntp servers
expected_ntp_servers = ['8.8.8.8','1.1.1.1']
#
# define a function to compare the results from the object
def is_ntp_valid(ntp_servers:list[str])->bool:
    return sorted(expected_ntp_servers) == sorted(set(ntp_servers))

#
# apply the function to the response framework adding a column
df = bf.q.nodeProperties().answer().frame()
#
df['ntp_valid'] = df['NTP_Servers'].apply(is_ntp_valid)
#
# check the results:
df[['Node','ntp_valid']]
  Node  ntp_valid
0   h1      False
1   r1      False
2   r3      False
3   r4      False
4   r2      False
5   r9      False
6   r5      False
7   r6      False
```

### VALIDATING INTERFACES CONFIG
This is accessible via the question: `bf.q.interfaceProperties()` and you can see the fields for each interface here:

```
bf.q.interfaceProperties().answer().frame().iloc[0]
Interface                            h1[Ethernet0/0]
Access_VLAN                                     None
Active                                          True
Admin_Up                                        True
All_Prefixes                      ['192.168.9.1/24']
Allowed_VLANs                                       
Auto_State_VLAN                                 True
Bandwidth                                 10000000.0
Blacklisted                                    False
Channel_Group                                   None
Channel_Group_Members                             []
DHCP_Relay_Addresses                              []
Declared_Names                       ['Ethernet0/0']
Description                                    TO R9
Encapsulation_VLAN                              None
HSRP_Groups                                       []
HSRP_Version                                    None
Inactive_Reason                                     
Incoming_Filter_Name                            None
MLAG_ID                                         None
MTU                                             1500
Native_VLAN                                     None
Outgoing_Filter_Name                            None
PBR_Policy_Name                                 None
Primary_Address                       192.168.9.1/24
Primary_Network                       192.168.9.0/24
Proxy_ARP                                       True
Rip_Enabled                                    False
Rip_Passive                                    False
Spanning_Tree_Portfast                         False
Speed                                     10000000.0
Switchport                                     False
Switchport_Mode                                 NONE
Switchport_Trunk_Encapsulation                 DOT1Q
VRF                                             VRF2
VRRP_Groups                                       []
Zone_Name                                       None
Name: 0, dtype: object
```
AS seen in previous notes you can also filter all the results based on specific values for each column; if you are only interested in specific fields you can filter them  
again using **Pandas** syntax by specifying the name of a column or a set of columns in  [] e.g.
```
 bf.q.interfaceProperties().answer().frame().Primary_Address
0        192.168.9.1/24
1        192.168.7.1/24
2                  None
3                  None
4                  None
5       192.168.12.1/24
6                  None
7                  None
[...]

 df[['Primary_Address','VRF']]
      Primary_Address      VRF
0      192.168.9.1/24     VRF2
1      192.168.7.1/24     VRF1
2                None  default
3                None  default
4                None  default
5     192.168.12.1/24  default
6                None  default
7                None  default
[...]
```
Simlar filters can be applied using question specific inputs
```
# Interface Properties filtered using question parameters.
bf.q.interfaceProperties(properties="MTU", nodes="/R/").answer().frame().query("MTU != 1500")
```

### VALIDATING IP OWNERS
This is used to determine what IPs are assigned to each device/VRFs; The answer is available via the **bf.q.ipOwners()** question and it presents something like this:
```
>>> df = bf.q.ipOwners().answer().frame()
>>> df
   Node      VRF    Interface              IP Mask Active
0    r6  default    Loopback0         6.6.6.6   24   True
1    r6  default  Ethernet0/2    192.168.56.6   24   True
2    r5  default  Ethernet0/0    192.168.35.5   24   True
3    r5  default  Ethernet0/3    192.168.57.5   24   True
4    r4  default  Ethernet0/2  192.168.46.132   25   True
5    r9  default    Loopback0         9.9.9.9   32   True
6    r6  default  Ethernet0/1  192.168.46.134   25   True
7    r2  default  Ethernet0/1  192.168.12.254   24   True
8    r3  default  Ethernet0/2    192.168.35.3   24   True
```
You can also easily specify a property for duplicate IP via extra input `duplicatesOnly=True`
```
>>> bf.q.ipOwners(duplicatesOnly=True).answer().frame()
Empty DataFrame
Columns: [Node, VRF, Interface, IP, Mask, Active]
Index: []

# double check that it's empty
bf.q.ipOwners(duplicatesOnly=True).answer().frame().empty
True

```

Another thing you can easily do is find who owns where a specific IP

```
 bf.q.ipOwners().answer().frame().query(f"IP == '5.5.5.5'")
   Node      VRF  Interface       IP Mask Active
21   r5  default  Loopback0  5.5.5.5   32   True
```


### VALIDATING UNUSED CONFIG
This is used to determine if there are part of the configuration that are not used; The answer is available via the **bf.q.unusedStructures()** question and it presents something like this:
```
>>> bf.q.unusedStructures().answer().frame().iloc[0]
Structure_Type             ipv4 prefix-list
Structure_Name                      block-7                 # <--- this is the actual prefix list name
Source_Lines      configs/R2.cfg:[136, 137]                 # <--- file and line location (it's 2 lines)
Name: 0, dtype: object
 
```

### CONTROL PLANCE VALIDATION: BGP/OSPF AND GENERIC ROUTES

There are different Batfish questions for BGP and OSPF.. You can use Batfish to check configuration but also sessions.

A specific section of the documentation is related to that: https://batfish.readthedocs.io/en/latest/notebooks/routingProtocols.html and  
here you can see some examples

- **BGP peer configuration** is available via : `bf.q.bgpPeerConfiguration()`  
  Example query: 
  ```
  bf.q.bgpPeerConfiguration().answer().frame().query("Local_AS == 65001 & Remote_IP == '5.5.5.5'")
  Node      VRF Local_AS Local_IP Local_Interface Confederation  ... Cluster_ID Peer_Group Import_Policy Export_Policy Send_Community Is_Passive
  0   r2  default    65001  2.2.2.2            None          None  ...       None       None            []            []          False      False
  ```

- **BGP Sessions** can be checked via `bf.q.bgpSessionStatus()` and `bf.q.bgpSessionCompatibility()`;  
  The first question gives a high level summary based on the BGP configuration and reports 3 possible results for the Session: 
    - ESTABLISHED: all good
    - NOT_ESTABLISHED: something blocking the connection **at the network level** (e.g. possibly an ACL in a device between the peers)
    - NOT_COMPATIBLE: the configuration of the 2 peers is not compatible

  The second question gives a greater level of details about the problem, below for instance you can see that we have a problem between **R4 **and** R6** and it seems  
  that **R4** is configured to peer with R4 but not viceversa (you can see that also because R4 has a configured peer to **R9** but nothing to **R6**):
  ```
  >>> bf.q.bgpSessionStatus().answer().frame()
  Node      VRF Local_AS Local_Interface      Local_IP  ... Remote_Interface     Remote_IP  Address_Families    Session_Type Established_Status
  0   r2  default    65001            None       2.2.2.2  ...             None       5.5.5.5  ['IPV4_UNICAST']            IBGP        ESTABLISHED
  1   r4  default    65001            None  192.168.49.4  ...             None  192.168.49.9  ['IPV4_UNICAST']  EBGP_SINGLEHOP        ESTABLISHED
  2   r5  default    65001            None       5.5.5.5  ...             None       2.2.2.2  ['IPV4_UNICAST']            IBGP        ESTABLISHED
  3   r6  default    65001            None       6.6.6.6  ...             None       4.4.4.4                []            IBGP     NOT_COMPATIBLE
  4   r9  default    65009            None  192.168.49.9  ...             None  192.168.49.4  ['IPV4_UNICAST']  EBGP_SINGLEHOP        ESTABLISHED

  >>> bf.q.bgpSessionCompatibility().answer().frame().query("Node == 'r6'")
  Node      VRF Local_AS Local_Interface Local_IP Remote_AS Remote_Node Remote_Interface Remote_IP Address_Families Session_Type Configured_Status
  3   r6  default    65001            None  6.6.6.6     65001        None             None   4.4.4.4               []         IBGP         HALF_OPEN
  ```

 - BGP RIB is available under the question: `bf.q.bgpRib()` which returns the following:
   ```
   >>> bf.q.bgpRib().answer().frame().head()
   Node      VRF     Network    Status           Next_Hop     Next_Hop_IP  ... Received_From_IP Received_Path_Id Cluster_List Tunnel_Encapsulation_Attribute Weight   Tag
   0   r4  default  2.2.2.2/32  ['BEST']    ip 192.168.24.2    192.168.24.2  ...          0.0.0.0             None         None                              None  32768  None
   1   r4  default  3.3.3.3/32  ['BEST']    ip 192.168.34.3    192.168.34.3  ...          0.0.0.0             None         None                              None  32768  None
   2   r4  default  5.5.5.5/32  ['BEST']  ip 192.168.46.134  192.168.46.134  ...          0.0.0.0             None         None                              None  32768  None
   3   r4  default  6.6.6.0/24  ['BEST']  ip 192.168.46.134  192.168.46.134  ...          0.0.0.0             None         None                              None  32768  None
   4   r4  default  9.9.9.9/32  ['BEST']    ip 192.168.49.9    192.168.49.9  ...     192.168.49.9             None         None                           None      0  None
   ```

Finally note that you can manually add:
- border interfaces toward devices that are not managed (so you don't have the configuration)
- BGP connections/peers with External Peers (of which you don't have the configuration)

You can do that by adding a gile called **isp_config.json** under the **batfish** folder in the snapshot, see documentation:

https://pybatfish.readthedocs.io/en/latest/formats.html#modeling-isps

And note that you can also add specific external BGP announcements in a similar way with a file called: **external_bgp_announcements.json**
placed inside the top-level snapshot folder (see https://pybatfish.readthedocs.io/en/latest/formats.html#external-bgp-announcements )


---


- OSPF interface configuration is available via : `bf.q.ospfInterfaceConfiguration()` 

- OSPF Session Compatibility, i.e. if the configuration allows for OSPF to establish neighbourships, is available via: `bf.q.ospfSessionCompatibility()`  
  If there is a mismatch, you can see them there. If all the sessions should establish correctly you should get an empty framework:
  ```
  >>> bf.q.ospfSessionCompatibility(statuses="!ESTABLISHED").answer().frame().empty
  True
  ```
  Note that this Batfish is able to detect issues that depends on parameters not related to the interface.. for instance, if we change the **router-id** in **R6** to be the same as in **R5**, we get:
  ```
   >>> bf.q.ospfSessionCompatibility(statuses="!ESTABLISHED").answer().frame()
         Interface      VRF            IP Area Remote_Interface Remote_VRF     Remote_IP Remote_Area       Session_Status
   0  r5[Ethernet0/2]  default  192.168.56.5    0  r6[Ethernet0/2]    default  192.168.56.6           0  DUPLICATE_ROUTER_ID
   1  r6[Ethernet0/2]  default  192.168.56.6    0  r5[Ethernet0/2]    default  192.168.56.5           0  DUPLICATE_ROUTER_ID

  # This is identified both if we manually set the router-id and if we have it selected via the highest loopback   
  # The online documentation will give the exact details about the what it checked
  ```

---

The records available in the Batfish questions/answers are presented below:
```
================================ 
   BGP ANSWER DETAILS
================================ 
>>> bf.q.bgpPeerConfiguration().answer().frame().iloc[0]
Node                           r2
VRF                       default
Local_AS                    65001
Local_IP                  2.2.2.2
Local_Interface              None
Confederation                None
Remote_AS                   65001
Remote_IP                 5.5.5.5
Description                  None
Route_Reflector_Client      False
Cluster_ID                   None
Peer_Group                   None
Import_Policy                  []
Export_Policy                  []
Send_Community              False
Is_Passive                  False
Name: 0, dtype: object

>>> bf.q.bgpSessionStatus().answer().frame().iloc[0]
Node                                r2
VRF                            default
Local_AS                         65001
Local_Interface                   None
Local_IP                       2.2.2.2
Remote_AS                        65001
Remote_Node                         r5
Remote_Interface                  None
Remote_IP                      5.5.5.5
Address_Families      ['IPV4_UNICAST']
Session_Type                      IBGP
Established_Status         ESTABLISHED
Name: 0, dtype: object


>>> bf.q.bgpSessionCompatibility().answer().frame().iloc[0]
Node                               r2
VRF                           default
Local_AS                        65001
Local_Interface                  None
Local_IP                      2.2.2.2
Remote_AS                       65001
Remote_Node                        r5
Remote_Interface                 None
Remote_IP                     5.5.5.5
Address_Families     ['IPV4_UNICAST']
Session_Type                     IBGP
Configured_Status        UNIQUE_MATCH
Name: 0, dtype: object


>>> bf.q.bgpRib().answer().frame().iloc[0]
Node                                           r4
VRF                                       default
Network                                2.2.2.2/32
Status                                   ['BEST']
Next_Hop                          ip 192.168.24.2
Next_Hop_IP                          192.168.24.2
Next_Hop_Interface                        dynamic
Protocol                                      bgp
AS_Path                                          
Metric                                         11
Local_Pref                                    100
Communities                                    []
Origin_Protocol                              ospf
Origin_Type                            incomplete
Originator_Id                             4.4.4.4
Received_From_IP                          0.0.0.0
Received_Path_Id                             None
Cluster_List                                 None
Tunnel_Encapsulation_Attribute               None
Weight                                      32768
Tag                                          None
Name: 0, dtype: object

================================ 
   OSPF ANSWER DETAILS
================================ 

>>> bf.q.ospfInterfaceConfiguration().answer().frame().iloc[0]
Interface              r6[Ethernet0/1]
VRF                            default
Process_ID                           1
OSPF_Area_Name                       0
OSPF_Enabled                      True
OSPF_Passive                     False
OSPF_Cost                           10
OSPF_Network_Type       POINT_TO_POINT
OSPF_Hello_Interval                 10
OSPF_Dead_Interval                  40
Name: 0, dtype: object


>>> bf.q.ospfSessionCompatibility().answer().frame().iloc[0]
Interface           r2[Ethernet0/2]
VRF                         default
IP                     192.168.24.2
Area                              0
Remote_Interface    r4[Ethernet1/0]
Remote_VRF                  default
Remote_IP              192.168.24.4
Remote_Area                       0
Session_Status          ESTABLISHED
Name: 0, dtype: object
```

Route analysis is also possible as part of the control plane validation.. this is available via the question: `bf.q.routes()`
and it will also take into account the routes that are exchanged via the routing protocols. 

Documentation details about route analysis is available here: https://batfish.readthedocs.io/en/latest/notebooks/routingTables.html

In our example snapshot configuration we have many routes exchanged and you can filter for instance for protocol (default is all)):
```
# Note the filter applied includes:
#  - static/bgp/ospf type of routes
#  - prefix needs to match a default
# The exact types of filters is available in the documentation link
#

>>> bf.q.routes(protocols="bgp,static,ospf", network="0.0.0.0/0").answer().frame()

  Node      VRF    Network                                 Next_Hop     Next_Hop_IP Next_Hop_Interface Protocol Metric Admin_Distance   Tag
0   h1     VRF1  0.0.0.0/0                         ip 192.168.7.254   192.168.7.254            dynamic   static      0              1  None
1   h1     VRF2  0.0.0.0/0                         ip 192.168.9.254   192.168.9.254            dynamic   static      0              1  None
2   r1  default  0.0.0.0/0                        ip 192.168.12.254  192.168.12.254            dynamic   static      0              1  None
3   r2  default  0.0.0.0/0    interface Ethernet0/2 ip 192.168.24.4    192.168.24.4        Ethernet0/2   ospfE2      1            110  None
4   r3  default  0.0.0.0/0    interface Ethernet0/0 ip 192.168.34.4    192.168.34.4        Ethernet0/0   ospfE2      1            110  None
5   r5  default  0.0.0.0/0    interface Ethernet0/0 ip 192.168.35.3    192.168.35.3        Ethernet0/0   ospfE2      1            110  None
6   r5  default  0.0.0.0/0    interface Ethernet0/2 ip 192.168.56.6    192.168.56.6        Ethernet0/2   ospfE2      1            110  None
7   r6  default  0.0.0.0/0    interface Ethernet0/0 ip 192.168.46.4    192.168.46.4        Ethernet0/0   ospfE2      1            110  None
8   r6  default  0.0.0.0/0  interface Ethernet0/1 ip 192.168.46.132  192.168.46.132        Ethernet0/1   ospfE2      1            110  None
```
Here you can somewhat easily see that allthe routers point to R4 for the default and that it's generated/propagated via OSPF.

---

You can also use the same question to check the **LONGEST_PREFIX_MATCH** for a specific **subnet/network**: this will basically get the route that is used
to forward the a packet for the specific destination.

E.G. we want to find what route is followed if we send a packet to the **mock up destination: 18.18.18.18** we will see that we match the default route
```
>>> bf.q.routes(protocols="bgp,static,ospf", network="18.18.18.18/32",prefixMatchType="LONGEST_PREFIX_MATCH").answer().frame()
  Node      VRF    Network                                 Next_Hop     Next_Hop_IP Next_Hop_Interface Protocol Metric Admin_Distance   Tag
0   h1     VRF1  0.0.0.0/0                         ip 192.168.7.254   192.168.7.254            dynamic   static      0              1  None
1   h1     VRF2  0.0.0.0/0                         ip 192.168.9.254   192.168.9.254            dynamic   static      0              1  None
2   r1  default  0.0.0.0/0                        ip 192.168.12.254  192.168.12.254            dynamic   static      0              1  None
3   r2  default  0.0.0.0/0    interface Ethernet0/2 ip 192.168.24.4    192.168.24.4        Ethernet0/2   ospfE2      1            110  None
4   r3  default  0.0.0.0/0    interface Ethernet0/0 ip 192.168.34.4    192.168.34.4        Ethernet0/0   ospfE2      1            110  None
5   r5  default  0.0.0.0/0    interface Ethernet0/0 ip 192.168.35.3    192.168.35.3        Ethernet0/0   ospfE2      1            110  None
6   r5  default  0.0.0.0/0    interface Ethernet0/2 ip 192.168.56.6    192.168.56.6        Ethernet0/2   ospfE2      1            110  None
7   r6  default  0.0.0.0/0    interface Ethernet0/0 ip 192.168.46.4    192.168.46.4        Ethernet0/0   ospfE2      1            110  None
8   r6  default  0.0.0.0/0  interface Ethernet0/1 ip 192.168.46.132  192.168.46.132        Ethernet0/1   ospfE2      1            110  None
```