# BATFISH NOTES

Batfish is a vendor agnostic network analysis tool; the goal of Batfish is to:
- Analyze network setup using offline snapshots from the device configurations
- Answer questions about the network via **pybatfish** which is a python library used to itneract with Batfish API  
  Note: you can also use an Ansible role (that use pybatfish under the hoods).  
- Simulate Control Plane. The type of questions you can ask Batfish is for instance, what is going to happen to a flow between A and B if I make this change?  
  What if I take down one node in the path? Etc..


Batfish is completely offline and you can you use it to validate changes before actually applying them to production.
Because it's offline and based on device models (not actually running devices OS) you can use it to analyze easily large scale networks with somewhat limited resources (1K device with 64GB ram seems reasonable); also, consider that virtual OS are usually lacking features that depend on actual hardware, this is instead ont a problem with batfish as it only works with device models.

Overall the use cases are:
- Validate configuration
- Query control plane state
- Verify ACL behaviour
- Analyze routing/flow paths
- Simulate network failure (impact analysis)
- Check if there is any unused configuration applied (general admin)

Note: be aware about supported devices; you can find a reference for supported devices, here:

https://batfish.readthedocs.io/en/latest/supported_devices.html

and limitations, for instance it **does not support: MPLS, IPv6** and has some other limitations for L2 operations (e.g. it does not support VPC) 


Many example and other things can also be found in Batfish official repo here:

https://github.com/batfish/batfish/tree/master

## BATFISH SETUP

Batfish can run in the form of a docker container.. so you'll need to have docker installed and runnig. Once you are ready you can launch it as follows:

```
! pull the container image
sudo docker image pull batfish/allinone


! verify the container image
sudo docker image ls 
REPOSITORY         TAG       IMAGE ID       CREATED       SIZE
batfish/allinone   latest    f62d3a939b17   13 days ago   1.53GB


!
! create a folder for Batfish Data (with an empty python file) and then run the container
mkdir -p /batfish-data/snapshot/configs
mkdir -p /batfish-data/output
touch /batfish-data/main.py              

sudo docker run -d --name batfish -v /batfish-data:/data -p 8888:8888 -p 9997:9997 -p 9996:9996 batfish/allinone

!
! check it is running, connect and verify the volume is mounted correctly (you should see the test file)
sudo docker container ls | grep batfish
ba11c95d7796   batfish/allinone        "./wrapper.sh"    

sudo docker container exec -it batfish bash
root@ba11c95d7796:/# ls -l /data/
-rw-rw-r--. 1 1000 1000  0 Jul 24 14:52 main.py
drwxrwxr-x. 2 1000 1000  6 Jul 24 14:50 output
drwxrwxr-x. 3 1000 1000 21 Jul 24 14:46 snapshot


```

As you can see Batfish requries 3 TCP ports: **8888,9996 and 9997** and you need to mount a volume where you will put the network snapshots.  
Once Batfish container is running, you will still need to install the python pybatfish library
```
$ python3 --version
Python 3.11.7

$ python3 -m pip install pybatfish
[...]
Installing collected packages: pytz, urllib3, tzdata, six, simplejson, PyYAML, ordered-set, numpy, idna, charset-normalizer, certifi, attrs, requests, python-dateutil, deepdiff, requests-toolbelt, pandas, pybatfish
Successfully installed PyYAML-6.0.1 attrs-23.2.0 certifi-2024.7.4 charset-normalizer-3.3.2 deepdiff-7.0.1 idna-3.7 numpy-2.0.1 ordered-set-4.1.0 pandas-2.2.2 pybatfish-2024.7.22.1569 python-dateutil-2.9.0.post0 pytz-2024.1 requests-2.32.3 requests-toolbelt-1.0.0 simplejson-3.19.2 six-1.16.0 tzdata-2024.1 urllib3-2.2.2


$ python3
Python 3.11.7 (main, Jan 26 2024, 19:22:20) [GCC 8.5.0 20210514 (Red Hat 8.5.0-21)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pybatfish
>>> 

```

