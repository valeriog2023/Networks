Notes form: https://arista.my.site.com/AristaCommunity/s/article/how-to-set-up-metamux-for-a-typical-exchange
Also check diagram: exchange_setup_diagram.png

The Goal is to configure a L1 switch to
 - connect to an exchange L3 switch on port et1
 - conenct to a internal L3 switch on port et2
 - establish a bgp connection between L3 switch and exchange
 - connect servers on port et3,et4,.. and
    - L1 forward traffic from the exchange L3 switch to the servers
    - L1 forward traffic from the servers to the exchange L3 switch 
      

# Incoming traffic (from the exchange)

For incoming traffic you can just configure your L3 switch and server switche interfaces
with the commands:
```
interface et<X>
  source et1
```
Note that:  

* the Exchnage switch will behave as if it is connected on a point-to-point link
  so the destination mac address will be the one of the internal L3 switch interface.
  All servers will have to be configured with the same mac address so that they will 
  accept this traffic, e.g. on a linux box:
  ```
  sudo ifconfig p4p2 down hw ether <same_mac>>
  sudo ifconfig p4p2 up
  ```

* You might have to disable features like ICMP Host Unkown/Unreachable on the internal
  L3 switch interface because the switch might not be able to reach the Ip of the servers
  (they will reach the traffic directly anyway)



# Outgoing traffic (to the exchange)

The interface toward the L3 exchange router needs to be configured to source traffic 
from a MUX application. Mux application have fixed ports to be used as output depending 
on their setup; below we assume ap8 is the out interface of the mux app. The other MUX 
interfaces will get the input from the internal L3 switch and the other server ports

```
int et1
  source ap8

int ap5
  source et1  ! -> from the internal L3 switch
int ap6
  source et4  ! -> from a server
int ap7
  source et5  ! -> from a server
...  
```

Note that:  

*  the server will need to be configured with static routes pointing to a gateway 
   in their own subnet. However, they will also need some static arp allocation so 
   that the mac address of the Exchange L3 switch is mapped to their gateway
   E.g. assuming a server is configured as 10.0.0.<X>/24 and gateway is 10.0.0.254

   ```
   # set the mac address of the Exchange L3 switch as the first hop mac
   /usr/sbin/arp -s 10.0.0.254 <£xchange L3 mac>
   
   # add routes
   route add -host <remote_host> gw 10.0.0.254 dev <intf>
   route add -net <subnet/mask> gw 000.000.000.000 dev <intf>
   or 
   ip route add <subnet/mask> via 000.000.000.000 [ dev <intf> ]
   ```
   Note: commans are actually different in the blog post the static mac address is configured
   for 000.000.000.000 IP and the route is configured using dev <interface> instead of the gateway
   so.. to be tested..


# Useful show commands

*  show l1 source/destination/path
   shows source destination and both information for a port or all ports

*  show l1 matrix / show l1 matrix all
   it will show how ports are connected in a schematic form


# A diagram
<img src="pictures/exchange_setup_diagram.png" alt="Exchange diagram setup" style="height: 600px; width:1000px;"/>