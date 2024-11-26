#  AUTOCONN2 - WS Generative AI and how to use it for network troubleshooting (18/11/24 Morning session)

- Tomasz Janaszka
- Adam Kulagowski
- Monika Antoniak

Lab guide https://dub.sh/ws-a1

Networks Chat Assistant

The bot works as a container with a  web interface: registry.digitalocean.com/ac2-registry/net-chat:latest

How is it connected to the LLM engine?
Have a look to https://www.docker.com/blog/build-and-deploy-a-langchain-powered-chat-app-with-docker-and-streamlit/

## Gen AI
learns patterns from large amount of data
generates new, original content (inline with the original content)
In particular, LLM:
- natural language understanding
- text generation
- summarization
- contextual assistance across a wide range of topics and tasks
- etc..

Note that summarization is pretty important because you can give it a bunch of data (logs) and get the key points ofw what happened

### Chatbot, copilot, agents
- chatbots are focused on providing answers and conversations
- copilot provide recommendations 
- agents can perform task autonomously (without human guidance)

### how does GenAI support network operations
- speed up documentation, give it to AI
- make it easier to get information
- suggest configurations (or fixes)

How to help troubleshooting?
this is mainly for junior staff and help them understand the situation while senior staff is busy with other projects

#### AI Allucinations
sometimes AI assistnant will get unreal content, i.e. realistic configurtion but not real e.g. you can ask how to configure EIGRP on juniper (which is not supported). You will get an answer that looks correct but the AI knows EIGRP is not supported..

We are going to use: 
### 1 LLM (gpt-40-mini)
advanced AI system designed to understand and generated human-like text
- quality/price
- context window
- output

### 2 LangChain (v.02)
framework for building applications powered by LLMs
enablsing seamless integration with various data sources, tools and workflows
- agents (ReAct): registers tools and cooperates with LLM
- coopertion is based on prompt templates
- data augmentation

### 3 Streamlit (v1.37)
Python framework designed for rapidly build web applications
abstracting away the complexity of a typical frontend-backend seratation:
- perfect for PoC
- easy development
- GenAI componennts


For the network part we use:
 . Container Lab (GNS3)
 - FRRouting (IP routing suite with plenty of protocols and cisco like shell)
 - VyOS (fully blown NOS), can be run in container with few tweaks ans Juniper like shell

 ## NET CHAT Assistant
 How does it work?
 
 <solution overview picture>

                                     Netdev write script with human readable
                                                 Output
                                                    |     
                                                    \/
 USer <--->  LLM ( App + GenAI Platformm ) <-----> Scripts
                     |
                     \/ 
                decide which script to runs
                and provides the output to the 
                user    
                     |
                     \/
                Runs the script on the network      

### Prompt Augmentation
Dynamically extending the context (i.e. our network data)

The result of each script is sent to LLM to enrich the context

Support Function calling, if it is supported by the LLm, the LLM can tell which tool can be sued to extend the context



### Prompt augmentation by ReAct Agent

1) input Question -> Prompt Template <------------------------ Tempaltes are bundled with tools

2) Input Question + Prompt Tempalte --> generates the Actual Prompt that goes to the LLM (together with the tools)

3) the LLM returns a 
   thought and Action which includes the execution of a tool

4) The tool execution returns data which is recorded in an Observation  
   This Observation is feed back into the prompt template and the cycle can restart 

Note: the prompt becomes bigger and bigger as it incorporates more information
      and of course this needs to fix in the context window size, so you can't just submitt millions of logs etc...


#### Prompt template:
we have the following sections:
- HEADER
- TOOLS
- How TO specify TOOL: how to specify tools and their parameters
- FORMAT: how the LLM should format its reponses             
- Additional instructions: e.g. avoid loops in proposing consecutive actions/tools
- Human query
- scrathpad      

**OVERALL THIS BECOMES AN EXERCISE IN SELECTING THE CORRECT TOOL/TOOLS, RUNNING IT AND PRESENTING THE RESULT IN A SPECIFIC WAY**


ee6Ahtof


### Adding a tool
A tool is not a script but it's all Python
Tools are script that are registered in the agent

Scripts need annotaion: @tool from the langchain  fraamework

Python script:
- docstring: description is compulsory
- args: (typing) is required and description of the argumetns
- code 


@tool
def show_version(host: str) -> str:
    """
    <docstring>

    Args:
      host (str): ...
    
    Returns:
      

    """

Now we need to register the script in the agent


agent = initialize_Agent(tools=tools,
                         llm = llm, ..) 


### Proper tool development
you can have a single tool that performs multiple operations or multiple basic tools
that do basic operations
e.g. 
- identify device type
- identify proper command
- run the command and get the output

these can be both single tools or a single tool
if they are a single tool, it will reduce the number of llm agent interaction 
and save on cost and be faster

Note that the description and the element yu put in the docstring are used by the llm 
gramework to select the proper tool so they need to be detailed 

A real problem is the size of the prompt as it has to be limited 