Finally we can prepare the data and data structure inside the batfish-data folder on the main host:
```
+--batfish-data
   +--snapshots
      +--site1           # <--- we use this as name of the snapshot
      |  +--configs      # <--- a folder called config is required
      |     +--R1.cfg    # <--- these are the sw hostnames
      |     +--R2.cfg
      |     +--R3.cfg
      |  +--batfish      # <--- a folder called batfish can be added for optional extra info
      |     +--isp_config.json
      |     +--layer1_topology.json 
   +--main.py

Notes: for network devices you can put the show running output while for cumulus linux you will need
       to collect and put in a single file hostname.cfg the output of the commands:
       hostname
       cat /etc/network/interfaces
       cat /etc/cumulus/ports.conf
       cat /etc/frr/frr.conf
```

## PYTHON TO BATFISH SETUP
Once the configuration are in place, we can use **pybatfish** to interact with **batfish**, below a sample snippet of code; in particular:

 - **bf_session** is used to provide details for communication with the Batfish application (e.g., IP address, API token, etc).
 - **bf_init_snapshot** is used to upload your configuration files into the Batfish application.
 - **load_questions** is used to initialise the Batfish Questions.
 - **bfq** is used to ask the question and receive the response.

After that we create the variables, which we need for our Python script to work:
- **bf_address**: the IP address we are using to connect to Batfish. As it's a local container this is 127.0.0.1
- **snapshot_path**: the path towards the directory with your snapshots.
- **output_dir**: the path to the directory, where we will be storing the results.


