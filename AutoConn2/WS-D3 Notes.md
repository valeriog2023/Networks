# Autocon2 Workshop WS:D3 - Network resiliency with Event Driven automation using Ansible

## Section 1

### Ansible Lightspeed
Lightspeed is gen AI to generate ansible content
- visual studio extension
  - from vscode you have to log into the lightspeed service
    This is part of the Ansible plug in
     you need to enable lightspeed in the workspace, connect and authorize
- AI works on BM watsonX code assitant 
- it creates a plan first and if it looks good it sends the plan to the LLM 
  to create the actual tasks

### into to ansible plays
Nothing new here..

- Tasks modules are specified in the syntax: `<vendor>.<collection>.<module>`
  the module actually matches a python file inside the collection
- collections is a way to package modules, roles, plugins, playbooks, etc..

NEtwork automation compared to server automation has a big difference.
Server automation sends and executes the code in the node and the controller fetches the result
for Network automation, he connection is contorlled via ansible_conenction
which is likely set to `network_cli` or `netconf` or `httpapi`



**Ansible navigator** is a command based tool for creating, reviewing and troubleshooting Ansible content. This includes inventories, playbooks, and collections.

In the following challenges ahead you will use ansible-navigator to run Ansible playbooks.

`ansible-navigator run playbook`
has 2 modes:
- textual mode and stdout mode

Ansible navigator comes with an interactive mode by default that allows you to explore the different options. Within this lab, we set the mode of ansible-navigator to stdout.

Go to the terminal tab and switch to the autocon2_aap_workshop directory (if not already there) and run the following command to get a listing of what is available within our inventory

Now you can use ansible-navigator
```
ansible-navigator inventory --list
```
this starts a textual interactive mode where you can check groups and hosts (in this case..)
It's actually pretty cool.. yu can deep dive into the host and theri vars or into the groups etc..

note the settings for ansible navigator are these for the lab
```
---
ansible-navigator:
  ansible:
    inventory:
      entries:
      - /home/student/autocon2_aap_workshop/hosts
  execution-environment:
    container-engine: podman
    enabled: true
    image: autocon-ee:latest
    pull:
      policy: never
  logging:
    level: debug
    file: /home/student/ansible-navigator.log
  playbook-artifact:
    save-as: /home/student/playbook-artifacts-autocon2/{playbook_name}-artifact-{time_stamp}.json
```

To create a playbook with Lightspeed you need to:
-  select the Ansible icon on the left and Get Started under the Ansible Creator    
   Panel and select: `Playbook with Ansible Lightspeed`
- provide a description of what the playbook should be doing and click analyze   
  - review the suggested steps after the analysis and then click on create playbook
  for instance:
  ```
  [description]
  "Configure a login banner on Cisco IOS with the text "First banner with Ansible"Configure a login banner on Cisco IOS with the text "First banner with Ansible""  Edit

  [playbook generated]
  ---
  - name: Configure a login banner on Cisco IOS
    hosts: cisco
    gather_facts: false
    tasks:
      - name: Configure a login banner on Cisco IOS
        cisco.ios.ios_banner:
          banner: login
          text: First banner with Ansible
          state: present
  ```  

  You can use navigator lso to test run your playbook
  ```
  ansible-navigator run playbooks/banner.yml --mode stdout
  ```
  This will:
  - setup a runner in podman 
  - execute the playbook
  - present the result

  (to be fair this is basically the same as to run the playbook locally except that navigator will run it in the configured evironment)

  If you just type **ansible-navigator** you will see a textual menu with all the options/functions that navigator supports
  As exapmles:
  - check the doc of a plugin e.g. type: 
    `:doc debug` or for non integrated modules `:doc cisco.ios.facts`
  - check the inventory
  - check ansible configuration
  - review application logs

  we can use navigator to run the playbook in non mode stdout:
  ```ansible-navigator run playbooks/facts.yml```
  this will create a textual menu and show the results on the hosts (provide summary)
  you can also deep dive and see stats of each tasks (using the numeric value associated)


### Resource specific modules
Netowrk automation has 4 types of modules: commands, facts, confgis and resource 
It is suggested to use resource specific modules if they are available
these are the modules taht take care of specific subsets of configuration..
e.g. vlans, or access-lists, interface ip, etc..

The modules are usually generic so juniper interface module will take the same input as the cisco interface module so single resource model is possible

Resource modules have different states:
action states
- merged
- replaced
- overridden
- deleted

non action
- gathered
- 

you also get enhanced resource return values onc the command has run

the gather_facts will also get the facts in the same format that the resource module will need



