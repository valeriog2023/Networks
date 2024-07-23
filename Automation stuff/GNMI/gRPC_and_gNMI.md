# gNMI Notes

**GNMI** is a protocol for network management on top of **gRPC**; as it uses GRPC is very efficient (via protcol buffers uses binary data)

- data model is YANG
- Capable of both configuration and telemetry
- it can stream data from devices in real time
- it is vendor agnostic
- it is supported by multiple languages (python/golang)

It provides unificiation of SNMP/CLI/SSH

### Protocol Buffers (Protobuffs)

This is a binary serialization protocol developed by Google and implemented by **gRPC**; It actually allows the payload to be transmitted as JSON, BYTES(binary) or PROTO (prototext similar to JSON).  
It is **strongly typed** and language agnostic (i.e. suported by multiple languages). By default it uses **TLS** with credentials or certificates and **TCP/6030 port** (used for Arista gNMI).  
The payload is optimized, e.g. you could squeeze a milion route routing table into a small payload.  
The file format used to define the message structure is usuall **.proto**


### gNMI Operations:
 - **Capabilities**: gNMI allows to exchange capabilities to see what each client supports in terms of operations, versions, encoding, etc..
 - **Get**: fetch a snapshot of data from the target for some **path**
 - **Set**: UPdate, Replace or Delete some configuration on the target device on a specific **path**
 - **Subscribe**: used for telemetry, it has multiple modes:
    - Once:  a one-time snapshot, similar to Get
    - Poll: repeatedly poll based on client requests
    - Streaming: 
       - Sample: Stream data at regular intervals
       - On change: stream data only when there's a change in the state


## XPATH
XML Path Language, in the context of gNMI, is used to identify node locations within an xml document; You will use it to navigate a data model usally written in **YANG**, and   
based on the model, create a query that you can send to the device, e.g.
```
! gives the description of Ethernet3
/interfaces/interface[name=Ethernet3]/config/description
!
! these 2 will give all the interfaces descriptions
/interfaces/interface[name=*]/config/description
/interfaces/interface/config/description

!
/network-instances/network-instance[name=default]/protocols/protocol[name=BGP]
```
You have a **tree** structure so if you stop before a terminal **LEAF** you will get everything under.  
Note also that you can use wildcards like **\***  inside a query filter (filters are based on the sqaure brackets) however what you can do might depend
on the secific YANG model.. so you need to know how to browse a **yang** model

### YANG
Yang is a data modelling language for netowkr automation which defines a schema used to represent configuration, state data, RPC and notifications.  
There are **open** YANG MODELs (**Openconfig/IETF**) but even if a vendor says it supports it, it does not mean it implements all of it and different vendors  
can actually implemen different things (with related issues).  
Native Models are proprietary models provided by a vendor and can be very big, definitely too big to be translated to **xpath** statements without tools.  
Some tools to browse YANG Models:
 -  Cisco YANG Explorer: downloadable as a docker container (but only for Cisco)
 -  JunOS Yang Data Model Explorer
 -  Pyang: creates a tree from a YANG model (python), more terminal based
 -  GNMIC: vendor agnostic: you might want to try to use this one..


