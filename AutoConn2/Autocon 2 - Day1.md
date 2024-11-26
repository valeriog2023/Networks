# Autocon 2 - Netwok Automation ( 20/11/2024)

No morning session

## Afternoon session

- check arista avd workshops should be available online
  maybe: https://github.com/aristanetworks/avd-workshops


- check Opsmil infrahub

Networks Automation Forum Feline

## first Talk: why haven't we seen full network automation yet? 

Three reasons:
- History.  
  Primarily this is TELCO and Hardware manuacturers (Cisco historically)
  TELCO was mainly a monopoly (Bell Labs, At&T, etc..) with a lot of anti-competitive behaviour

  In 1953 the US regulations promoted consent decree which limited the TELCO words and this lead to the creation of Open Source world (including Unix)
  
  In 1973 Unix was presented at a conference and AT&T could not sell it (as it was not telco service) so was given away from free

  In 1983 Anti trust law suit (consent decree no longer applies) so At&T started charginig for sw now

  In 1991 Linux starts its journey (AT&T seels rights of Unix to Novell)

  Cisco creates certification which means only specialized people can operate networks and no
  interface interoperability or integration is required (biggest obstacle to automation)

  On the compute side, the need for automation was clear and stressed and took priority over network autoamtion
  this including vendor, etc..

  Google did not want to stick to the entwork devices paradigm and started building their own software platform to control
  multiple devices at the same time
  They had immense pressure for growth
  They had the resources to work on it (mostly using people non specialized in networks that just wanted everything to be programmatic)

- Ecosystem
  
  Ecosystems build on themselves:
    - an innovation is brought forth
    - investment is done on the innovation
    - interoperability with different systems is introduced
    - costs are reduced
    ----> the cycle starts again

    Linux is hustorically a huge innovation and drived of innovations because:
    - it's open suorce
    - it's freee
    - it's suported by the community
    - it runs on everything

    becasue of that, in 2010 Linux gets a critical mass and investment start growing to build SaaS Companies/Sw (massime influ of capitals)

    When are network operating systems reaching crytical mass? 
    Not there yet but Vyos and SONIC are getting there

- Perception
  release of OpenFlow (2012) and OPenSwitch(2013) give the perception that it was time for network automation
  but was it so?

  Different component of technology require different levels for investment:
  -  SW: doesn't require a lot of investment
  -  HW: requires a mid level of investment
  -  Infrastructure (DC, power plants, etc) require a lot of investment

  NEtwork automation is part of all levels so it's not easily achievable to get 

### Barriers
- network sw starts with no programmatic feagures
- ??
- ??

### Acceleratros
- incrasing open sw for netwrk devices
- people close to the problem are developing cross skills
- network automation is in the middle of the adoption curve


-------------------------------------------------
## Second Talk: Partnership with Netbox Lab

Netbox cloud free plan is available  <--- access to the tool is free

What is Diod? It gets data into netbox

In netbox new edition you get change management and branching

Check 
 - Netpicker test network automation
 - check slurp'it
 - container lab 
 - etc..
 there's a lot of movement in network automation (see tools above )

### Netbox discovery and assurance
extracts the current state of the network and onboards it into netbox 
It's separate but it integrates with netwbox (it will be available in all editions of netbox in Q4 2024)

Assurance is also separate but integrted with netbox (comes from Diod)

Approach to discovery and assurance is to have an open ecosystem of tools


------------------------------------------------
## third Talk: Survey Results

I have taken a picture with summary of this


------------------------------------------------
## fourth Talk: Network To Code

Used Nautobot and Python to automate hardware refresh

### Design Driven Automation
Take the workflow and build automation around that

Elements of automation:
- Lifecycle event should be automated (provision/decomm/etc..)
  - idempotency is important 
- integrate with external system  (be sure flows with external/3rd party sytems are not interrupted)
- Day2 operations:  streamlined hardware break/fix processes
- One click complex network changes  

- consolidate visibility: on-prem vs cloud resources
- tool/methods for operational oversight: retrieve and disaplay **only** the necessary information
- Impact on efficiency and decion making (Cudown extraneous information)

Use 
- modular components (HW and manufactures will change)
- Data sources are important
- understand your target users


------------------------------------------------
## Fifth Talk: AI Driven Network Observability
By Jeremy Schulman - Major League Baseball

- Natural Language Processingg
- Named Entity Recognition
  If you see metrics coming in with  a specific tag you should be able to correlate with other metrics with same tag
- Retrieval Augmented Generation (RAG)
- ChatOps for the Network
- Really Cool ahsboard

Observability:
- buy if it is available  -  IP fabric (does depp network analysis)
- borrow from open source - NEtbox
- Build what is not available - chatbox

picture taken:
Yellow is made inhouse

AI takes all the info that comes in, and gives a best RCA possible

The chatbot creates automatically dashboards and graphs based on natural language questions
The AI selector gets the AAA from TACACS Authorization.. it all goes into a datalake and they
are correlated via ML.

LLM can generate real time the dashboard that you want so that you don't have to look for a specific dashboard
in the middle of hundreds of different dashboards

### chatops
teams outside of the network can use to interact the network
they can use to shut/no shut ports and give visiibility of other stats

Okta is used to fine grains perms in slack with a protocol called skim
Note the chatbot actually creates forms that people have available in slack
the forms gets data from netbox to give the content information

----
Multicast Tree Observability
- subscribers and sources
- health of links on the path

- integrating selector.ai (LLM) Copilot with ChatOps

---> check Building RAG Chatbots With Langchain In Python, e.g. https://realpython.com/build-llm-rag-chatbot-with-langchain/

------------------------------------------------
## Sixth Talk: The tale of 2 Henrys
By Michal A Daly

Principles to build sw and tools with:

- Each tool uses standard connections
- Each coponent tool does one job
- Only one system makes changes at the end
- Shared state - Easy to cmpare what is running with what shuld be running
- Services with single responsibilities - no more building things on top of things
- all new code with regiorously enforced standards

Basicaly pet vs cattle applied to sw pieces

------------------------------------------------
## Seventh Talk: Cmprehensive Infrastructure Automation
By dinesh - suzieq (?)

If you don't have a desgin of the framework you want to build and go straight into building tools
you will soon hit a wall of bricks.
What needs to happen is have an idea of the overall framework for the whole picture (don't just
focus on pieces of it like troubleshooting, config generation, etc..)

Configuration is small part of the daily job

You need a Signal Driven Workflow that:
- covers network lifecycle (Design, Build, Deploy, Validate and Opoerate)
- each step can be further decomposed into individual blocks each of which can be automated

A signal could be anything that the business could be interested in (e.g. a specific query about how many vlans have 4+ mac addresses)
You need to match the signal to **Workflow** that needs to be done (based on the task). 
The workflow is then made of tasks, each of which can or can not be automated.
The entity that matches signal and workflow is the: **signal correlator**

We also need to build common vocabulary so taht when people talks about something everybody means the same thing
e.g. is the source of truth really a SoT or more a source of data? (the devices are the actual SoT)

Then we need to use **reusable and composable building blocks**


**motto**: **We shape our tools and thereafer our tools shape us** so be very **careful!!**

------------------------------------------------
## Eigth Talk: 