```
---
- name: Publish SoT to Github repository
  hosts: localhost
  gather_facts: false

  tasks:

    - name: Retrieve a repository from a distant location and make it available locally
      ansible.scm.git_retrieve:
        origin:
          url: https://github.com/<your Github username>/autocon2_aap_workshop
      register: repository

    - name: Copy SNMP SoT files to temporary repository
      ansible.builtin.copy:
        src: "/home/student/autocon2_aap_workshop/"
        dest: "{{ repository['path'] }}/"
        mode: "0644"

    - name: Publish the changes to Github repo
      ansible.scm.git_publish:
        path: "{{ repository['path'] }}"
        token: "{{ lookup('ansible.builtin.env', 'GH_TOKEN') }}"
```

Resource modules have a simple data structure that can be transformed to the network device syntax. In this case the SNMP dictionary is transformed into the Cisco IOS-XE network device syntax.

Resource modules are idempotent, and can be configured to check device state.

Resource Modules are bi-directional, meaning that they can gather facts for that specific resource, as well as, apply configuration. Even if you are not using resource modules to configure network devices, there is a lot of value for checking resource states.

The bi-directional behavior also allows brown-field networks (existing networks) to quickly turn their running-configuration into structured data. This allows network engineers to get automation up running more quickly and get quick automation victories.

This structured data can be persisted to a remote SCM using the ansible.scm collection.

# Automation Controller
**Ansible Automation Platform** this looks like an evolution of AWX
the Overview front page presents a summary of hosts, jobs inventory etc..
then there are links to the specific sections (again projects, inventories, jobs, etc..)
At the bottom of the page there are quick start processes guides to do things like:
- Build a decision environment
- Build an automation execution environment
- Create organizations
- Create dynamic inventory etc..
- create a rulebook activation etc..

however it seems that these guided steps requie a license?!?!
 ---> valid Ansible Automation Platform subscription
      You can however sign up with a developer license (developer portal)

 AWX is just one component of the automation platform
 
 Private Automation Hub is  away to host content collection on premises but to be fair.. you can keep them in git and install them manually
 however the Private automatino Hub can sync with galaxy etc..

 **Workflows**: daisy chain playbooks


**Note:** Lightspeed can also be used to explain existing playbooks
If you have an open playbok and the go into the Ansible plugin and select ansible Lightspeed
You can see the button: `Explain the current playbook`

# workflows
A Workflow Job Template is a series of connected automation tasks (or Playbooks) that are executed in a specific order to achieve a desired outcome. Compared to an individual Playbook (or Job Template), a Job Template handles straightforward tasks in a single playbook, while a Workflow job template is designed to manage more complex automation scenarios involving multiple playbooks (or Job Templates) and decision-making processes.

You first create a job workflow but it's basically empty
That leads you to the visualizer where you can add single job templates
we create a first step as follows:
```
Node Type: Job Template
Job Template: Configure BGP
Convergence: Any
Node alias: arista-configure-bgp
```
we click finish and we see the new node, then we select the node and add a new step
```
Node Type: Job Template
Job Template: Validate BGP
Status: Run on success
Convergence: Any
Node alias: arista-validate-bgp
```
now save the workflow

# Rule Books
ansible-rulebook relies on a few components. These components all come together to allow you to respond to events and decide on the next course of action. The three main components to the rulebooks are as follows:

- Source - The sources of our events come from source plugins. These plugins define where we are listening for events.
 There are lots of source plugins:
  - Azure
  - file
  - kafka
  - alertmanager
  - etc..

- Condition - The conditional statements in the rulebook allow us to match criteria on which we want to have some kind of response to.

- Action - Lastly, the action is our response once the condition has been met from the event source. This can be to trigger remediation, log a ticket for observation or generate other events which we would want to respond to.

webhook source rule example
```
# code: language=yaml
---
- name: Listen for events on a webhook
  hosts: all
  ## Define our source for events
  sources:
    - ansible.eda.webhook:
        host: 0.0.0.0
        port: 5000
  ## Define the conditions we are looking for
  rules:
    - name: Say Hello
      condition: event.payload.message == "Ansible is super cool"
  ## Define the action we should take should the condition be met
      action:
        run_playbook:
          name: playbooks/say-what.yml
```

you execute the rule books as follows:
```
ansible-rulebook --rulebook rulebooks/webhook-example.yml -i hosts --print-events
```
Note that:
- the print events is optional but it helps to identify what events are seen
- when running, the rulebook basically hangs waiting for events
- ansible.eda.webhook is a red hat collection

To trigger the even we run:
```
curl -H 'Content-Type: application/json' -d "{\"message\": \"Ansible is alright\"}" 127.0.0.1:5000/endpoint
```
this calls the webhook that we use as a source and becuase the conditions are met, the rulebook runs and executes the playbook