### PYANG Example
```
! install pyang
pip3 install pyang

! clone openconfig repo
git clone https://github.com/openconfig/public.git

! make a folder for the yang models and copy them from the openconfig repo, there
mkdir yang_modules
cp -R public/release/models/*.yang yang_modules/
cp -R public/release/models/*/*.yang yang_modules/
cp -R public/third_party/ietf/*.yang  yang_modules/

! use pyang to see the tree structure
! As you can see it tells you if the entry is read-only(ro) or read-write(rw) and the type expected
s$ pyang openconfig-interfaces.yang -f tree
module: openconfig-interfaces
  +--rw interfaces
     +--rw interface* [name]
        +--rw name                  -> ../config/name
        +--rw config
        |  +--rw name?            string
        |  +--rw type             identityref
        |  +--rw mtu?             uint16
        |  +--rw loopback-mode?   oc-opt-types:loopback-mode-type
        |  +--rw description?     string
        |  +--rw enabled?         boolean
        +--ro state
        |  +--ro name?            string
        |  +--ro type             identityref
        |  +--ro mtu?             uint16
        |  +--ro loopback-mode?   oc-opt-types:loopback-mode-type
        |  +--ro description?     string
        |  +--ro enabled?         boolean
        |  +--ro ifindex?         uint32
        |  +--ro admin-status     enumeration
        |  +--ro oper-status      enumeration
        |  +--ro last-change?     oc-types:timeticks64
        |  +--ro logical?         boolean
        |  +--ro management?      boolean
        |  +--ro cpu?             boolean
[...]

!
! You can also filter to a specific tree-path section
$ pyang openconfig-interfaces.yang -f tree --tree-path=/interfaces/interface/state/counters
module: openconfig-interfaces
  +--rw interfaces
     +--rw interface* [name]              # <-- this means you can use a filter [name=<string>] or [name=*]
        +--ro state
           +--ro counters
              +--ro in-octets?             oc-yang:counter64
              +--ro in-pkts?               oc-yang:counter64
              +--ro in-unicast-pkts?       oc-yang:counter64
              +--ro in-broadcast-pkts?     oc-yang:counter64
              +--ro in-multicast-pkts?     oc-yang:counter64
              +--ro in-errors?             oc-yang:counter64
              +--ro in-discards?           oc-yang:counter64
              +--ro out-octets?            oc-yang:counter64
              +--ro out-pkts?              oc-yang:counter64
              +--ro out-unicast-pkts?      oc-yang:counter64
              +--ro out-broadcast-pkts?    oc-yang:counter64
              +--ro out-multicast-pkts?    oc-yang:counter64
              +--ro out-discards?          oc-yang:counter64
              +--ro out-errors?            oc-yang:counter64
              +--ro last-clear?            oc-types:timeticks64
              +--ro in-unknown-protos?     oc-yang:counter64
              +--ro in-fcs-errors?         oc-yang:counter64
              +--ro carrier-transitions?   oc-yang:counter64
              +--ro resets?                oc-yang:counter64



!
pyang openconfig-acl.yang -f tree
module: openconfig-acl
  +--rw acl
     +--rw config
     +--ro state
     |  +--ro counter-capability?   identityref
     +--rw acl-sets
     |  +--rw acl-set* [name type]
     |     +--rw name           -> ../config/name
     |     +--rw type           -> ../config/type
     |     +--rw config
     |     |  +--rw name?          string
     |     |  +--rw type?          identityref
     |     |  +--rw description?   string
     |     +--ro state
     |     |  +--ro name?          string
     |     |  +--ro type?          identityref
     |     |  +--ro description?   string
     [...]
```

### **GNMIC**
Simliar to PYANG you can use gNMIC at https://gnmic.openconfig.net
However gnmic is a gNMI CLI client that provides full support for Capabilities, Get, Set and Subscribe RPCs with collector capabilities:
 - Full support for gNMI RPCs.  
   Every gNMI RPC has a corresponding command with all of the RPC options configurable by means of the local and global flags.
 - Flexible collector deployment.  
   gnmic can be deployed as a gNMI collector that supports multiple output types (NATS, Kafka, Prometheus, InfluxDB,...).
   The collector can be deployed either as a single instance, as part of a cluster, or used to form data pipelines.
 - gNMI data manipulation.  
   gnmic collector supports data transformation capabilities that can be used to adapt the collected data to your specific use case.
 - Dynamic targets loading.  
   gnmic support target loading at runtime based on input from external systems.
 - YANG-based path suggestions
   Your CLI magically becomes a YANG browser when gnmic is executed in prompt mode. In this mode the flags that take XPATH values will get auto-suggestions based on the provided YANG modules. In other words - voodoo magic 🤯

