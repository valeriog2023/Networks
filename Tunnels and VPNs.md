# Short Recap of VPN with Crypto Maps
Requirements:
* reachability between tunnel endpoints
* phase1 and phase2 paramters matching
* nat-traversal is now automatically detected but you may need to keep it active with: ```crypto isamkp nat keepalive```
  

Example config:
```

crypto isakmp policy 10
  encr aes 256
  hash sha512
  authentication pre-share
  group 24
!
  crypto isakmp key <KEY> address <PEER_IP>
!
crypto ipsec transform-set <SET_NAME> esp-aes 192 esp-sha384-hmac
  mode tunnel
!
ip access-list extended <CRYPTO_ACL_NAME>
    permit ip <SRC> <WILDCARD> <DEST> <WILDCARD>

!
crypto map <MAP_NAME> local-address <LOCAL_IP>
!
crypto map <MAP_NAME> 10 ipsec-isakmp
    set peer <PEER_IP>
    set transform-set <SET_NAME>
    match address <CRYPTO_ACL_NAME>
!
! apply the crypto map to the interface
! toward the <PEER_IP> (possibly to more 
! than on interface if routing can change) 
interface <X>
  crypto map <MAP_NAME>

! Need a route to forward traffic out of interface <X>
ip route <DEST> <MASK> <NEXT_HOP>

! show commands
show crypto isa sa
show crypto ipsec sa
```

# GRE over IPSEC with CRYPTO MAPs

GRE is IP Protocol 47
Notes:
* GRE is IP protocol 47
* The IP MTU is set on the tunnel to offload fragmentation to the end host.   
 * Don't Fragment (DF) bit is not copied by default from the original IP header to the inner GRE payload and further to the outer ESP header, so  
 hosts running Path MTU Discovery (PMTUD) over a GRE over IPsec tunnel will think that the end-to-end path MTU is larger than it is (because the packet is fragmented even if they did set the bit to 1)  
 By lowering the IP MTU to account for both ESP and GRE, the router will now generate ICMP Unreachable at a lower value when fragmentation is needed, as seen below.
*  that ```tcp adjust-mss``` is also required to be set to 40 bytes less than the mtu in the tunnel
The effect is to edit payload of a TCP three-way handshake if the MSS exceeds the configured value.  
The max MSS should be the *IP MTU minus 40 bytes (20 bytes for the IP header, 20 bytes for the TCP header)*. 
* you can also try to enale the replication of the **DF** bit in the tunnel with the command: ```tunnel path-mtu-discovery```

Configuration example:
```

interface Tunnel0
  ip address 192.168.0.1 255.255.255.0
  ip mtu 1400
  ip tcp adjust-mss 1360
  ! you can enable routing over the encrypted tunnel
  ip ospf 1 area 0
  tunnel source Loopback0
  tunnel destination <PEER_IP>
!
crypto isakmp policy 10
  encr 3des
  hash md5
  authentication pre-share
  group 5
!
crypto isakmp key <KEY> address <PEER_IP>
!
crypto ipsec transform-set <CRYPTO_SET_NAME> esp-aes esp-sha-hmac
  mode transport
!
ip access-list extended GRE_TUNNEL
  permit gre host <LO0_IP> host <PEER_IP>
!
crypto map GRE_OVER_IPSEC local-address Loopback0
!
crypto map GRE_OVER_IPSEC 10 ipsec-isakmp
  set peer <PEER_IP>
  set transform-set <CRYPTO_SET_NAME>
  match address GRE_TUNNEL
!
interface <X>
  description Outgoing interface for PEER_IP
  crypto map GRE_OVER_IPSEC

```

# GRE over IPSEC with CRYPTO PROFILES

This is very similar to the use of crypto map but it just a pplies a profile to the tunnel

Configuration example:
```

crypto isakmp policy 10
  encr 3des
  hash md5
  authentication pre-share
  group 5
!
crypto isakmp key <KEY> address <PEER_IP>
!
crypto ipsec transform-set <SET_NAME> esp-aes esp-sha-hmac
  mode transport
!
crypto ipsec profile <PROFILE_NAME>
  set transform-set ESP-AES-128-SHA-1
!
!
interface Tunnel0
  ip address 192.168.0.1 255.255.255.0
  ip mtu 1400
  ip tcp adjust-mss 1360
  ! enable routing protocol if required
  ip ospf 1 area 0
  tunnel source Loopback0
  tunnel destination 150.1.8.8
  tunnel protection ipsec profile <PROFILE_NAME>

```

# IPSEC Virtual Tunnel Interfaces (VTIs)
IPsec Virtual Tunnel Interface (VTI) is a tunnel where the payload is directly encapsulated in ESP.
It is similar to GRE but:
*  overhead is 24 bytes lower
   * Remember GRE requires extra 20 (outer IP Header) + 4 (Actual GRE Header) 
