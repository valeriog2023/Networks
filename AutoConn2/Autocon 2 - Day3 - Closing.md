# Autocon 2 - Netwok Automation ( 22/11/2024)

## Closing talks and notes

## Talk 1 - Network automation at digital Ocean
By Mircea Ulinic

### Tools:
- **Netbox**  
  Using Netbox Scripts; they allow to interact dynamiccaly with the Data (in Netbox) 
  and create new Data in Netbox
  E.g. 1 
  they used to build rack using the UI of netbox to fill in the data for the script
  when the script is executed it creates the racks, IP allocation, PDU, etc..
  (This happens before the physical devices are there)
  E.g. 2
  Using scripts they are able to go through the data and generate reports dedicated to specific checks
  (like do we have duplicated IPs in loopbacks, prefix validation, etc..)

- **Peering Manager**  
  Similar to Netbox: https://peering-manager.net
  but an underrated project

- **IRRD**  
  https://irrd.readthedocs.io
  This run internal whois for peering hygiene

### Configuration Management:
- **Salt**  
  - Vendor Agonstic (integrate with napalm)
  - Tried and tested n many large scale environment
  - Deploy configuration changes frequently across a portion of the fleet
  - Orchestration and even driven capability
  - Many integrations out of the box
    Easily develop new features using a Turing complete language (Python)
  - Rest API

  <Salt design picture>

  Note that Arista allows to deply a proxy minion directly on the switch so that's what they are planning to do
  but anyway only 35% of the fleet is managed directly, for the remaining part they use salt-sproxy

  Overall it oes not matter how the devices are managed

- tooling integration:
  <picture>

**Use Case example:**  
They use ZTP using salt generating the configuration for devices that are staged in netbox
the configuration is placed in NGINX server
devices get an IP via DHCP, download a script that fetches the config from the NGINX


### Monitoring:
- **Promtheus**  
  Scrapes the data via http and saves it into a time series
  Exporters can be used to connect to objects that have no possibility to be scraped directly via http
  (not used/sued for telemetry)

- **Alerta**
  Simple dahsboar that presetnts alerts (from alertmanager) and allows lots of customization
  it also allows integration with netbox (to get information for instance about interface names/descriptions)
  --> Also used to put the alert into a Rabbit MQ message queue
  --> Salt will get the message and start running some checks possibly creating a Jira and running some actions

### Network Automation and AI

GPU droplets are virtual machines powered by GPU offered


## Talk 2 - Total Network Operations (TNOps): Navigating Disruption and Preparing for the Future
By Scott Robohn

TNOps is a project with a podcast: an opportunity to discuss with people what they are doing so that we collectively
improve
What came out of it is:
- have an holistic System
- always keep learning
- how to adapt DevOps to NetOps

Netops is considered:
- Lowest rung of the ladder below NetEng and NetArch
- does not get constructive attention it could use
- CAPEX (gear) is easy to identify; OPEX for ops can be 10x but is spread out and harder to track

This can change and network automation is of great importance to NetOps but people and process are as important as that.

TNOS Stack / Framework 
<picture>
the situation gets more and more complex and needs to be connected to serve a higher purpose

### Organize Ops to manage Disruption
It's part of Tech and IT overall, disruption is nothing new..
oftware will become more and more important;  
Caveats:
- Beware buzzwords
- Hardwares is still important (sw runs on hw)

Overall this is not really a technical talk.. mostly just a talk a bit generic and all over the places about embracing changes.