Etc.. see the website for full list.. Note that GNMIC is written in golang and its source code is publicly available here: https://github.com/openconfig/gnmic  
Also it is available as a container.

```
# after installing gnmic, you can use it from the previous set
# by loading the files (--file option in this case loads everything in the yang_moudles folder) and creating a prompt
# Note that you will get autocompletion for both commands and paths and a brief explanation of the path!

cd yang_modules
gnmic --file ./ prompt


gnmic>  get --path /interfaces/interface[name=*]/state/counters/in-pkts
Error: failed getting targets config: failed reading targets config: no targets found
gnmic> 
```

<img src="../pictures/gnmic_get_path.png" alt="GNMIC Get PATH" style="height: 400px; width:1600px;"/>

Note that **GNMIC** can use yaml file instead of passing options via the command line; by default gnmic will look for a file called `.gnmic.yml` (file extension can also be yaml/json);   
if you want to specify a different file path you can just use the option `--config <file>`     
Note that environment variables can also be used, for instance some examples are here:
- GNMIC_ADDRESS: matches the option --address <ip:port>
- GNMIC_PASSWORD: matches the option --password <pwd>
- GNMIC_USERNAME: matches the option --username <user>

An example of a gnmic config file is below:
```
[gnmic config file]
---
username: admin
password: sros
port: 57400
timeout: 5s
skip-verify: true
tls-key: /path/to/client.key
tls-cert: /path/to/client.crt
tls-ca: /path/to/ca.crt

targets:
  172.17.0.100:
    timeout: 2s
    subscriptions:
      - sub1
    outputs:
      - output1
      - output3
  172.17.0.101:
    username: sros
    password: sros
    insecure: true
    subscriptions:
      - sub2
    outputs:
      - output2
      - output3
  172.17.0.102:57000:
    password: sros123
    tls-key: /path/file1
    tls-cert: /path/file2

    
subscriptions:
  sub1:
    paths:
      - /configure/port[port-id=*]
      - /state/port[port-id=*]
    stream-mode: on_change # target-defined # sample
  sub2:
    paths:
       - /configure/port[port-id=*]/statistics
    stream-mode: sample
    sample-interval: 10s

outputs:
  output1:
    type: file
    file-type: stdout
  output2:
    type: file
    filename: local.log
  output3:
    type: nats
    address: localhost:4222
    subject-prefix: telemetry
    username:
    password:
  [...]
```
#### GNMIC OPTIONS
Other gnmic options that can be useful (they can be applied to all type of requests.. not necessarily get requests):
- --log: this display the log messages from the request (you can log to a file or just on screen)
- --debug: verbose debug messages; useful if you want to have a look at what the source code does.. note that this level of tracing will show  
  username and password
- --print-request: this will print the **paths,encoding and data-type (for filter)** of the request:
  ```
  gnmic -a 192.168.122.3:6030 -u admin -p admin --insecure get --insecure --path "interfaces/interface[name=Ethernet3]/state/counters" --print-request 
  Get Request:
  {
    "paths": [
      "interfaces/interface[name=Ethernet3]/state/counters"
    ],
    "encoding": "JSON",
    "data-type": "ALL"
  }
  Get Response:
  [
    {
      "source": "192.168.122.3:6030",
      "timestamp": 1721730047315664554,
      "time": "2024-07-23T11:20:47.315664554+01:00",
      "updates": [
  [...]
  ```      
