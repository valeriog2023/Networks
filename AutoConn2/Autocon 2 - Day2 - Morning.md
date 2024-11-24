# Autocon 2 - Netwok Automation ( 21/11/2024)

## Morning session

### Talk 1 - The art of automating the automation
Paypal infrastructure automation

Infrastructure is Hybrid Multi cloud, Multi BU, Multi Vendor Network
Global CDN with commercial CDN providers

4 major areas:
- CDN network
- DC-Clos
- Public cloud
- global backbone
and overall Network security that encompass them all

Automation is different based on which area is covered

Challenges:
- increasing automatino needs
- security of the tools
- feature gap between different areas
- small tams and limited budgets
- all needs were due yesterday
- growing demand for self service tools

Need for a framework to generate applications with modular components:
For instance:
- you have components that handle the UI or the DB connection or the access to devices, a deployment model, etc..
- you describe them with meta parameters (in json) 
- you can model your application in terms of the components it needs.

The application can now be described as a set of (dockerized) components and it can be automatically **created**

**NOTE:** this idea is not new in software development, e.g. android applications are built like this and AWS also
offers a way to automatically create application from pre-existing components

**NOTE2:** the guy however has a team of 30 software developers just dedicated to network automation

--------------------------------------------------
### Talk 2 - Itential Session (sponsor)

Why network automation is not taking off?
There's a lt of tools around but it seems things don't really change

Age of Progress:
- Ansible
- Netmiko
- OPenconfig
- nornir
- tailf (?)

How Itential delivers: (see pictures)
pretty empty talk though.. not much details on actual stuff

--------------------------------------------------
### Talk 3 - Intent-Based MPLS Router and WAN Provisionin
By Matthew Deibel

Journey of network automation:
- manual - cli
- semiautomated - scripts and rules-based management
- software defined - a software abstraction of thenetwork infrastructure
- automation centri: Automating provisioning, configuration, deployment and orchestration
- Intent based - automated actions that keeo the network aligned to the intent

This is similar to what we were doing.. have data inside a "source" and then use it to generate config
main differenc is that they give it a UI so that it could be accessed more easily

How do you translate the benefits of network automation into a leadership/business metric?
- Data quality
- imporve employee morale and engagement
- process efficiency
but still how do you get to a money figure? the question remains..

------------------------------------------------------
IP FABRIC shows multicast exactly as we want might be 
worth to arrange a demo in London
Look for demo at ipfabric.io


------------------------------------------------------
### Talk 4 - test the network
By @devnetdan Cisco Press Author // Cisco pyATS

If you don't have a test environment there is a lot of pressure and lack of confidence and 
people want to be absolute sure before starting  actually testing.

You can use automation to:
- run read only tests to ensure the network is operating properly
- push configuration (business perspective this makes more sense)

Benefits of NEtwork testing:
- Minimal Risk (extract data only)
- Wealth of data (Network is just data)
- Assurance (Network is running as expected/Regression testing)

Different types of tests (adapted to the network world):
- unit tests: 
  - local tests, ex (check network features are configured)
- integration teststing
 - how multiple systems interact (check routing tble and other connectivit)   
- endd-to end teting
  - how the complete system interacts
    (use ping traceroute etcc..)
- regression testing:
 - check weather a new feature breaks/degrades the system
   run validation tests before and after a networks change    


Ideally a snapshot is a normalized data model consisting of network operational and configuration data

Snapshot Data Collection:
- CLI Scraping + Parsing
- API (RestAPI, GraphQL) but also Restconf, netconf, gNMI
- Open source Tools Examples
  - NSOT: Netbox, Nautobot, Infrahub
  - Observability: Suzieq
  - Configuration analysis: Batfish

#### Python testing Framework:
- unit test (part of the standard library)
- pytest: external (but better) and extensible with plugins
          include NUTS (Network Unit Testing System)
          Disatvantage: it requires you to do things by yourself (connect to devices, collect data, parse it etc..)
- Cisco pyATS:
   Batteries included network testing fraework
- Arista Network Test Automation (ANTA) Frameweok: apparently very impressive

**Pytest:**
- assertions: pass/fail results
- Markers: Uses tag to customize test behaviours, e.g. it allows to skip a test based on the result of another test
- Fixtures: allows to share context among different tests (e.g. first test creates a DB connection and then it's reused in all the ther tests)
            It can also be used to create mock data for tests
- Parametrization: Loop through multiple paramters set; you can feed to the same test multiple set of parameters to see how it behaves

**PyATS:**
- You have everything baked into the library (and it's vendor agnostic)
- Testbed - Network topology
- AETest infrastructure - testing Framework
- unicorn - device connectivity
- pyATS Library (exGenie) - Data Parsing
- Easypy: run time environment

**Success stories:**
Fixtures were used to collect network data and return nornir objects that were then reused
Pictures taken..

--------------------------------------------------
### Talk 5 - Open TEXT (sponsor)

Customer Problem (see picture) came up from a major outage (Firewall updaed with a deny rule for 0.0.0.0/0)
solution was automated process with safeguards

The morale is that, the team were struggling to find a list of things they wanted to automate but the incident
was an obvious chice that they were overlooking

Yes but, what do they actually do??

**CloudmyLAB** can be used to create a digital twin or a network lab, good for POC and you can use it with Open-Text non-production license



--------------------------------------------------
### Talk 6 - Building a business case for Automation
Using infromal channels by william-Collins

Picture bycicles vs Trains

Picture of building Orgaization influence
--> Target is at least VP level
    But how do you get buy-in? Apparently the Cloud team is a good starting point and partner with them
    Note: the cloud team does not linke the network team because they are slow in running changes

    A second team that usually has budget is Security so also good to partner up with them (they are usually also slow)

    Once you have champions for these teams agreeing on what to do you can start work your way to managers and directors


Also important to:
-  learn how to speak the language of the leadership: spreadsheet, Budgets, ROI, Compliance, etc..
-  learn story telling with compelling story
-  find/create an opportunity