* other non-IP payloads are not supported. (e.g. IS-IS)
* the IPsec Transform Set must use Tunnel Mode, because there is no other transport header

The configuration of a VTI is identical to a GRE over IPsec tunnel with a Crypto IPsec Profile, except that the **tunnel mode is set to IPsec IPv4 or IPsec IPv6**.  
* traffic must be routed inside the tunnel (you can use dynamic routing)
* Peer tunnel termination should be reachable not via the same protocol used in the tunnel

Configuration example:
```
crypto isakmp policy 10
  encr aes 192
  hash sha384
  authentication pre-share
  group 15
!
crypto isakmp key <KEY> address <PEER_IP>
!
crypto ipsec transform-set <CRYPTO_SET> esp-3des esp-md5-hmac
  mode tunnel
!
crypto ipsec profile VTI_PROFILE
 set transform-set <CRYPTO_SET>
!
!
interface Tunnel0
 ip address 192.168.0.1 255.255.255.0
 ip tcp adjust-mss 1406
 ip ospf 1 area 0
 tunnel source Loopback0
 tunnel destination <PEER_IP>
 tunnel mode ipsec ipv4
 tunnel protection ipsec profile VTI_PROFILE
```

Note that this tunnel can account for a correct **mtu**; you can see that using ```show interface tunnel0``` that should show **MTU 1446** (for IPSEC in tunnel mode with 54 overhead).  
Still a good idea however to set use the ```adjust-mss 1406``` with 1406 being the valueyou get by further removing the encapsulated IP + TCP header


# DMVPN

Dynamic Multipoint VPN (DMVPN) is a multipoint GRE-based tunneling technology.  
You have one or more hubs configured as **Next-Hop Resolution Protocol (NHRP) Servers**  that create mappings between:
* The public IP address used for the tunnel source (**NBMA address**),
* The private IP address used inside of the tunnel.  

Major points:
* NHRP mapping is similar to ATM and Frame-Relays Inverse ARP.  
* Tunnels are created on-demand based on the particular destination of traffic.  
* Hub and spokes must agree on certain parameters, such as:
  *  NHRP authentication
  *  GRE tunnel key number
  *  Multicast support  
     Note that multicast works in way similar to frame-relay so, from an IGP routing point of view, 
     the spokes only learn routes from the hub as they don't see the ther spokes directly.  
* The spokes have a manual/static mapping between hub’s tunnel address and NBMA address
* The hub dynamically learns about the spokes through NHRP messages. 


The first step to verify a DMVPN setup is to check that the spokes have registered with the hub correctly.

## DMVPN with no Encryption
This is the basic setup (no encryption used) for a **DMVPN phase1** setup where there is no spoke-to-spoke dynamic tunnel created

```
[HUB]
interface Tunnel0
 ip address 192.168.0.254 255.255.255.0
 ip nhrp authentication <KEY>
 ip nhrp map multicast dynamic
 ip nhrp network-id 1
 tunnel source <INTF_Y>
 tunnel mode gre multipoint
 tunnel key 2
 no shutdown



[SPOKE]
interface Tunnel0
 ip address 192.168.0.2 255.255.255.0
 ip nhrp authentication <KEY>
 ip nhrp map 192.168.0.254 <HUB_PUBLIC_IP>
 ip nhrp map multicast <HUB_PUBLIC_IP>
 ip nhrp network-id 1
 ip nhrp nhs 192.168.0.254
 tunnel source <INTF_X>
 tunnel mode gre multipoint
 tunnel key 2
 no shutdown
!
! point some prefixes to the tunnel
! or use dynamic routing
ip route <PREFIX> <MASK> 192.168.0.254


! some useful show commands
show dmpvn
```


## DMVPN adding Encryption

------------
------------
# Some MTU considerations

**GRE** can incapsulate multi protocol, not only IP but it requires
* 4 extra bytes for the GRE Header (point-point) or 8 extra bytes if the tunnel is point-to-multipoint 
* 20 Bytes for the Outer IP
If you only tunnel IP you can use ```tunnel mode ipip``` which only adds 20 bytes

**IPSEC** contains
* ESP constant: SPI(4) + SN(4) + PADLength(1) + NextHeader(1) = 10
* ESP-AuthData: always truncated to 12 Bytes
* AES-CBC (RFC 3602): IV(16) + MaxPadding(15)
* ESP in tunnel mode adds 20 Bytes for a tunnel IP Header. (Transport mode doesn't).

So overall MAXIMUM ESP(AES) overhead = 10 + 12 + 31 = 53. Obviously the padding cannot be odd, so use 54 as the MAXIMUM overhead.
The adjust-mss size should consider additional 20 bytes for TCP Header