- --format: changes the format of the response back and supports: `flat, proto, protojson, prototext, json, event`  (default is json)  
  In particular flat will show the full **Xpath** plus the value
  ```
  gnmic -a 192.168.122.3:6030 -u admin -p admin --insecure get --insecure --path "interfaces/interface[name=Ethernet3]/state/counters" --format flat
    interfaces/interface[name=Ethernet3]/state/counters/openconfig-interfaces:carrier-transitions: 2
    interfaces/interface[name=Ethernet3]/state/counters/openconfig-interfaces:in-broadcast-pkts: 0
    interfaces/interface[name=Ethernet3]/state/counters/openconfig-interfaces:in-discards: 0
    interfaces/interface[name=Ethernet3]/state/counters/openconfig-interfaces:in-errors: 0
    interfaces/interface[name=Ethernet3]/state/counters/openconfig-interfaces:in-fcs-errors: 0
    [...]


  gnmic -a 192.168.122.3:6030 -u admin -p admin --insecure get --insecure --path "interfaces/interface[name=Ethernet3]/state/counters" --format event
  [
    {
      "name": "get-request",
      "timestamp": 1721729243807457405,
      "tags": {
        "interface_name": "Ethernet3",
        "source": "192.168.122.3:6030"
      },
      "values": {
        "/interfaces/interface/state/counters/openconfig-interfaces:carrier-transitions": "2",
        "/interfaces/interface/state/counters/openconfig-interfaces:in-broadcast-pkts": "0",
        "/interfaces/interface/state/counters/openconfig-interfaces:in-discards": "0",
        "/interfaces/interface/state/counters/openconfig-interfaces:in-errors": "0",
        "/interfaces/interface/state/counters/openconfig-interfaces:in-fcs-errors": "0",
        [...]

  ```

### YANG MODELS
Are generally available in either the openconfig repo github or on vendor's specific repos, e.g. https://github.com/aristanetworks/yang  
If you want to use GNMIC with Bendor specific (Arista in this case) models, you'll have to clone the vendor's repo and point gnmic to the correct file:
```
gnmic --file EOS-<version>/openconfig/public/release/models \     <--- this path points to a file in the arista repo (locally cloned)
      --dir  ../public/third_party/ietf                     \     <--- this path points to the openconfig public repo (locally cloned)
      --exclude ietf-interfaces                             \
      prompt


# if you want to get the (very long) list of paths you can do instead
gnmic --file EOS-<version>/openconfig/public/release/models \
      --dir  ../public/third_party/ietf                     \ 
      --exclude ietf-interfaces                             \
      path

```

You might also want to generate a json/yaml representation of a model to see what parameters/values you need to provide if you want to configure
a specific path  
You can do that with the keyword: **generate** when you specify a `--path`:  
Note that you will see both fields that are **rw** and **ro** and not always the distinction is clear..
```
gnmic --file ./ --exclude ietf-interfaces --path <path> generate 

gnmic --file ./ --encoding json_ietf --exclude ietf-interfaces --path interfaces/interface[name=Ethernet3]/state generate 
admin-status: ""
counters:
  carrier-transitions: ""
  in-broadcast-pkts: ""
  in-discards: ""
  in-errors: ""
  in-fcs-errors: ""
[...]
cpu: ""
description: ""
enabled: "true"
forwarding-viable: "true"
hardware-port: ""
hashing-policy: ""
id: ""
ifindex: ""
in-rate: ""
last-change: ""
logical: ""
loopback-mode: ""
management: ""
mtu: ""
name: ""
oper-status: ""
out-rate: ""
physical-channel: []
tpid: oc-vlan-types:TPID_0X8100
transceiver: ""
type: ""


gnmic --file ./ --encoding json_ietf --exclude ietf-interfaces --path interfaces/interface[name=Ethernet3]/config generate 
description: ""
enabled: "true"
forwarding-viable: "true"
hashing-policy: ""
id: ""
loopback-mode: ""
mtu: ""
name: ""
tpid: oc-vlan-types:TPID_0X8100
type: ""
```

### GNMI SETUP EXAMPLE ON ARISTA
The following snippet of command will enable gnmi on port 6030 on an arista switch
```
# conf t
config)# management api gnmi
config-mgmt-api-gnmi)# transport grpc default
config-mgmt-api-gnmi)# provider eos-native                   <- required to access native (i.e. arista/vendor) ynag modules
config-mgmt-api-gnmi)# wr
#
# show management api gnmi

Octa: enabled

Transport: default
Enabled: yes
Server: running on port 6030, in default VRF
SSL profile: none
QoS DSCP: none
Authorization required: no
Accounting requests: no
Notification timestamp: last change time
Listen addresses: ::
Authentication username priority: x509-spiffe, metadata, x509-common-name
```


