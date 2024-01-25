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