The following snippet of code will load the configuration from one snapshot and run just a brief summary.  
This code has been tested using a basic EVE-NG Lab setup with Cisco IOS (at some point I'll load the lab details somewhere in the repo..)
The LAB is anyway made up of 8 routers, one of which is working as a host and runs some basic OSPF, BGP and multicast
```
[main.py]
#!/usr/bin/env python
import logging
from rich import print as rprint

from pybatfish.client.session import Session

BF_HOST="127.0.0.1"
BF_SNAPSHOT_NAME = "site1"
BF_SNAPSHOT_PATH = f"snapshots/{BF_SNAPSHOT_NAME}"  # note this is the local path on the host



if __name__ == "__main__":
    # Setting host to connect
    logging.getLogger("pybatfish").setLevel(logging.ERROR)
    bf = Session(host=BF_HOST)

    
    bf.init_snapshot(BF_SNAPSHOT_PATH, overwrite=True)

    # The following 3 operations return a brief review of the configuration just parsed
    # note that they are all available under bf.q which stands for questions on the session
    # File Parse Status
    # Parse Warnings
    # Init Issues
    #    
    file_parse_status = bf.q.fileParseStatus().answer()
    parse_warnings = bf.q.parseWarning().answer()
    init_issues = bf.q.initIssues().answer()
    #
    # You can decide to exit if there are issues.. Note: that the if is using a pandas attribute via the frame() method
    if not init_issues.frame().empty:
        rprint(":cross_mark: Validation issues found.")
        #sys.exit(1)
        rprint(init_issues)
        user_answer = input("Do you still want to proceed? [y/n] ").lower()
        if not user_answer.startswith("y"):
            sys.exit()

    rprint(f"File Parse status result:\n{file_parse_status}")
    rprint(f"\nFile Parse Warnings result:\n{parse_warnings}")


```

when executed it prints:
```
>>> rprint(file_parse_status)
           File_Name                  Status File_Format   Nodes
0  configs/Host1.cfg  PARTIALLY_UNRECOGNIZED   CISCO_IOS  ['h1']
1     configs/R1.cfg  PARTIALLY_UNRECOGNIZED   CISCO_IOS  ['r1']
2     configs/R2.cfg  PARTIALLY_UNRECOGNIZED   CISCO_IOS  ['r2']
3     configs/R3.cfg  PARTIALLY_UNRECOGNIZED   CISCO_IOS  ['r3']
4     configs/R4.cfg  PARTIALLY_UNRECOGNIZED   CISCO_IOS  ['r4']
5     configs/R5.cfg  PARTIALLY_UNRECOGNIZED   CISCO_IOS  ['r5']
6     configs/R6.cfg  PARTIALLY_UNRECOGNIZED   CISCO_IOS  ['r6']
7     configs/R9.cfg  PARTIALLY_UNRECOGNIZED   CISCO_IOS  ['r9']


# The format is for all of the answers, a TableAnswer object similar to a dataframe and you can actually get the dataframe: file_parse_status.frame()
```

Note that even if there are parts of the configuration that are not recognized, you might be good to go.. just doulbe check that the parts that are not recognized are not
related with the questions you want to ask..  
If you want to integrate batfish in your tests, you should whitelist the issues you know about and fail the workflow in case things outside the whitelist come up


### SNAPSHOTS
Snapshots is a collection of plain-text files that contain information about the network.  
The layout of each snapshot is:
```
configs/         #-> this is required and it contains actual device configuration (startup/running)
  |- R1.cfg
  |- R2.cfg
  |- R3.cfg  
  [...]
hosts/           #-> this is optional and it would include json files names of hosts and their interfaces/IP (so this folder is not for network devices)
  |- server1.json
  |- server2.json
  [...]  
iptables/       #-> this is also optional and it would include iptables rules for the hosts in the host folder
  |- server1.iptables


An example for server1.json:
{
    "hostname": "server1",
    "ipTableFile": "iptables/server1.iptables",
    "hostInterfaces": [
        "eth0": {
            "name": "eth0", 
            "prefix": "192.168.0.1/24",
            "gateway": "192.168.0.254"
        }
    ]  
}

The format for the iptables fiels is just a print of the iptables chain rules e.g. an empty set of rules would be something like:
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination 
```

You can/should also add other information to add extra information for Batfish


# BATFISH Questions

Batfish can answer a set of questions, see https://pybatfish.readthedocs.io/en/latest/questions.html  
They are all available under the session object **bf.q**
```
dir(bf.q)
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_session', 'a10VirtualServerConfiguration', 'aaaAuthenticationLogin', 'bgpEdges', 'bgpPeerConfiguration', 'bgpProcessConfiguration', 'bgpRib', 'bgpSessionCompatibility', 'bgpSessionStatus', 'bidirectionalReachability', 'bidirectionalTraceroute', 'compareFilters', 'comparePeerGroupPolicies', 'compareRoutePolicies', 'definedStructures', 'detectLoops', 'differentialReachability', 'edges', 'eigrpEdges', 'evpnL3VniProperties', 'evpnRib', 'f5BigipVipConfiguration', 'fileParseStatus', 'filterLineReachability', 'filterTable', 'findMatchingFilterLines', 'hsrpProperties', 'initIssues', 'interfaceMtu', 'interfaceProperties', 'ipOwners', 'ipsecEdges', 'ipsecSessionStatus', 'isisEdges', 'layer1Edges', 'layer3Edges', 'list', 'list_tags', 'load', 'loopbackMultipathConsistency', 'lpmRoutes', 'mlagProperties', 'multipathConsistency', 'namedStructures', 'nodeProperties', 'ospfAreaConfiguration', 'ospfEdges', 'ospfInterfaceConfiguration', 'ospfProcessConfiguration', 'ospfSessionCompatibility', 'parseWarning', 'prefixTracer', 'reachability', 'referencedStructures', 'resolveFilterSpecifier', 'resolveInterfaceSpecifier', 'resolveIpSpecifier', 'resolveIpsOfLocationSpecifier', 'resolveLocationSpecifier', 'resolveNodeSpecifier', 'routes', 'searchFilters', 'searchRoutePolicies', 'snmpCommunityClients', 'subnetMultipathConsistency', 'switchedVlanProperties', 'testFilters', 'testRoutePolicies', 'traceroute', 'undefinedReferences', 'unusedStructures', 'userProvidedLayer1Edges', 'viConversionStatus', 'viConversionWarning', 'viModel', 'vrrpProperties', 'vxlanEdges', 'vxlanVniProperties']

```
Using python **rich.inspect** module you can also visualize them better
```
from rich import inspect

>>> inspect(bf.q,methods="all")
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── <class 'pybatfish.question.question.Questions'> 
│ Class to hold and manage (e.g. load, list) Batfish questions.                                                                                                                                                                                                                                │
│                                                                                                                                                                                                                                                                                              │
│ ╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮ │
│ │ <pybatfish.question.question.Questions object at 0x7f2328ab0f40>                                                                                                                                                                                                                         │ │
│ ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯ │
│                                                                                                                                                                                                                                                                                              │
│ a10VirtualServerConfiguration = class a10VirtualServerConfiguration(...) Returns Virtual Server configuration of A10 devices.                                                                                                                                                                │
│        aaaAuthenticationLogin = class aaaAuthenticationLogin(...) Returns nodes that do not require authentication on all virtual terminal lines.                                                                                                                                            │
│                      bgpEdges = class bgpEdges(...) Returns BGP adjacencies.                                                                                                                                                                                                                 │
│          bgpPeerConfiguration = class bgpPeerConfiguration(...) Returns configuration settings for BGP peerings.                                                                                                                                                                             │
│       bgpProcessConfiguration = class bgpProcessConfiguration(...) Returns configuration settings of BGP processes.                                                                                                                                                                          │
│                        bgpRib = class bgpRib(...) Returns routes in the BGP RIB.                                                                                                                                                                                                             │
│       bgpSessionCompatibility = class bgpSessionCompatibility(...) Returns the compatibility of configured BGP sessions.                                                                                                                                                                     │
│              bgpSessionStatus = class bgpSessionStatus(...) Returns the dynamic status of configured BGP sessions.                                                                                                                                                                           │
│     bidirectionalReachability = class bidirectionalReachability(...) Searches for successfully delivered flows that can successfully receive a response.                                                                                                                                     │
│       bidirectionalTraceroute = class bidirectionalTraceroute(...) Traces the path(s) for the specified flow, along with path(s) for reverse flows.                                                                                                                                          │
│                compareFilters = class compareFilters(...) Compares filters with the same name in the current and reference snapshots. Returns pairs of lines, one from each filter, that match the same flow(s) but treat them differently (i.e. one permits and the other denies the flow). │
│      comparePeerGroupPolicies = class comparePeerGroupPolicies(...) Compares the behavior of routing policies across a network change.                                                                                                                                                       │
│          compareRoutePolicies = class compareRoutePolicies(...) Finds route announcements for which the behavior of the route-policies in the given snapshots differ.                                                                                                                        │
│             definedStructures = class definedStructures(...) Lists the structures defined in the network.                                                                                                                                                                                    │
│                   detectLoops = class detectLoops(...) Detects forwarding loops.                                                                                                                                                                                                             │
[...]
```


To access the result you just select a question and use the **.answer()** method (possibly also use **.frame()** to get back a pandas dataframe)


```
[BATFISH QUESTIONS EXAMPLES]
>>> bf.q.ospfAreaConfiguration().answer().frame()
  Node      VRF Process_ID Area Area_Type                                  Active_Interfaces Passive_Interfaces
0   r6  default          1    0      NONE  ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2', ...                 []
1   r3  default          1    0      NONE  ['Ethernet0/0', 'Ethernet0/2', 'Ethernet0/3', ...                 []
2   r4  default          1    0      NONE  ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2', ...                 []
3   r2  default          1    0      NONE        ['Ethernet0/0', 'Ethernet0/2', 'Loopback0']    ['Ethernet0/1']
4   r5  default          1    0      NONE  ['Ethernet0/0', 'Ethernet0/2', 'Ethernet0/3', ...                 []



>>> bf.q.interfaceProperties().answer().frame()
          Interface Access_VLAN Active Admin_Up           All_Prefixes Allowed_VLANs Auto_State_VLAN     Bandwidth Blacklisted Channel_Group Channel_Group_Members  ... Proxy_ARP Rip_Enabled Rip_Passive Spanning_Tree_Portfast       Speed Switchport Switchport_Mode Switchport_Trunk_Encapsulation      VRF VRRP_Groups Zone_Name
0   h1[Ethernet0/0]        None   True     True     ['192.168.9.1/24']                          True    10000000.0       False          None                    []  ...      True       False       False                  False  10000000.0      False            NONE                          DOT1Q     VRF2          []      None
1   h1[Ethernet0/1]        None   True     True     ['192.168.7.1/24']                          True    10000000.0       False          None                    []  ...      True       False       False                  False  10000000.0      False            NONE                          DOT1Q     VRF1          []      None
2   h1[Ethernet0/2]        None  False    False                     []                          True    10000000.0       False          None                    []  ...      True       False       False                  False  10000000.0      False            NONE                          DOT1Q  default          []      None
3   h1[Ethernet0/3]        None  False    False                     []                          True    10000000.0       False          None                    []  ...      True       False       False                  False  10000000.0      False            NONE                          DOT1Q  default          []      None
4   r1[Ethernet0/0]        None  False    False                     []                          True    10000000.0       False          None                    []  ...      True       False       False                  False  10000000.0      False            NONE                          DOT1Q  default          []      None
5   r1[Ethernet0/1]        None   True     True    ['192.168.12.1/24']                          True    10000000.0       False          None                    []  ...      True       False       False                  False  10000000.0      False            NONE                          DOT1Q  default          []      None

[...]
[42 rows x 37 columns]



 bf.q.bgpProcessConfiguration(nodes='/R/').answer()
  Node      VRF Router_ID Confederation_ID Confederation_Members Multipath_EBGP Multipath_IBGP Multipath_Match_Mode         Neighbors Route_Reflector    Tie_Breaker
0   r2  default   2.2.2.2             None                  None          False          False           EXACT_PATH       ['5.5.5.5']           False  ARRIVAL_ORDER
1   r4  default   4.4.4.4             None                  None          False          False           EXACT_PATH  ['192.168.49.9']           False  ARRIVAL_ORDER
2   r5  default   5.5.5.5             None                  None          False          False           EXACT_PATH       ['2.2.2.2']           False  ARRIVAL_ORDER
3   r6  default   6.6.6.6             None                  None          False          False           EXACT_PATH       ['4.4.4.4']           False  ARRIVAL_ORDER
4   r9  default   9.9.9.9             None                  None          False          False           EXACT_PATH  ['192.168.49.4']           False  ARRIVAL_ORDER
```

You can provide additional input information to the questions that act differently depending on the questions (it's basically filtering):
- Filter by node with `nodes='<expression>'`: 
   - Exact filter: e.g. bf.q.bgpProcessConfiguration(nodes='<node_name>').answer()
   - String match: e.g. bf.q.bgpProcessConfiguration(nodes='\<pattern>\').answer()

To know exactly what additional information is supported by each question you need to refer to the documentation of the specific question  https://pybatfish.readthedocs.io/en/latest/questions.html  

Because under the hoods we have a **Pandas** dataframework, you can also use directly Pandas methods, just get the dataframework:

`df = bf.q.bgpProcessConfiguration(nodes='/R/').answer().frame()`  

and:
- convert the result to csv `df.to_csv()`
- convert the result to html `df.to_html()`
- convert the result to dictionary `df.to_dict(orient="records")`
- get a specific row with `df.iloc[<row_number>]` so that you will see the single row as a record (all fields visible)
- check if the result is empty with `df.empty`
- Run a specific **query** on columns, for instance, only show rows rows where the column router ID has a specific value:
  ```
  df.query("Router_ID == '2.2.2.2'")
  0   r2  default   2.2.2.2             None                  None          False          False           EXACT_PATH  ['5.5.5.5']           False  ARRIVAL_ORDER
  ```
  Note that the **query** method supports different operators: `==, in, >, <` etc... basically everything that returns a boolean and can run on a value for a specific column
  (and also on multiple columns)