# GNMI OPERATIONS WITH GNMIC

### GNMIC CAPABILITIES
This gives you: 
- a list of supported encodings 
- a list of supported models (so you can check what path are in those modules)
- the GNMI Version
You can query for capabilities with gnmic:
```
gnmic -a <host>:<port=6030>  -u <user> -p <pwd> --insecure capabilities

$ gnmic -a 192.168.122.3:6030 -u admin -p admin --insecure capabilities | more
gNMI version: 0.7.0
supported models:
  - openconfig-ospf-policy, OpenConfig working group, 0.1.3
  - arista-exp-eos-mlag, Arista Networks <http://arista.com/>, 
  - openconfig-sampling, OpenConfig working group, 0.1.0
  - openconfig-isis-flex-algo, Arista Networks <http://arista.com/>, 0.6.1
  - ietf-netconf-monitoring, IETF NETCONF (Network Configuration) Working Group, 
  - arista-routing-policy-notsupported-deviations, Arista Networks, Inc., 
  - openconfig-ospf-types, OpenConfig working group, 0.1.3
  - arista-exp-eos-l2protocolforwarding, Arista Networks, Inc., 
  - arista-l1-open-config-optical-channel-model-aug, Arista Networks <http://arista.com/>, 1.0.0
  - arista-network-instance-notsupported-deviations, Arista Networks, Inc., 
[...]
supported encodings:
  - JSON
  - JSON_IETF
  - ASCII


```


### GNMIC GET
You can run a single get request but also multiple get requests from different multiple paths: just use multiple `--path <path>` options;  
In both cases the result is returned inside a list under the keyword **updates**.  
In the same way, you can point to different target by using `-a <address>` multiple times in your request; the results are always included in a list
and presented as dictionaries.    
Requests can also be filtered by type with the options: **ALL, CONFIG, STATE, OPERATIONAL** and the default being **ALL**; the filter is applied
with the `--type <OPTION>` command;  
Finally you can also specify the option `--values-only` which will return, instead of a dictionary with key: value, just a lists of values..so   
I guess it could be useful if you are very specific in your query..  
Notes: 
- Some **gnmic** options are actually for NOKIA devices only..
- Below I did not use double quotes in the path but it's good practice to use them
- Again be aware that even if a model is supported, it does not mean that every path will be implemented by the device..
```
[single path request]
gnmic --address <host>:<port=6030>  \
      -u <user> -p <pwd> --insecure \
      get --path "<path>"
      
# gnmic -a 192.168.122.3:6030 -u admin -p admin --insecure get --path interfaces/interface[name=Ethernet3]/state/counters | more
[
  {
    "source": "192.168.122.3:6030",
    "timestamp": 1721726470248628184,
    "time": "2024-07-23T10:21:10.248628184+01:00",
    "updates": [
      {
        "Path": "interfaces/interface[name=Ethernet3]/state/counters",
        "values": {
          "interfaces/interface/state/counters": {
            "openconfig-interfaces:carrier-transitions": "2",
            "openconfig-interfaces:in-broadcast-pkts": "0",
            "openconfig-interfaces:in-discards": "0",
            "openconfig-interfaces:in-errors": "0",
[...]           


[multiple path request]
gnmic --address <host>:<port=6030>      \
      -u <user> -p <pwd> --insecure get \
      --path "<path1>"                  \  
      --path "<path2>"      

gnmic -a 192.168.122.3:6030 -u admin -p admin --insecure get                    \
   --path interfaces/interface[name=Ethernet3]/state/counters/in-broadcast-pkts \
   --path interfaces/interface[name=Ethernet3]/state/counters/out-errors
[
  {
    "source": "192.168.122.3:6030",
    "timestamp": 1721726805252385617,
    "time": "2024-07-23T10:26:45.252385617+01:00",
    "updates": [
      {
        "Path": "interfaces/interface[name=Ethernet3]/state/counters/in-broadcast-pkts",
        "values": {
          "interfaces/interface/state/counters/in-broadcast-pkts": 0
        }
      }
    ]
  },
  {
    "source": "192.168.122.3:6030",
    "timestamp": 1721726805252385617,
    "time": "2024-07-23T10:26:45.252385617+01:00",
    "updates": [
      {
        "Path": "interfaces/interface[name=Ethernet3]/state/counters/out-errors",
        "values": {
          "interfaces/interface/state/counters/out-errors": 0
        }
      }
    ]
  }
]      
```


