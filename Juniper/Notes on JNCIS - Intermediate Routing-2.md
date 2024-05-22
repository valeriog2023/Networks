# Junos Intermediate Routing - 2

## Introduction to Routing Instances
Routing instances are similar to Cisco VRFs.
A different instance of a routing table is created per routing instance and can be used to allow overlapping IP ranges and to keep traffic separated.  

In order to create a routing instance you need to:

- Create an instance of type **virtual-router** and give it a name, e.g. **Customer1**, **Customer2**
  ```
  [edit]
  set routing-instances Customer1 instance-type virtual-router 
  set routing-instances Customer2 instance-type virtual-router 
  ```
- Allocate interfaces to the routing instance, e.g. ge-0/0/0.0 and ge-0/0/1.0:
  ```
  set routing-instances Customer1 interface ge-0/0/0.0
  set routing-instances Customer2 interface ge-0/0/1.0
  ``` 

- we give the interfaces the same IPs andwe can cehck the routing instance in the routing table:
  ```
  R1# run show route 
  inet.0: 3 destinations, 3 routes (3 active, 0 holddown, 0 hidden)
  
  [...]
  Customer1.inet.0: 1 destinations, 1 routes (1 active, 0 holddown, 0 hidden)
  + = Active Route, - = Last Active, * = Both

  10.34.0.1/32       *[Local/0] 00:00:03
                       Reject            <-- int is physically down
  [...]
  Customer2.inet.0: 1 destinations, 1 routes (1 active, 0 holddown, 0 hidden)
  + = Active Route, - = Last Active, * = Both
  
  10.34.0.1/32       *[Local/0] 00:00:03
                       Reject            <-- int is physically down

  ```
- you can also:
  - use the command: `show run instance Customer1`  to check the specific routing instance
  - use the command: `ping <ip> routing-instance Customer1` to run a ping from related rot=uting instance

There are different types of routing-instances.. a non exhaustive list of what you can find is:
- **forwarding**: for filter based forwarding and common access Layer Application
- **l2vpn**: for **L2VPN**
- **no-forwarding**: used to separate large networks into smaller administrative domains
- **virtual-router**: Used for non-VPN related applications
- **vpls**: Used for point-to-multipoint LAN implementation between a set of sites in a VPN
- **vrf**: Used in L3 VPNs
- **virtual switch**: virtual switch routing instance

## RIB Groups
RIB groups are a way to transfer routes from one routing instance/protocol to a set of other routing instances.  
Note that you have both `import-rib` and `export-rib` policies available and you can apply a specific `import-policy` defined under `policy-options policy-statement`.   
Once the rib group has been setup and the policy applied you need to associate in the source
routing instance the routes you want to share the the specific **rib-group**

```  
[edit]
set routing-instances Customer1 instance-type virtual-router 
set routing-instances Customer2 instance-type virtual-router 
! In this case 
! The first routing instance is the source
! Any follow up routing instance is where the routes are going to be imported
!
edit routing-options 
[edit routing-options]
set rib-groups TEST_OSPF import-rib [ inet.0 Customer1.inet.0 Customer2.inet.0 ]
exit
!
! now you need to associate the routes to the specific rib group
! This needs to be done in whatever protocol the route is generated (e.g. static, ospf, etc..)
! 
edit protocols ospf 
[edit protocols ospf]
set rib-group TEST_OSPF
``` 