A second example is by listening to a kafka topic, see kafka-example.yml
This time we triger it by produing a message in the kafka topic:

```
kafka-console-producer --bootstrap-server broker:9092 --topic eda-topic

{"message": "Ansible is good"}
```

Event data is automatically passed to the Ansible playbook. Try sending another message specifying sender with your name from the kafka tab.
so the message
```
{"message": "Ansible is cool", "sender":"YOUR NAME"}
```
will pass sender to the playbook executed. Note that the play needs to account for the var which in this case is:
```
Thank you, {{ ansible_eda.event.body.sender | default('my friend') }}
```
more on rulesbooks:
https://ansible.readthedocs.io/projects/rulebook/en/stable/

You can of course have rulebooks in the automation controller
Just like Automation Controller has resources needed for job template execution, Event-Driven Ansible Controller defines resources needed for execution of rulebooks. There are three main resource types that have to be defined before creating a rulebook activation that will listen for incoming events.

### Decision Environments
These are like Execution Environments.
They are built to contain tools to execute playbooks. Both are container images that contain all the resources needed to execute rulebooks/playbooks.

Decision Environments are also built with collections that contain the source plugins for any source you want to receive events from. This means that if you'd like to receive events from Dynatrace, for example, you would have to install the collection dynatrace.event_driven_ansible in order to leverage the source plugin for Dynatrace.

### Credentials
 is one of the components required by the Rulebook execution
 you have private repositories for either Decision Environments or Projects, you can create a credential from Automation Decisions > Infrastructure > Credentials on the left-hand side of the AAP tab. By default, a Decision Environment Container Registry credential is added at installation time. There is also another credential called AAP which was pre-loaded into the AAP instance for this workshop. This credential will be used at the for Rulebook Activations in upcoming exercises.

### Projects
Projects are really just like they are on Automation Controller (under the Automation Execution heading). These projects represent source control repositories that contain your rulebooks.

### Example setup
check https://github.com/ansible-network/autocon2_aap_workshop

. Setup a kafka topic:
/bin/kafka-topics --bootstrap-server localhost:9092 --topic network --create --partitions 3 --replication-factor 1

. configure cisco device to stream telemetry
  a playbook does this and we check that it connects to telgraf with:
  `show telemetry connection all`

. verify telegraf configuration

```
############################################## CISCO 8000V  #############################################
[[inputs.cisco_telemetry_mdt]]
#  ## Telemetry transport can be "tcp" or "grpc".  TLS is only supported when
#  ## using the grpc transport.
  transport = "grpc"
#
#  ## Address and port to host telemetry listener
  service_address = ":57000"

############################################## OUTPUTS  ####################################################

[outputs.kafka]
# URLs of kafka brokers
  brokers = ["broker:9092"] # EDIT THIS LINE
# Kafka topic for producer messages
  topic = "network"
  data_format = "json"

~                                
```
so I didn't really receive any message when configuring the cisco..
anyway let's proceed

. configure a new Decision section
Go to the AAP tab. In the Automation Decisions section, choose Projects and click on Create project button.

. setup a new rule book: n the Automation Decisions left sidebar menu, click on Rulebook Activations
  ```
  Name: Cisco Telemetry
  Organization: Default
  Project: Autocon2 Rulebooks
  Rulebook: kafka-interface-rules.yml
  Credential: AAP
  Decision environment: Autocon2 Decision Environment
  Restart Policy: Always
  Log level: Info
  ```

The kafka-interface-rules.yml uses the ansible.eda.kafka source plugin to listen for events from the Kafka topic called network that we created in the previous step. 

The Cisco router will forward the telemetry data to Telegraf, which will receive it using the cisco_telemetry_mdt input plugin, decode it and write it to the network topic.

This rulebook has a single rule named Retrieve Data and Launch Job-template which looks for an event signifying that an interface went down. 

Once this rule is matched, the job template EDA-Fix-Ports will be launched and EDA will pass the name of the affected interface as an extra variable to it.

Note: This job template hasn't been created yet, we will create it in the next step.
```
- name: Look for interface shutdown events and remediate
  hosts: localhost
  sources:
    - ansible.eda.kafka:
        topic: network
        host: broker
        port: 9092

  rules:
    - name: Retrieve Data and Launch Job-template
      condition: events.body.fields.new_state == "interface-notif-state-down"
      action:
        run_job_template:
          name: "EDA-Fix-Ports"
          organization: "Default"
          job_args:
            extra_vars:
              interface: "{{ event.body.fields.if_name }}"
```

You see actions generated by rule books in rule audit where you can check:
- the event tab
- the action tab