### GNMI SET OPERATIONS
SET operations are used when you want to configure the devices; it can work in different ways:
- **UPDATE**: similar to a "merge" operation: only the provided data/keys is modified: existing data that is not specified in the update remains unchanged
- **REPLACE**: overwrites data at a specified path; it replaces the entire path with the provided data and previous data is lost.  
  You might need to use this to remove configuration..
- **DELETE**: removes the data from the specified path (this does not require a payload.. everything under the path will be deleted)

In **GNMIC** you create the payload structure for a set request using the generate command:

```
# this assumes:
# - open config modules are all downloaded into yang_modules, if not you need to point --dir to the folder with file from 
#   the open configu public repo and from the path:  ~/public/third_party/ietf
# - the vendor/device models are available at the path referenced by the --file <path> option, in this case we use arista
# - the encoding is selected based on the vendor compatibility (arista wants ietf_json)
# - here we use the --replace option
gnmic generate                                                  \
      --encoding json_ietf                                      \
      --file  yang/EOS-4.23.2F/openconfig/public/release/models \ # vendor models for specific device/os
      --exclude ietf-interfaces                                 \
      --dir yang_modules/                                       \ # this is where the public/third_party/ietf modules are located
      set-request                                               \ # command to generate payload
      --replace /network-instances/network-instance/vlans       \ # <path> that we want to replace

replaces:
- path: /network-instances/network-instance/vlans
  value:
    vlan:
    - config:
        name: ""
        status: ACTIVE
        vlan-id: ""
      members: {}
      vlan-id: ""
  encoding: JSON_IETF
```
from the excerpt generated above you can create your own content for value; for instance, assuming we want to create 2 vlans: 1004 and 1005  
with names respectively test-vlan and dc-vlan we would amend the payload to something like this:
```
---
vlan:
  - config:
      name: "test-vlan"
      status: ACTIVE
      vlan-id: "1004"
    members: {}
    vlan-id: "1004"        
  - config:
      name: "dc-vlan"
      status: ACTIVE
      vlan-id: "1005"        
    members: {}
    vlan-id: "1005"
```
Note that, the exact value combination that works might need some testing.. or you might want to generate a similar configuration first on a device
and then extract it from there to see the values..

Once the yaml config is prepared (and saved to a file, e.g. vlan.yaml) you can use it in your **set** command
```
# Note: 
# - arista wants to specify the name=default network instance set when setting vlans with this path
# - using the update option you can point to the root path / 
#   and configure multiple things at the same time.. of course your payload will have to be prepared differently
# - the configuration is applied but not saved
# - the configuration file provided can also be json (just point to a .json file)
# - the --gzip just compreses the data and makes everything quicker

 gnmic -a 192.168.122.3:6030 -u admin -p admin --insecure --insecure --gzip set  \
 --update-path "/network-instances/network-instance[name=default]/vlans"  \ 
 --update-file vlan.yaml 

{
  "source": "192.168.122.3:6030",
  "timestamp": 1721732636969508268,
  "time": "2024-07-23T12:03:56.969508268+01:00",
  "results": [
    {
      "operation": "UPDATE",
      "path": "network-instances/network-instance[name=default]/vlans"
    }
  ]
}

```

