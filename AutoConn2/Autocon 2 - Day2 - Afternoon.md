# Autocon 2 - Netwok Automation ( 21/11/2024)

Side notes for multicast graph: 
 - https://github.com/optiz0r/ansible-multicast-graph and https://blog.ipspace.net/2017/12/create-ip-multicast-tree-graphs-from/
 - check gojs.net for graphic representation in js

## Afternoon session

### Talk 1 - Automated Doc Generation
By Jose Miguel Izquierdo (Juniper) based in Madrid

**Challenges:**
- time-consuming
- prone to human error
- inconsistent across interations and projects
- difficulty in maintaining version control


**Motivations:**
- Standardization: make it part of the process (document as code)
- Consistent look & feel (doesn't matter who is the author)
- Tracking control
- change Management
- reusability
- integration

**Solution:**
This is about combining different tools:
- MarkDown  
  It's a lighweight markup language quite simple overall (very potable results)

- Mermaid  
  Diagram as code: it's simple and dyanmic and apparently easy to learn
  Version control friendly and it integrates with markdown 
  ```mermaid
    flowchart TD;
    A[Start] --> B[Process 1];
    B --> C[Process 2];
    C --> D[End];
  ```

- **PlantUML**  
  Another tool for Diagram as Code  
  it does require a server that can be deployed as container and vscode extension to point to the server
  ```
  docker run -d -p 8888:8080 plantuml/plantuml-server:jetty
  ```
  Again simple and dynamic, easy to learn and adapt (older then marmaid)
  Verion control friendly (more types of diagrma than mermaid)
  
  ```plantuml
  @startuml
    class Example {
      - String name
      - int number 
    
      +void getName()
      +void getNumber()
      +String toString()
    }
  @enduml
  ```
  With docker container you also need to enable preview of local non secure content but you can also point to https://www.plantuml.com/plantuml 

- Jinja2:  
  Used to generate text artifacts.. No need to add any explanation here..
  Of course you can use jinja2 to generate the diagram

- Ansible:  
  Used to render Jinja2 and collect data

- Docker / Jenkins / Git

- Pandoc
  Universal document converter, we can switch from markdown to pdf to word and html etc..
  Very flexible
  
- Latex:
  Used to specify formulas, layout, fonts,etc.. it can produce very high quality output

- AI: well you can submitt all your stuff to an AI and ask them to create docs but how standard is that going to be?

#### How does this all come together?

**Workflow1:**  
We use jinja2 templates (Markdown and code blocks) and ansible to collect data and render Markdown and Graphs

The process can be triggered by a merge request every time you make changes to data file, e.g. 
Assume you have in code the config of a colo and uplinks..
you create a PR to change an uplink, when merged automatically new documentation is generated (and possibly uploaded to confuence for instance)

**Workflow2:**  
Using the same workflow (different templates) we can automatically generate markdown documentation based on pre/post checks and 3rd party
like Grafana, Robotframework, etc..
The document generated can then be sent via email or attached to jira


**Notes:** It might be nice to create a diagram for each colocation for the physical interconnections

---------------------------------------------------
### Talk 2 - Infrastructure automation with Pliant (sponsor) 

If you have too many or too few tools you are not going to be successfull.
Too few tools might not cover all the aspects required while too many tools might create overlapping and complexity in how they are used and why.

The sweet spot seems to be around 5 to 6 tools overall

Pliant gives a UI to orchestrate automation with Low code/no code approach. The platform injest API and trnsforms in drag and drop objects
so tht they can be combined in an easy way. this can include:
- open ticket in JIRA
- make changes to devices
- query some DB state, etc..
- run custom scripts

The goal is basically to reduce the skill levels required to write automation


---------------------------------------------------
### Talk 3 - Everything Everyhere All at Once
(Cut short because of technical issues)

It seems we need to know eveything of our devices everywhere on demand.
The tool:

>> gather

has been defined as a simple command line utility that multiplexes the output of show commands to get tha result

It's basically netmiko with multi-thread and the idea is to gatehr data as fast as possible and insipred by cisco cmd utility

it basically queries a lot of devices t the same time..

Because it saves everything in a simple text file, you can use the unix paradigm and combine the result with other unix tools
e.g.
- grep
- count
- sort
- find uniq elements
- text and column formatting with sed and awk
- etc..


Note these text files are pretty big.. millions of lines..

---------------------------------------------------
### Talk 4 - Network Whisperer
Building the Ultimate AI network Agent
This is about using natural language to query a chatbot to get information about the network

An agent is an application powered by LLM with  a predefined system prompt

Has a set of tools which are self contained functions designed to perform specific tasks
There are however some requirements (picture of Network Agent Requirements)

In the end this presenation is very similar to the Agent presented during the first workshop
it uses the streamlit framework with a set of tools and it applies to an AWS account


---------------------------------------------------
### Talk 5 - The human factor of using LLMs in network operations
By Phillip Gervasi (Kentik)

This is an intro to LLM (for the moment)
LLM don't really understand the context of a chain of words (e.g. humor and innuendos)
however Transformr model can capture longer range dependencies in text (i.e. the context)
They are still a probabilistic approach but they give better result.

Problems stil presents with Transforme Models and LLM:
- Hallucinations
- Real time telemetry data
- Handling diverse data type sources, etc..
- Privacy and regulatory concerns

The solution is to keep humans in the loop involved in training, overlook/correct hallucinations, design architecture etc..

In  summary:  
LLM can help anyone query large diverse and even real-time datasets quickly and easily

Benefits:
- Reduce of manual clue-chaining and root cause analysis
- Get insight w couldn't otherwise se (due to  lack of ability, skill, time, etc..)
- Potential for a more autonomous NetOPs workflow

**What is one easy way to get started?**  
- Drop you information into the prompt with your questions (note LLM have a limited on the number of tokens they can get/parse.. 
  it's retty big.. aroung 100K but it won't get full logs and configs of everything)

- Use the LLM to generate your queries

- Use an LLM in a RAG system with a vector Database
  See picture Use an LLM in a RAG syste with a vector database

A bit more complex but useful is to fine tune your model (llama?) with your own network domain information
This will take some time but not too much but it will also require a very high amount of data
(but again what data?)

Finally you can also:
- combine RAG and fine tuning with RAFT
  Have a look at: https://www.superannotate.com/blog/raft-retrieval-augmented-fine-tuning
- Use Agents and LLM together
  The agensts use the LLM to understand what to do

**How to get start right now**  
- Download Ollama 
- Go to Huggingface.co and downaload a smaller modele (like Llama 3.2) or whatever suits your fancy
- Sign up for and/or download a free vector database like chroma (local) or the free version of Pinecone (hosted) to use for RAG
- Use a programmatic workflow frameworks like LangChain to ties pieces together
- Use Streamlit to make a quick and easy webapp 
- Go and check out Amazon Bedrock or Azure AI studio for an easy way to build an LLM workflow with droopdowns, menus and wizards


