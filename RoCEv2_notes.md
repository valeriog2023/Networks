# RoCEv2

**RoCE** stands for **RDMA over Converged Ethernet** where RDMA, **Remote Directory Memory Access** is a tecnique that allows hosts in a network to directly access other hosts's memory without involving the operating system or CPU, i.e. bypassing the kernel (and the network stack).

**RDMA** was originally created for **inifiniband** switches for High performance clusters **(HPC)** and brought to traditional switches with **RoCEv1** however that only supporterd Ethernet so was limited to a L2 domain.  
**RoCEv2** added **UDP** encapsulation to support L3 and it's therefore much more flexibile.
Note that inifiniband also takes care of congestion management while in an Ethernet Deployment this is done via:
* explicit congestion notification (ECN) and
* priority flow control (PFC) congestion avoidance algorithms.


<img src="pictures/RoCE vs RoCEv2 packet.png" alt="RoCE Packets" style="height: 200px; width:1000px;"/>

Deep learning systems are optimized to handle large amounts of data to process and re-evaluate results. 

Inference systems may use smaller data sets but be hyper-scaled to many devices.

When communication between the server clusters involved in learning cycles has high latency, or packet drops, the learning job can take much longer to complete, or in some cases fail, so these applications require: **low latency, lossless networks**. 

## Explicit Congestion Notification (ECN)
**ECN** can be used for end-to-end congestion management;  
The process is end-to-end and built in the data path: 

* a router on the path marks a packet with the **ECN** flag when it starts to experience congestion: 
   * the 2 least significant bits of the type of service **(TOS)** field in the IP Header are set to **0x11**. 
* The receiver gets the packet with the ECN congestion experience bits set and it generates and sends a **congestion notification packet (CNP)** back to the sender. 
* The sender receives the congestion notification, it slows down the flow that matches the notification. 

### ECN with WRED implemenation

**WRED** can be used to set thresholds that indicate congestion and to mark traffic with ECN bits.

WRED can set two thresholds: ```min``` **(Orange)** and ```max``` **(Red)** . On Cisco Nexus 9000 this is done on a per-queue level.  
The **minimum** threshold indicates minor congestion; based on the **drop probability** in the WRDE configuration, a certain amount of packets is marked with **ECN** while leaving the queue.

If buffer utilization in the queue reaches the WRED **maximum** threshold every packet leaving the queue is marked with **ECN** 

```
[NXOS CONFIG EXAMPLE]
! Note: I actually did not manage to test this.. so use just as "possibly" working
!
feature ecn
!
mls qos congestion-control ecn statistics
mls qos congestion-control ecn threshold <threshold>
mls qos congestion-control wred
mls qos congestion-control wred average-queue-length <threshold>
!
interface ethernet <interface-number>
  ecn enable
  wred enable
  wred avg-qlen <threshold>
  wred min-thresh <threshold>
  wred max-thresh <threshold>


```


## Priority Flow Control (PFC)
Priority Flow Control was introduced in Layer 2 networks as the primary mechanism to enable lossless Ethernet.  
Flow control is driven by the class of service **(COS)** value in the **Layer 2 frame**.  
Congestion is signaled with **pause frames**, and a pause mechanism.  

As RoCEv2 can be routed, **PFC** was changed to work with **DSCP codepoints** priorities to signal congestion in a L3 routed domain. 

DSCP is a used to classify network traffic and because it uses the 6-bit differentiated services field in the IP header.   
PFC frames use the L2 802.1p Priority Code Point (PCP) so a mapping between
DSCP and PFC is required and when a switch receives a packet with a DSCP value, it:
 * Looks up the mapping DSCP<->PCP .
 * Sets the PCP value in the VLAN tag of the Ethernet frame.
 * Applies PFC based on the PCP value, pausing transmission if necessary.

PFC is transmitted per-hop, from the place of congestion to the source of the traffic, e.g.
*  LEAF1 starts experiencing congention toward a host, so sends a PAUSE frame to the SPINE
*  The SPINE receives tha PAUSE and starts buffering traffic instead of sending it to the LEAF
   *  When the buffer in the SPINE reaches a threshold, a new PAUSE frame is sent toward the source.  
   We assume this is LEAF2 connected with the source
*  LEAF2 receives the PAUSE frame and starts buffering
   * again when a threshold is reached, a new PAUSE frame is sent to the actual SRC 
* when the SRC slows down and the buffers clear up, PAUSE frames are no longer sent and traffic can resume.

This step-by-step behavior could take time to be propagated to the source and also a PFC storm can occur (rare event though) when a misbehaving host continuously transmits PFC frames. This behavior can saturate the buffers on all the network nodes.  
The PFC watchdog feature checks whether packets in a no-drop queue are drained within a specified time period.  
If the time period is exceeded, all outgoing packets are dropped on interfaces that match the PFC queue that is not being drained to prevent a PFC deadlock in the network.

PFC is used as the primary tool to manage congestion for RoCEv2 transport. 

When PFC is enabled on the Cisco Nexus 9000 switch, a class of service is dedicated to lossless transport. Traffic in this class is treated differently than traffic in other classes. Any port on the Cisco Nexus 9000 switch configured with PFC is allocated a dedicated no-drop queue and dedicated buffer for that queue.
The queue has two thresholds:
*  xOFF threshold is set higher in the buffer. When reached a PFC frame is generated and sent toward the source of the traffic. 
* xON threshold, this is where pause frames are halted and no longer sent toward the senders. 

```
[NXOS CONFIG EXAMPLE]
! Note: I actually did not manage to test this.. so use just as "possibly" working
!
feature pfc
!
mls qos map cos-dscp <CoS> <DSCP value>
mls qos srr-queue input threshold <threshold> cos <CoS>
!
interface ethernet <interface-number>
 pfc enable
!
```

## DCQCN: Data Center Quantized Congestion Notification 
Working together, ECN can react first to mitigate congestion. and if buffer utilization continues to build up, PFC behaves as a fail-safe and prevents traffic drops. 
This collaborative process between PFC and ECN where they managed congestion together is called **DCQCN** and is developed for RoCE networks.  
Working together, PFC and ECN provide efficient end-to-end congestion management. When the system is experiencing minor congestion where buffer usage is moderate, WRED with ECN manages the congestion seamlessly. In cases where congestion is more severe or caused by microbursts producing high usage of buffers, PFC is triggered, and that congestion is managed. 

## Approximate Fair Drop (AFD)
AFD can distinguish high bandwidth **(elephant flows)** from short-lived and low bandwidth flows **(mice flows)**.   
After AFD has information about which traffic makes up the elephant flows, AFD can mark ECN bits with 0x11 values, *but only for high bandwidth flows*.  
The number of packets marked with ECN is based on the bandwidth used by the flow and the interface bandwidth.

Performance is optimized for the lowest latency and **AFD** has the advantage (over **WRED**) to distinguish which set of flows are causing the most congestion. 

In an AI cluster, it is advantageous to let short-lived communications run to completion by not allowing a long transfer of data and any resulting congestion to slow them down. Packet drops are still avoided, but many transactions get completed faster because the system can tell the elephant flows apart and only slows them down.