Notes:
- Arista let you run cli command to the box if you send them to the path: `"cli:/"`, the structure is
  ```
  updates:
    - path: "cli:/"
      value: interface Ethernet 3
    - path: "cli:/"
      value: description TEST description
    - path: "cli:/"
      value: switchport mode access
    - path: "cli:/"
      value: write memory
  ```
  The option for the set command need to  have `--encoding ascii` and `--request-file <yaml_command_file>`. However this is not great.. commands  
  are run one by one.. and it kinda falls back not to use gnmi.. (instead of the files you could send multiple update requests to the cli path but not great..).  
  You might want to use this to **save the config**
- while the example use the `--update-path`, `--update-file` the process would be the same with replace.. you would just need to use `--replace-path`, `--replace-file`
- we used files to replace values as we had multiple values to replace.. you could however just use the flag `--update-value`, `--replace-value`




### GNMI SUBSCRIBE OPERATIONS
Subscribe requests allow to get updates from the device either periodically or when we have a state change. The updates are small because we are using grpc and it's really good to stream data efficiently.  
These updates are then supposedly sent to a broker message (e.g. kafka) and then to some time series database like influxdb or Prometheus

When creating subscriptions there's a lot of different subscriptions options..  The most important sets the way you get updates with `--stream-mode`:  
- **ON_CHANGE**: Updates are only sent when the value of the entry item changes. 
- **SAMPLE**: Data is sent at periodic interfaces as specified in the sample interfval field --sample-intervale
- **TARGET_DEFINED**: if the path specified refers to leaves that are event-driven, then an **on_change** subscription may be created (e.g. interface up/down admin-state);   
  if the data represents coutners value a **sample** subscription is used (e.g. interface counters)

Once the stream mode is set, you can also set a **heartbeat** with `--heatbeat-interval`; if this is set there must always be one update for every heartbeat, even if the stream mode is **on_change** or **sample** with `--suppress-redundant` and no changes have occurred
```
 gnmic -a 192.168.122.3:6030 --gzip -u admin -p admin --insecure subscribe  \
       --path "/interfaces/interface[name=Ethernet3]/state/counters"        \
       --sample-mode sample                                                 \       
       --sample-interval 60s                                                \
       --format flat

interfaces/interface[name=Ethernet3]/state/counters/in-broadcast-pkts: 0
interfaces/interface[name=Ethernet3]/state/counters/in-discards: 0
interfaces/interface[name=Ethernet3]/state/counters/in-errors: 0
interfaces/interface[name=Ethernet3]/state/counters/in-fcs-errors: 0
interfaces/interface[name=Ethernet3]/state/counters/in-multicast-pkts: 0
interfaces/interface[name=Ethernet3]/state/counters/in-octets: 0
interfaces/interface[name=Ethernet3]/state/counters/in-pkts: 0
interfaces/interface[name=Ethernet3]/state/counters/in-unicast-pkts: 0
interfaces/interface[name=Ethernet3]/state/counters/out-broadcast-pkts: 0
interfaces/interface[name=Ethernet3]/state/counters/out-discards: 0
interfaces/interface[name=Ethernet3]/state/counters/out-errors: 0
interfaces/interface[name=Ethernet3]/state/counters/out-unicast-pkts: 0

interfaces/interface[name=Ethernet3]/state/counters/carrier-transitions: 2
---> this is an update
interfaces/interface[name=Ethernet3]/state/counters/out-multicast-pkts: 10622
interfaces/interface[name=Ethernet3]/state/counters/out-octets: 1335741
interfaces/interface[name=Ethernet3]/state/counters/out-pkts: 10622
---> this is an update
interfaces/interface[name=Ethernet3]/state/counters/out-multicast-pkts: 10623
interfaces/interface[name=Ethernet3]/state/counters/out-octets: 1335864
interfaces/interface[name=Ethernet3]/state/counters/out-pkts: 10623


```
As before, you can subscribe to multiple paths at the same time