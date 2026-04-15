***2***

*Building Your First AI Agent*

**This chapter covers**

- Turning LLM calls into reasoning loops

- Understanding core agent components (messages, tools, memory,
  artifacts)

- Defining a framework-agnostic Minimal Agent Spec

- Implementing the spec in LangChain and AutoGen

- Adding safety and human-in-the-loop controls

In Chapter 1, we introduced the concept of AI agents and pipelines and
how they create systems that bring reasoning, control, and
accountability together to automate and streamline offensive security
workflows. A pipeline relies on smaller units of intelligence consisting
of AI agents that are capable of interpreting context, invoking tools,
and recording decisions. This chapter shifts from introducing concepts
to implementation by building your own AI agent.

We'll first define the core components that are essential to building
single-agent systems, including messages, tools, memory, and artifacts.
We'll show how wrapping an LLM inside these structures transforms
reactive text generation into a governed decision-making system that can
act autonomously. Then, we'll start building these pieces ourselves,
coding agentic components from the ground up while creating adapters
that let us extend our code to LLM frameworks like LangChain and
AutoGen.

Once we establish the foundation for building an agent, we'll discuss
essential AI governance topics and guardrails that ensure the safe use
of these agents. This includes setting up a sandbox environment,
incorporating safety gates for human validation, and creating kill
switches that will stop agents if they deviate from the intended path.
Any security professional must effectively utilize guardrails and safely
integrate AI into security systems, particularly since cybersecurity is
a high-stakes operation with significant financial, legal, and
reputational implications.

Finally, we'll apply everything we have learned up to this point to
build a triage agent, which can help you prioritize security alerts,
incidents, or vulnerabilities in your own workflows. By the end of the
chapter, you will be able to build single specialized agents that can
automate specific workflows in a safe and controlled manner.

1.  What is an Agent?

An *agent* is a single, contained pipeline powered by a large language
model (LLM): it gathers input data, reasons and creates plans, acts with
data and the environment through a tool, observes the result, reflects
the successes and failures of its actions into memory, and writes these
outputs as an artifact. Agents empower security professionals. They
enable autonomous task execution, can respond in dynamic environments,
and can operate 24/7 --- this is essential to protecting modern software
systems that are prone to malicious attacks.

Individual agents are highly capable of conducting single-stage security
operations, such as reconnaissance and triage. As we make our agentic
systems more complex, it becomes more important to store the results as
artifacts, which are JSONL, markdown, and other files containing
structured information about how an AI agent responded. Later, when
multiple agents are chained together to run complex workflows, those
artifacts become the interface between stages (described further in
Chapter 3). It's worth pausing here to clarify how an agent differs from
the large language model (LLM) that powers it.

**[DEFINITIONS]{.smallcaps}** A Large Language Model (LLM) is a
text-prediction engine that is trained to generate a response that is
associated with a textual input. By default, LLMs only generate text,
have no memory between API calls, respond to single prompts, and produce
only one output per input. In contrast, agents are autonomous systems
that use an LLM as the "brain", but add additional capabilities for
perception, memory, planning, interactions with the environment, and
actions that lead to achieving a goal. Agents have memory and can
remember context across multiple interactions. They can also utilize
tools, which are resources that an LLM can leverage to expand its
capabilities, such as custom functions, APIs, databases, MCP servers,
and more. Agents possess reasoning capabilities and can break down
complex, multi-step plans, iteratively working towards objectives
without human guidance. Finally, agents operate in a feedback loop --
they can perceive → reason → act → observe, and repeat until the goal is
achieved. In summary, agents are pipelines that extend the capabilities
of LLMs to operate autonomously.

Now that we've distinguished the reactive LLM from the reasoning agent
that surrounds it, we can examine how that agent actually works. The
following section breaks down the agent loop into five essential
components: the messages, tools, memory, controller, and artifacts that
make up the agent loop.

2.  The Anatomy of An Agent

An agent is a structured loop that connects five core components,
enabling agents to perform complex tasks, including reasoning, action,
observation, reflection, and recording. Figure 2.1 shows a schematic
representation of a single agentic loop. By iterating through these
components, agents can do things that were previously reserved for
humans only.

![A screenshot of a computer AI-generated content may be
incorrect.](media/image1.png){width="5.25in"
height="3.419368985126859in"}

Figure 2.1. An AI agent workflow consists of 5 steps that are iterated
until they converge to a desired outcome: 1) Reason → Use the LLM to
plan a step. 2) Act → Execute that step with a tool. 3) Observe →
Capture the result. 4) Reflect → Update memory and decide again. 5)
Record → Write everything to an artifact.

2.2.1 Core Components

AI agents comprise five key components summarized in Table 2.1:
messages, tools, memory, agents, and artifacts. We describe these
components in more depth below.

Table 2.1. Core Agent Components

  --------------------------------------------------------------------------
  Component   Role                  Typical Artifact     Why It Matters
  ----------- --------------------- -------------------- -------------------
  Message     A single              { \"role\":          Structures
              communication unit    \"system\",          reasoning history,
              between the system,   \"content\":         and makes loops
              user, and model.      \"Analyze scan       reproducible.
                                    results\" }          

  Tool        An external           Function handle, CLI Turns reasoning
              capability the agent  command, or REST     into measurable
              can call---scripts,   call                 action.
              APIs, scanners.                            

  Memory      Storage for past      Conversation buffer  Provides context
              messages, results,    or vector store      and continuity
              and summaries.                             between steps.

  Agent       The controller that   Plan object or       Transforms model
              determines *the next  next-action list     predictions into an
              action*.                                   intentional
                                                         workflow.

  Artifact    The durable record of JSONL log, Markdown  Enables auditing,
              what happened.        report, database row replay, and
                                                         defensive analysis.
  --------------------------------------------------------------------------

*Messages* are a structured unit of communication within a conversation
between the user and the LLM. They are the building blocks that form a
prompt, which are the input you send to an AI model to get a response.
It's usually a question or a command, like "List 5 poems Emily Dickinson
wrote". With turn-based interactions (e.g., a chatbot), the prompt is
usually a single message. However, agents typically construct a prompt
from multiple messages that work together.

> **Chain of Thought (CoT) and Reasoning**
>
> In the early days of LLMs, chat models were much more likely to
> hallucinate. In 2022, Google researchers discovered that when a model
> is instructed to break down a complex problem into smaller,
> intermediate steps, it yields more accurate results. They called this
> method *Chain of Thought (CoT)*, and it's so powerful because it
> allows AI models to return more accurate results without incurring
> additional training costs.
>
> For example, consider the following mathematical reasoning problem: A
> cake has eight slices. You give two slices to your friend and two to
> your mother. Your friend gives you back a slice. How many slices do
> you have now? Without CoT, LLMs tended to return randomly generated
> numbers (e.g., 23 slices). However, with CoT, we can break this
> problem up into the following operations:
>
> Start: 8 Slices
>
> You give 2 slices to your friend: 8 Slices - 2 Slices = 6 Slices
>
> You give 2 slices to your mother: 6 Slices - 2 Slices = 4 Slices
>
> Your friend gives back a slice: 4 Slices + 1 Slices = 5 Slices
>
> The answer is 5 slices
>
> CoT is the foundation for AI reasoning. It has had a profound impact
> on AI products, even affecting the user interface, such as the thought
> processes you experience when interacting with a chatbot.

We discussed the differences between LLMs and agents: LLMs can only
respond to simple messages, but they cannot interact with the outside
world. *Tools* enable LLMs not only to converse, but also to interact
with the outside world. They consist of custom functions, API calls, or
database queries that an agent needs to execute in order to complete a
given task. This is important for several reasons: for example, to
retrieve real-time information, an agent needs access to the internet,
as LLMs are limited by the knowledge they acquired during their training
period. Or if you want an LLM to perform a mathematical operation, tools
are great because LLMs are known to hallucinate, especially when it
comes to mathematical reasoning questions. Tools are specialized
instruments that the agent can pick up and use when needed, when they
cannot reason through the task.

As described in the previous section, an *agent* is a pipeline that
receives messages, determines when to utilize tools, accesses memory,
and generates responses. They follow a reasoning loop: understanding the
request, determining what information or actions are needed, calling the
appropriate tools, synthesizing results, and responding appropriately to
fulfill a user's request. It is a decision maker that orchestrates and
coordinates all components to accomplish tasks effectively.

Agents are powerful, mainly because they also consider previous
interactions. *Memory* is the way they retain information across
interactions. Without a memory component, each conversation would start
fresh with no context. Imagine having to copy and paste a previous
conversation to get a relevant response -- that is a terrible user
experience! Memory can be short-term (e.g., the past N number of
messages in the conversation) or long-term -- facts from past sessions
that are stored in a special container called a vector database. Memory
is crucial because it makes an agent feel like a personalized assistant
as you use it over time.

Finally, agents can create *artifacts*, which are tangible outputs from
the model. These include items such as documents, code files, reports,
or charts. Artifacts are typically formatted, saved, and can be
downloaded or edited further by a human (or another LLM). Altogether,
these components form the basis of a modern AI agent workflow.

2.  ***Mental Model: The ReAct Agent Loop***

Figure 2.2 shows how these core agentic components combine to solve the
user's query using the Reasoning and Action (ReAct) agentic framework.
ReAct consists of three main steps in a loop that are executed until a
user's problem is solved.

- *Reasoning*: The LLM undertakes a thought process that involves
  planning, decision-making, and strategic thinking before taking
  action.

- *Action*: The model interacts with the outside world, using anything
  from custom functions to API calls to accessing databases, and

- *Observation*: The model perceives and interprets the results or
  feedback from its actions.

The original ReAct implementation utilized only the Reasoning, Action,
and Observation loop, which limited its performance in real-world
applications. Since then, additional processes have been introduced and
integrated into the workflow to significantly improve an agent's general
performance, including:

- Reflection: The model performs a meta-cognitive evaluation of its own
  performance, which can be used to improve its next steps.

- Recording: The information, context, learnings, logs, and model
  outputs from the session are stored for future reference and
  decision-making purposes.

While it seems simple, ReAct is powerful because it enables LLMs to act
as autonomous agents. The reasoning component grounds actions in reality
and helps prevent hallucinations. Additionally, the loop is flexible. It
enables the AI agent to adjust its plan based on what it discovers. Most
importantly, the agentic decision-making process is transparent,
allowing the user to understand how the model arrived at its decisions.

> **[NOTE]{.smallcaps}** If you swapped out any common LLM framework
> (e.g., LangChain for AutoGen), the ReAct flow would remain identical.
> LLM frameworks differ in minor implementations of the underlying
> abstractions, not in the foundational principles or design structures.

![](media/image2.png){width="5.25in" height="3.5in"}Figure 2.2. The
ReAct Agent Schematic Diagram. 1) The user provides a query to the LLM,
2) The LLM reasons and determines a plan to solve the user's query, 3)
the LLM uses a tool to perform an action that gets the system closer to
its goal, 4) the LLM outputs an artifact, 5) The LLM observes the
result, 6) The agent reflects and updates its memory to return a better
response, 7) We iterate until the goal is reached.

2.  ***Why Structure Matters with Agentic Workflows***

A key question is, why does all of this matter? Why do we need to
complicate a simple LLM API call with all these additional components?
Simple automation systems like LLMs can return responses to prompts
(e.g., Tell me what is the capital of Kansas), but an LLM alone can't
reason about complex user queries, like mathematical reasoning problems
In critical applications like cybersecurity, which carry high stakes and
have legal and operational consequences, we need to be able to trust how
models arrive at their decisions. By connecting an LLM with additional
parts like messages, tools, memory, and artifacts, you make an AI
agent's behavior observable. We can store the LLM's reasoning as an
artifact and visualize the steps it took to reach its conclusion.
Gaining insights into the reasoning process allows us to refine it
further and put in control mechanisms with human intervention.

Transparency into the reasoning process allows security testers to use
AI safely: every decision, every action, every result is logged as an
artifact through telemetry tools, which automatically collect, transmit,
and analyze data. For example, teams can use a tool like LangSmith to
manage LLM logs, metrics, and traces, and track events for enhanced
debugging and auditing.

In later chapters, we'll show how these same components will scale into
full multi-agent pipelines, where two or more agents will coordinate
through shared artifacts and gates.

3.  ***Defining the Minimal Agent Specification (Spec)***

In this section, we'll translate the concepts of a ReAct agentinto code
so it can be implemented in any framework. We'll start by defining the
*Minimal Agent Spec, which is* the smallest set of interfaces and data
structures an AI agent must support to be portable, testable, and safe.

Think of this spec as the API contract that every agent in this book
will obey. We take a framework-agnostic approach for development,
because it provides flexibility and resilience when building agentic
systems. You can swap a framework like LangChain for another one like
AutoGen, LangGraph, or something that hasn't been invented yet, and your
pipelines will still work. The spec ensures that every agent, regardless
of the framework being used, communicates, acts, and logs in a
consistent, auditable manner.

In the book, we will use Pydantic to establish a minimal spec. Pydantic
is a Python-based data validation library that uses type annotations to
define data schemas and automatically validate, parse, and serialize
data. This is important to ensure agents produce predictable, parseable
outputs.

4.  ***Messages and Observations***

A core component of an agent is the message, which is how the user and
LLM communicate. A message's role defines who is speaking in the
conversation. There are four standard roles across most AI frameworks:

- *System*: A system message contains instructions and context for the
  agent, including background knowledge, defining constraints, and
  setting the agent\'s behavior.

- *User*: The human-provided input, commonly containing questions,
  commands, and requests.

- *Agent*: These are AI-generated responses, including the thoughts,
  reasonings, and actions it takes. It can also contain other metadata,
  such as tool calls, analysis, or final answers.

- *Tool*: The results from tool execution. These can include outputs
  from external systems (e.g., APIs, databases, custom tools) and
  observations the agent uses for reasoning.

We define how to set the Message and Observation schemas in Listing 2.1.
The Message class is an object that stores information that is passing
through the agent, and it contains the role, content, the timestamp of
the generated message, and additional metadata that is passed on. The
Observations class captures what happened after an action, and includes
information like the tool name, the model inputs/outputs, error codes if
they happen, and other key information for model monitoring and error
tracing.

Listing 2.1 Message and Observation schemas

> from pydantic import BaseModel, Field
>
> from datetime import datetime
>
> from typing import Optional, Dict, Any
>
> class Message(BaseModel):
>
> role: str \# \"system\", \"user\", \"agent\", \"tool\"
>
> content: str \# natural-language text
>
> timestamp: datetime = Field(default_factory=datetime.utcnow)
>
> meta: Optional\[Dict\[str, Any\]\] = None
>
> class Observation(BaseModel):
>
> tool_name: str
>
> input: Dict\[str, Any\]
>
> output: Dict\[str, Any\]
>
> success: bool
>
> error: Optional\[str\] = None
>
> timestamp: datetime = Field(default_factory=datetime.utcnow)
>
> **[TIP]{.smallcaps}** We recommend that you store your artifacts in
> simple formats that JSON can handle. This means using basic types like
> strings, numbers, booleans, arrays, and objects to avoid complex
> objects that would need special conversions. For the data-centered
> developer, if you are storing your numerical data in NumPy arrays or
> similar objects, these need to be converted to lists. Python objects
> need to be convered to dictionaries. This practice ensures that your
> information can be visualized in logs, dashboards, and other visual
> representations of your data.

***[2.2.6 The Tool Interface]{.smallcaps}***

Tools are how an agent interacts with the world, and it includes
anything from a custom function you wrote (e.g., a regex parser) to an
API call from an external service (e.g., a vulnerability scanner). In
Listing 2.2, we define a schema for the base class Tools, which include
metadata like the tool name, description, and a method .invoke() that
can be used to run any kind of function, invoke an API, or do some other
task.

> **[NOTE]{.smallcaps}** The input and output data formats should follow
> the same schema that was provided in the Observations class we defined
> in Listing 2.1. This is to ensure that we can trace the movement of
> data across different agent modules.

**Listing 2.2 The Tool Schema**

> class Tool:
>
> name: str
>
> description: str
>
> def invoke(self, input: Dict\[str, Any\]) -\> Dict\[str, Any\]:
>
> \"\"\"Run the tool and return structured output.\"\"\"
>
> raise NotImplementedError

***[2.2.7 The PingTool]{.smallcaps}***

In Listing 2.3, we define a tool that runs ping, a Linux/Unix shell
command that allows us to see if another device in the network is online
and reachable. This command is commonly used to see if your internet is
working, if a website is down, and for other diagnostic applications.

**Listing 2.3 An Example Tool: PingTool**

> import subprocess, json
>
> class PingTool(Tool):
>
> name = \"ping\"
>
> description = \"Checks if a host is reachable.\"
>
> def invoke(self, input : Dict\[str, Any\]) -\> Dict\[str, Any\]:
>
> \"\"\"
>
> Ping a target host to check if it\'s alive and reachable.
>
> Args:
>
> input: Dict with \"host\" (str) - target IP or hostname
>
> Returns:
>
> Dict with \"reachable\" (bool) - True if host responds
>
> Note: May return False if ICMP is blocked by firewall.
>
> \"\"\"
>
> host = input\[\"host\"\]
>
> try:
>
> subprocess.check_output(\[\"ping\", \"-c\", \"1\", host\], timeout=3)
>
> return {\"reachable\": True}
>
> except subprocess.CalledProcessError:
>
> return {\"reachable\": False}

***[2.2.8 The Agent Interface]{.smallcaps}***

With messages and tools in place, we can define the Agent class, which
contains the core logic that runs and coordinate the LLM with the tools,
memory, and other decision-making logic.

In Listing 2.4, we provide the skeleton to implement the ReflAct
framework, a variant of the ReAct agent that includes reflection. We
define three methods that would need to be built out further: the
.plan() method that will devise an action plan based on the input
message, .act(), which would invoke a tool, and .reflect(), which would
allow the LLM to evaluate its response and improve its performance.

**Listing 2.4 The Agent Schema**

> class Agent:
>
> def plan(self, history: list\[Message\]) -\> Message:
>
> \"\"\"Generate the next action or reasoning step.\"\"\"
>
> return None
>
> def act(self, plan: Message, tools: list\[Tool\]) -\> Observation:
>
> \"\"\"Execute the planned action using an appropriate tool.\"\"\"
>
> return None
>
> def reflect(self, observation: Observation) -\> Message:
>
> \"\"\"Update internal memory and produce a reflection message.\"\"\"
>
> return None

***[2.2.9 Artifacts and Logging]{.smallcaps}***

> Every agent run produces some data, plans, actions, results, and
> reflections. We treat these outputs as artifacts, and we will save
> them in JSONL (one JSON object per line) format. In Listing 2.5, we
> define the artifact logger class, which saves all of the model outputs
> in the JSONL log. The log file will be stored in the directory
> run_dir. New traces will be appended to this file as a new line.
> Artifact logging is important because it provides an audit trail for
> your agent, and allows you to prove exactly what your agent did during
> any security task (e.g., a penetration test). Logs are essential for
> assessments and debugging. Additionally, from a compliance and legal
> protection standpoint, logs demonstrate that your agent adhered to the
> scope of the security testing project.

**Listing 2.5 Artifact Logger Class**

> import json, uuid, os
>
> class ArtifactLogger:
>
> def \_\_init\_\_(self, run_dir=\"runs\"):
>
> os.makedirs(run_dir, exist_ok=True)
>
> self.file = open(f\"{run_dir}/{uuid.uuid4()}.jsonl\", \"w\",
> encoding=\"utf8\")
>
> def write(self, record: dict):
>
> json.dump(record, self.file)
>
> self.file.write(\"\\n\")
>
> self.file.flush()

We can now look at how to bring these components together into a working
specification that unites messages, tools, and artifacts into one
repeatable loop.

***[2.2.10 Putting It Together]{.smallcaps}***

At this point, we can summarize the Minimal Agent Spec in Table 2.2

Table 2.2. Summary of the Minimal Agent Spec

  -------------------------------------------------------------------------
  **Element**       **Responsibility**               **Example
                                                     Implementation**
  ----------------- -------------------------------- ----------------------
  Message           Encodes reasoning and            Pydantic model / dict
                    communication                    

  Tool              Performs concrete actions        HTTP scanner, PingTool

  Agent.plan()      Chooses next action              LLM prompt → plan

  Agent.act()       Executes plan                    Tool invocation

  Agent.reflect()   Updates memory                   LLM summary of result

  ArtifactLogger    Records everything               JSONL log per run
  -------------------------------------------------------------------------

This small set of rules is all you need to build interoperable agents.
Everything else, including the framework abstractions, fancy
orchestration, and memory stores sits on top of this layer.

With the spec in place, we can bring it to life. The next section shows
how these same components run inside LangChain, so you can see the
reasoning loop in action.

> **Exercise 2.1. Build Your Own Tool**
>
> Write a simple Tool subclass that performs a harmless text
> operation---such as counting words in a string or extracting URLs from
> JSON. Then log the input and output using ArtifactLogger. You've just
> implemented half of a working agent.

1.  ***Implementing the Agent with LangChain***

You now have the blueprint for a framework-agnostic agent. Let's bring
it to life using LangChain, which provides convenient abstractions for
tools, memory, and control loops. LangChain is widely adopted,
well-documented, and supports the same mental model we defined
earlier---plan → act → reflect---so it's an ideal teaching framework.

The goal here isn't to master LangChain; it's to prove that your Minimal
Agent Spec runs as expected in a real environment. By the end of this
section, you'll have a working Triage Agent that can reason about
scanner output, decide which targets look risky, and record every step
for audit.

***[2.3.1 Setting Up the Adapter]{.smallcaps}***

LangChain offers built-in methods and objects that map directly to the
interfaces we just defined (Table 2.3). We recommend creating a small
adapter file that can act as a bridge between the custom code we wrote
and code for third-party libraries like LangChain. Writing additional
adapter code encapsulates our project and ensures we can swap and test
components more easily.

Table 2.3 Mapping between custom data schemas and LangChain-defined
objects

  --------------------------------------------------
  Spec Concept      LangChain Equivalent
  ----------------- --------------------------------
  Message           BaseMessage / ChatMessage

  Tool              Tool class or StructuredTool

  Memory            ConversationBufferMemory

  Agent.plan()      LLM prompt inside a Chain

  Agent.act()       Tool.invoke() via AgentExecutor

  Agent.reflect()   Follow-up LLM call or callback

  ArtifactLogger    Custom callback or Python logger
  --------------------------------------------------

The code below uses several LangChain implementations to initiate an AI
agent. We describe the main parts below:

- We use OpenAI's LLMs for the AI model

- We store the conversation history using the ConversationBufferMemory()
  method. Note that this method stores everything, and so if you expect
  to have a long session interaction, there are other methods that may
  be more appropriate so that you don't run out of memory.

- We use the initialize_agent method to start up the agent. The
  agent_type that is set is the ReAct model for a single turn.

**Listing 2.6 General LangChain Adapter**

from langchain.agents import initialize_agent, AgentType

from langchain.memory import ConversationBufferMemory

from langchain.llms import OpenAI

from langchain.tools import Tool

from core.logger import ArtifactLogger

def build_langchain_agent(tools: list\[Tool\]):

llm = OpenAI(temperature=0.2)

memory = ConversationBufferMemory(memory_key=\"chat_history\")

agent = initialize_agent(

tools,

llm,

agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,

memory=memory,

verbose=True

)

logger = ArtifactLogger()

def run(input_text):

result = agent.run(input_text)

logger.write({\"input\": input_text, \"output\": result})

return result

return run

> [**TIP** Separate Adapters from Core Logic]{.smallcaps}**.** The rest
> of your code should import build_langchain_agent*()* rather than
> LangChain classes directly. This makes swapping to other frameworks
> (such as AutoGen) easily doable with a single line change.

***[2.3.2 Creating Your First Tool]{.smallcaps}***

Let's reuse the PingTool idea from Section 2.2, but write it in
LangChain's format. To create tools with LangChain, we wrap the Python
function with a \@tool decorator to convert it into a Tool object the
agent can call (Listing 2.7).

Listing 2.7 LangChain Ping Tool

> from langchain.tools import tool
>
> import subprocess
>
> \# Tells LangChain this is a tool
>
> \@tool(\"ping_host\", return_direct=True)
>
> def ping_host(host: str) -\> str:
>
> \"\"\"Checks if a host responds to ICMP ping.\"\"\"
>
> try:
>
> subprocess.check_output(\[\"ping\", \"-c\", \"1\", host\], timeout=3)
>
> return f\"{host} is reachable.\"
>
> except subprocess.CalledProcessError:
>
> return f\"{host} did not respond.\"
>
> [**NOTE** Declarative Tools.]{.smallcaps} LangChain's \@tool decorator
> automatically registers metadata (name and docstring) so the agent can
> describe and select the tool at runtime.
>
> ***[2.3.3 Running the Reasoning Loop]{.smallcaps}***

Now we'll assemble everything together to take in a list of URLs to run
ping on, using our LangChain agent (Listing 2.8).

Listing 2.8 Executing the Agent

from adapters.langchain.agent import build_langchain_agent

from mytools import ping_host

agent_run = build_langchain_agent(\[ping_host\])

targets = \[\"example.com\", \"no-such-host.local\"\]

for host in targets:

print(\"\>\>\", agent_run(f\"Check reachability of {host}\"))

\# Sample output (truncated):

\# \>\> example.com is reachable.

\# \>\> no-such-host.local did not respond.

Behind the scenes, the agent generated a reasoning step ("Try ping_host
with target=X"), executed the tool, observed the result, and logged the
artifact in /runs/\<uuid\>.jsonl.

***[2.3.4 Adding Memory and Reflection]{.smallcaps}***

LangChain's ConversationBufferMemory is its memory component that keeps
track of the conversation history (storing the HumanMessage and
AIMessage objects). This helps the agent stay aware of prior results, so
it can reflect and use past history within the context window (Listing
2.9):

Listing 2.9 Reflecting on Past Actions

> \# Initiate the memory buffer
>
> memory = ConversationBufferMemory()
>
> \# execute a conversation\...
>
> \# Get a list of the model and user messages
>
> print(memory.chat_memory.messages)
>
> \# Get the chat history in string format
>
> print(memory.buffer)

\# Typical output:

> \# \>\> We tested two hosts. example.com responded; no-such-host.local
> did not.

This demonstrates *reflection*, which is the agent used memory of
earlier actions to form a conclusion.

> **ReAct in One Sentence**
>
> LangChain's ReAct pattern alternates reasoning and action steps
> automatically. You don't have to manage the loop; you just inspect the
> trace it produces.

***[2.3.5 Adding Human-in-the-Loop Gates]{.smallcaps}***

Automation is powerful, but every offensive-security agent must have
gates: they need to be able to stop and ask permission from another
entity (e.g., a manager, security professional, another LLM) before
acting.

The example in Listing 2.7 requires that the user interacts with the AI
model in the terminal to tell the agent whether or not to run the ping
tool we created.

Listing 2.10 Simple Approval Gate

def confirm(prompt: str) -\> bool:

reply = input(f\"\[Confirm\] {prompt} (y/n): \")

return reply.lower().startswith(\"y\")

if confirm(\"Proceed with external ping tests?\"):

for host in targets:

agent_run(f\"Check reachability of {host}\")

else:

print(\"Aborted by user.\")

We will extend this pattern in Chapter 3 to apply to multi-agent
pipelines.

> [**TIP** Never Skip the Gate.]{.smallcaps} Always require explicit
> approval before an agent performs network or system actions. Human
> review isn't bureaucracy---it's a safety feature.

***[2.3.6 Reflection and Improvement]{.smallcaps}***

After a few runs, your agent may successfully complete the task.
However, when it doesn't, you'll notice the following patterns in your
LLM outputs:

- Some outputs will repeat themselves. This can be an indicator that the
  model is stuck on some suboptimal solution, and it's not addressing
  the core issue.

- Some outputs will drift slightly off topic, because LLMs are
  stochastic and can follow random threads.

When you are running into these issues and you want to improve your
workflow, there are two quick fixes for this:

1.  *Set temperature to a low value (recommended range: 0.0--0.2)* --
    The temperature is a model parameter that adjusts how "creative" the
    model is. Lower values allow the model to return more consistent
    results, while higher values (e.g., 1.0) represent very creative and
    random responses.

2.  *Log everything* -- As a best practice, you should store your logs
    so that you can 1) study and replay failed runs later to determine
    the root cause, and 2) have LLMs take that context to improve their
    responses if you force the system to re-evaluate and re-try.

To refine the agent's reasoning, you can review the logs and manually
evaluate how to improve your agentic workflow, or you can add a final
reflection prompt after the workflow is completed to have the LLM
identify possible improvement areas.

> [**TIP** Determinism Is a Spectrum]{.smallcaps}. Don't chase identical
> results---chase reproducible reasoning. Your logs are what make the
> experiment repeatable.

The following prompt will ask the LLM how to adjust the tests it wrote
to improve it for future iterations. You can adjust this process further
to reflect on any kind of workflow.

Given previous results, how should we adjust our next tests?

> [**CAUTION** Reflection isn't review.]{.smallcaps} A model's
> "reflection" can sound confident even when it's wrong. Always verify
> reasoning before accepting it as fact.

***[2.3.7 Comparing Workflows with AutoGen]{.smallcaps}***

LangChain is a comprehensive LLM framework that allows us to build
production-ready AI applications, and is well-suited for applications
that require a Retrieval Augmented Generation component. That being
said, LangChain can be difficult to work with -- the library is evolving
at a rapid pace, and there issues like frequent breaks with earlier
versions, performance issues, and overengineering that adds unnecessary
complexity.

Another notable LLM framework for our discussion is AutoGen. It is an
open-source agent framework from Microsoft that is designed to rapidly
prototype multi-agent workflows. If you prefer to develop with AutoGen
in mind, you can replace build_langchain_agent() or add another adapter
using the following code in Listing 2.9.

Listing 2.11 AutoGen Example

from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(name=\"triage\",
llm_config={\"temperature\":0.2})

user = UserProxyAgent(\"operator\", code_execution_config=False)

assistant.register_function(ping_host)

assistant.initiate_chat(user, message=\"Check reachability of
example.com\")

We'd note the following:

- You can think of the AssistantAgent and UserProxyAgent classes as two
  different agent roles

- The AssistantAgent is meant to help in triage (discussed in more depth
  later)

- The UserProxyAgent is an agent that can execute code and provide
  feedback to the other agent. Setting code_execution_config to False
  means the agent can't run code.

- The .register_function() method is used to register tools. Note this
  differs from LangChain, which uses the \@tool decorator

> **Framework Swap Checklist**
>
> Preserve your core models (Message, Observation, Tool).
>
> Keep I/O JSON-safe.
>
> Confine framework imports to /adapters.
>
> Validate identical artifact logs before trusting results.

This example illustrates that both implementations satisfy the same
Minimal Agent Spec. However, you'll find that functions, objects, and
methods will differ across frameworks, despite accomplishing the same
tasks.

> **Exercise 2.2. Build Your Own Analysis Agent**
>
> Modify the Triage Agent to read a small JSON file of web-app scan
> results.\
> Have it:

1.  Extract each finding.

2.  Rank severity from 1 to 5.

3.  Output a short summary report.

> Inspect the generated JSONL log and verify that each reasoning step is
> recorded. Once you do this, you will have a working agent with memory,
> tools, reflection, and governance.
>
> Validate identical artifact logs before trusting results.

***[2.3.9 LangChain Agent Summary]{.smallcaps}***

- The Minimal Agent Spec runs cleanly in LangChain using LLM + Tool +
  Memory.

- Adapters isolate framework code, keeping your system portable.

- Reflection and artifact logging make reasoning auditable.

- Safety gates transform clever code into responsible automation.

Next, in Section 2.4, you'll see how to swap this agent for AutoGen or
LangGraph without rewriting its core and discuss how these frameworks
handle -agent coordination at a high-level.

1.  ***Agent Adapters***

LangChain is widely used with AI engineers and developers, and it gave
us a clean, modular way to build our first agent. But frameworks evolve
quickly, and the latest updates or patches can easily break your code.
Additionally, the LLM space is rapidly growing, and tomorrow's engineers
may prefer to use AutoGen, LangGraph, CrewAI, or another framework that
has not yet been released.

Rather than hard-coding and relying on third-party libraries as external
dependencies, we can treat each framework as a swappable *adapter*, code
that can bridge different modules (e.g., custom code versus third-party
code). By creating adapters, we ensure our system is robust against
changes, and that we can implement the same core interfaces we defined
in the Minimal Agent Spec using different frameworks.

In this section, you'll extend the robustness and reliability of your
agent system to use AutoGen for your Triage agent.

***[2.4.1 Why Adapters Exist]{.smallcaps}***

As a general best practice for software development, when you decouple
modules from each other, there are several advantages over a
tightly-coupled system that relies on external libraries (Figure 2.9):

1.  *Portability* -- You can easily swap libraries without rewriting the
    core business logic.

2.  *Testability* -- You can test the agent's behavior without a live
    API or without setting up complex third-party services.

3.  *Longevity* -- When third-party library updates with breaking
    changes, you only need to fix it in the adapter module rather than
    throughout the entire codebase.

4.  *Cost control* -- You can easily swap cheaper alternatives or add
    fallback logic without rewriting the core logic.

5.  *Better readability* -- Separating modules helps maintain the
    readability of the codebase and reduces a developer's mental
    fatigue.

6.  *Vendor independence* -- Creating adapters prevents vendor lock-in,
    which allows you to remain agile and independent of a vendor's
    activities.

┌────────────────────────────┐

│ Core Logic │

│ (plan, act, reflect, log) │

└────────────┬───────────────┘

│

┌─────────┴──────────┐

│ │

LangChain Adapter AutoGen Adapter

Figure 2.3. Adapter pattern for AI agents. The core logic should be
decoupled from adapters, which contain components that rely on
third-party libraries.

Note that the core application logic never imports LangChain or AutoGen
directly---it just calls the adapter's run() method. That discipline
will pay off in Chapter 3, when you plug multiple agents into a single
pipeline.

***[2.4.2 AutoGen in a Nutshell]{.smallcaps}***

Recall that AutoGen is a framework that specializes in multi-agent
workflows. It organizes interaction through *agents* that talk to each
other. A minimal configuration has two roles, which we described
previously:

- AssistantAgent --- the AI decision-maker (your triage logic).

- UserProxyAgent --- a controller that mediates requests and tool calls.

We register existing tools as callable functions using the
.register_function method. Everything else flows from the same
principles we've already established. In listing 2.9, we'll create an
AutoGen adapter that is similar to our LangChain adapter to run our
ping_host tool.

Listing 2.12 Building the AutoGen adapter

\# adapters/autogen/agent.py

from autogen import AssistantAgent, UserProxyAgent

from core.logger import ArtifactLogger

from mytools import ping_host

def build_autogen_agent():

logger = ArtifactLogger()

assistant = AssistantAgent(\"triage\", llm_config={\"temperature\":0.2})

user = UserProxyAgent(\"operator\", code_execution_config=False)

assistant.register_function(ping_host)

def run(prompt: str):

result = assistant.initiate_chat(user, message=prompt)

logger.write({\"input\": prompt, \"output\": str(result)})

return result

return run

Usage is identical to the LangChain adapter:

from adapters.autogen.agent import build_autogen_agent

agent_run = build_autogen_agent()

agent_run(\"Check reachability of example.com\")

***[2.4.3 Comparing Framework Behavior]{.smallcaps}***

We summarize the differences between LangChain and AutoGen in Table 2.4.
Each framework has its own strengths and weaknesses, but they both
produce the same ReAct agentic pattern: reason → act → observe →
reflect. Choosing one framework over another depends on the use case
you're solving for and the application you're building.

Table 2.4. Comparison between LangChain and AutoGen

  --------------------------------------------------------------------
  Feature        LangChain                   AutoGen
  -------------- --------------------------- -------------------------
  Tool interface \@tool decorator / Tool     Register Python functions
                 class                       

  Memory         ConversationBufferMemory    Built-in conversation
                                             state

  Coordination   AgentExecutor loop          Agent-to-agent messaging

  Logging        Custom callbacks            Explicit logging in
                                             wrapper

  Concurrency    Single thread by default    Supports multi-agent
                                             chats
  --------------------------------------------------------------------

***[2.4.4 Beyond AutoGen --- CrewAI and LangGraph]{.smallcaps}***

We discussed LangChain and AutoGen as the main frameworks we'll discuss
throughout this book. However, there are two other notable frameworks
that illustrate where the agentic AI ecosystem is headed. Both of them
are built on top of LangChain, but they have different underlying
philosophies and use-cases.

CrewAI is a role-based multi-agent framework that focuses on
collaborative AI agents - users should aim to build AI teams (or crews)
with specialized roles to fullfill specific tasks. Compared to AutoGen,
it has an opinionated structure, which can make it faster to get started
on common tasks. While it's less flexible that AutoGen, its
business-friendly abstractions make it ideal for process automations
(e.g., AI marketing teams, research crews, etc).

LangGraph is a library built from the LangChain creators, but it is
specifically created for building cyclic, graph-based agent workflows.
It allows developers to build pipelines as graphs of nodes and edges,
enforcing explicit state transitions. This means, you can control the
flow of an agent using loops, conditional statements, and complex
routing, and persist the intermediate steps. As is the case with all
graph-based technologies, LangGraph is much more complex than chains,
and it makes many more API calls, resulting in higher costs and latency.
However, if you need to build complex agentic workflows for
production-ready uses, LangGraph is a great tool for graph-based
implementations.

***[2.4.5 The Unviersal Adapter Pattern]{.smallcaps}***

In summary, to make future swaps between different frameworks painless,
codify this one rule: Every framework lives behind an adapter function
that accepts the same parameters and returns a callable run() method.

In Listing 2.10, we define another abstraction called the get_agent
function, which allows us to grab the adapter we'd like to use for
downstream tasks.

Listing 2.13 Universal Adapter Selector

from adapters.langchain.agent import build_langchain_agent

from adapters.autogen.agent import build_autogen_agent

def get_agent(adapter=\"langchain\", tools=None):

if adapter == \"autogen\":

return build_autogen_agent()

return build_langchain_agent(tools or \[\])

Now your top-level code stays frozen even as frameworks evolve.

> **Exercise 2.3. Cross-Adapter Validation**

1.  Run the same input prompt through both the LangChain and AutoGen
    adapters.

2.  Compare the JSONL logs in the runs/ directory.

3.  Confirm that both recorded equivalent reasoning steps.

> If the artifacts align, congratulations---you've verified that your
> architecture is truly framework-agnostic.
>
> Validate identical artifact logs before trusting results.

***[2.4.6 Adapter Summary]{.smallcaps}***

- Adapters insulate your logic from framework churn.

- LangChain, AutoGen, CrewAI, and LangGraph share the same agentic core.

- Keeping all I/O JSON-serializable makes logs portable and pipelines
  replayable.

- The universal adapter function future-proofs every example in this
  book.

Next, in Section 2.5, we'll add Safety and Governance to ensure that
autonomy never outruns authorization.

1.  ***Safety and Governance***

By now, your agent can reason, act, and reflect without constant human
supervision. That autonomy is exactly what makes it useful, and what
makes it dangerous if left unchecked.

In offensive security, automation must always operate within clearly
defined boundaries. A well-designed agent doesn't just work; it knows
where it may not work.

This section turns those ethical ideas from Chapter 1 into technical
controls: safety gates, sandboxing, logging, and auditability. These
concepts are not meant to add bureaucratic overhead, but they are
established engineering principles that transform clever scripts into
trustworthy systems.

***[2.5.1 Why Safety Matters]{.smallcaps}***

Offensive security tools and techniques are dual-use: the same skills
used to identify vulnerabilities can be weaponized for malicious
purposes. The only thing that separates a penetration tester and a
cybercriminal is authorization and intent. Strict governance is
essential to prevent the crossing of ethical and legal boundaries.

These skills and dangers are amplified with automation. The same
reasoning capability that helps an agent can lead it to test outside its
authorized scope, misinterpret network boundaries, or execute
destructive commands based on misunderstandings. This poses operational
risks that can result in unintended damage to production systems,
including running a destructive action by mistake and service outages
affecting critical infrastructure. There are also ethical and legal
risks: without proper authorization or by processing sensitive data in
an unsafe way, offensive security activities are a computer crime under
the US Computer Fraud and Abuse Act (CFAA).

Without guardrails, an AI agent could:

- Trigger aggressive scans on production hosts during business hours
  (adding unnecessary latency and hurting the user experience),

- Exfiltrate confidential data that was not part of the engagement scope

- Generate payloads that violate your testing agreement or terms of
  service

- Pivot into networks explicitly marked as out-of-bounds

Governance mechanisms act as circuit breakers between creativity and
consequence. They serve to limit what an agent can execute without
verification. The following sections will discuss specific approaches to
ensuring AI agents operate safely within our systems.

> **If it can't be audited, it isn't safe.**
>
> Logging and human approval aren't red tape; they're how we prove
> integrity to clients, legal teams, and ourselves.

***[2.5.1 Building Safety Gates]{.smallcaps}***

As we briefly discussed in Chapter 1, a *gate* is any checkpoint that
enforces review or conditions before a step continues. Gates can be
manual (requiring human input) or automated (rules that stop unsafe
operations or other LLMs that judges whether an operation is unsafe).

In Listing 2.11, we implement a simple safety gate that does two
things: 1) it automatically blocks an agent from touching critical
infrastructure if the target contains any of the following strings:
"prod", "payment", or "core-db". 2) For all other targets, it pauses
execution and asks the operator for specific approval before proceeding.

Listing 2.14 Simple Gate Implementation

def safety_gate(action: str, context: dict) -\> bool:

\"\"\"Return True if action is approved to proceed.\"\"\"

prohibited_hosts = \[\"prod\", \"payment\", \"core-db\"\]

if any(p in context.get(\"target\", \"\") for p in prohibited_hosts):

print(f\"\[Gate\] Blocked unsafe target: {context\[\'target\'\]}\")

return False

confirm = input(f\"\[Gate\] Approve \'{action}\' on
{context\[\'target\'\]}? (y/n): \")

return confirm.lower().startswith(\"y\")

We recommend that you integrate this check inside your act() method or
pipeline loop so every high-risk command passes through human review.

> [TIP]{.smallcaps} Design gates first, then tools. It's easier to
> expand authorization later than to rebuild a system that assumed
> unlimited freedom.

***[2.5.3 Sandboxing and Isolation]{.smallcaps}***

Even approved actions should run in a controlled environment.
*Sandboxing* is running code in an isolated environment that restricts
access to the broader system. It's a place where experiments can be
conducted while restricting access to the broader system.

AI agents automatically generate and execute code you haven't personally
reviewed, which can cause several unintended side effects that can be
dangerous. Sandboxing ensures these errors happen in a contained
environment. It's a final defensive layer when safety gates and human
approval aren't enough. Figure 2.4 illustrates visually how the sandbox
is its own separate container from the rest of the system.

Common strategies for sandboxing include:

- *Containerization*: The agent should get an isolated environment
  inside Docker or Podman with network limits, resource quotas, and
  filesystem restrictions. Here, it can install tools, run exploits, and
  generate payloads that don't access and affect the real filesystem or
  network.

- *Process isolation:* An agent should not have full access to
  everything - we need to drop privileges and ensure the agent uses
  restricted user accounts with limited permissions.

- *Offline simulation:* We should be able to replay attack logic on
  synthetic or recorded data before executing against live targets. This
  let's us verify the agent's reasoning chain.

┌────────────────────────────────────────┐

│ Agent Process │

│ ┌──────────────────────────────────┐ │

│ │ Sandbox (network off) │ │

│ │ └── Tool execution here ─────┘ │ │

└──┴──────────────────────────────────┴──┘

Figure 2.4. Sandbox isolation model. Agents should be tested in a
restricted process inside a network-limited container for defense. That
way, if a safety gate falls (e.g., a human verifier doesn't catch an
error in reasoning logic), the system as a whole remains intact.

***[2.5.4 Comprehensive Logging]{.smallcaps}***

AI agents reason about what they do, choose tools, and execute commands
automatically. If something goes wrong (or even if it goes right), you
need to know what the agent decided to do, why it made that choice, when
did it happen, and did it succeed or fail. This helps us prove that we
stayed within our authorized bounds.

As we defined in Section 2.2.4, your ArtifactLogger schema defines the
input and output arguments that are captured. We can expand it to
capture metadata that supports replay and accountability, shown in
Listing 2.12.

Listing 2.15 Adding a New Record to the Artifact

record = {

\"run_id\": run_id,

\"agent\": \"triage\",

\"stage\": \"recon\",

\"timestamp\": timestamp,

\"input\": input_data,

\"output\": output_data,

\"approved_by\": user_email,

\"status\": \"success\"

}

logger.write(record)

Logs like this turn experiments into evidence. If something goes wrong,
you can reconstruct exactly what was decided, by whom, and why.

> **Defense Through Transparency**
>
> Your logs are valuable to defenders too. Blue-team engineers can
> replay your logs to:

- Understand attacker behavior: How did the agent chain exploits? What
  patterns emerged?

- evelop detections: What network traffic did the recon phase generate?
  Can we write SIEM rules to catch it?

- Test incident response: Can our SOC team identify the attack in our
  logs? How long did detection take?

- Improve defenses: Which vulnerabilities did the agent prioritize?
  Should we patch those first?

Good offensive data is good defensive data. Comprehensive logs makes the
entire organization more secure.

***[2.5.5 Operational Policies]{.smallcaps}***

Before any engagement, formalize these rules:

1.  *Authorized scope only* **--** Define targets, time windows, and
    prohibited actions in writing.

2.  Human review required**.** Every agent run must include at least one
    approval gate.

3.  *Data minimization* -- Agents should never collect or store
    unnecessary personal data.

4.  *Deletion on completion --* Purge artifacts after the engagement
    unless required for audit.

5.  *Responsible disclosure* -- Report vulnerabilities privately and
    within agreed timelines.

These policies make it possible to innovate responsibly.

***[2.5.6 Implementing Kill Switches]{.smallcaps}***

Sometimes the safest response is stop the action immediately*.* We need
to build in killswitches that prevents our agents from doing more harm.
Listing 2.13 implements a global killswitch that runs in the background
and continuously monitors for a manual abort command, allowing you to
immediately halt all agent operations if something goes wrong.

Listing 2.16 Global Kill Switches

import threading, time

class KillSwitch:

def \_\_init\_\_(self):

self.active = False

def monitor(self):

while True:

cmd = input(\"\[KillSwitch\] Type \'STOP\' to abort: \")

if cmd.strip().upper() == \"STOP\":

self.active = True

print(\"\[KillSwitch\] Aborting all agents.\")

break

Notes:

- The active flag is a shared signal that all agents can check. Setting
  active=True triggers an emergency stop.

- The monitor method continuously waits for keybord input. When you type
  "STOP", it sets active=True and stops the agent.

- We use the threading library to run the process in the background,
  allowing the agent to work normally while the kill switch siltently
  listens for the abort command.

> **Exercise 2.3. Your Safety Checklist**
>
> Draft a short checklist you'll use before every agent run:
>
> ☐ Defined scope
>
> ☐ Sandbox verified
>
> ☐ Gate configured
>
> ☐ Logging enabled
>
> ☐ Kill switch active
>
> Run the checklist manually once; in a following chapter we'll automate
> it in your pipelines.

***[2.5.7 Safety And Governance Summary]{.smallcaps}***

- Safety gates enforce review and prevent unauthorized actions.

- Sandboxing isolates tools and limits damage.

- Comprehensive logs provide traceability and support defensive
  analysis.

- Operational policies formalize ethical boundaries.

- Kill switches ensure human control, even under automation.

You've built a responsible agent that thinks before it acts. Now we'll
see it operate end-to-end in the Adaptive Triage Agent scenario.

1.  ***Capstone Project: The Adaptive Triage Agent***

You've built all the pieces: messages, tools, memory, adapters, and
safety gates. Now it's time to connect them into a single,
self-contained system---an agent that can read reconnaissance data,
reason about what matters, and produce a ranked summary while staying
inside ethical boundaries. Figure 2.11 shows what we expect to build in
the end of this capstone project.

Intake → Reason → Act → Observe → Reflect → Report

│ │ │ │ │

▼ ▼ ▼ ▼ ▼

JSON LLM Plan Tool Observation Summary

│ │ │ │

└── Logged in /runs/triage.jsonl ──┘

Figure 2.5. Adaptive Triage Flow. This diagram shows how information
moves through the loop and how every transition is logged for replay.

This is your capstone project for Chapter 2. We'll walk through each
stage and see how the ReAct loop you've learned works in practice in
triage.

***[2.6.1 Scenario: The Adaptive Triage Intern]{.smallcaps}***

You\'re testing a web application\'s security, and your reconnaissance
tools just finished scanning. You now have a JSON file with 847 entries:
subdomains, web pages, server information. Hidden somewhere in this pile
are the valuable targets---admin panels, staging servers with weak
passwords, exposed API endpoints. But most of the 847 entries are
useless: error pages, redirects, and dead links. Manually reviewing each
one would take hours you don\'t have.

Your manager asks you to build an AI assistant that reads this file,
identifies the most interesting targets, and writes a short report
explaining why they matter. The catch: it should only analyze data
you\'ve already collected, never touch live systems or make network
requests. This is perfect for an autonomous agent---clear objective,
bounded scope, and low risk since it\'s just reading files.

This \"Adaptive Triage Intern\" embodies everything from this chapter.
It operates within strict boundaries (file analysis only, no network
access), logs its reasoning so you can review its decisions, and runs
safely in a sandbox. Think of it as your smart assistant who handles
tedious data review so you can focus on actual hacking. By building this
agent, you\'ll apply all the safety principles to create something
genuinely useful for real penetration tests. Let\'s build it.

***[2.6.2 Data Intake]{.smallcaps}***

We'll start with a small mock dataset (targets.json):

\[

{\"host\": \"api.dev.example.com\", \"status\": 200, \"title\": \"Dev
API\"},

{\"host\": \"staging.example.com\", \"status\": 403, \"title\":
\"Forbidden\"},

{\"host\": \"admin.example.com\", \"status\": 401, \"title\":
\"Unauthorized\"},

{\"host\": \"cdn.example.com\", \"status\": 200, \"title\": \"OK\"}

\]

The agent's first task is to ingest this data as structured input: no
network calls, no live probing.

***[2.6.3 Reasoning Step]{.smallcaps}***

Feed the parsed JSON to the LLM through the adapter we built in a
previous section (Listing 2.14):

Listing 2.17 Planning and Reasoning

input_text = (

\"Given these host entries, rank which are most likely \"

\"to expose sensitive admin or test interfaces. \"

\"Explain your reasoning briefly.\"

)

triage_agent = get_agent(adapter=\"langchain\", tools=\[\])

result = triage_agent(f\"{input_text}\\n{targets}\")

print(result)

\# Sample output:

\# 1. admin.example.com --- 401 Unauthorized suggests login portal.

\# 2. staging.example.com --- 403 indicates restricted staging area.

\# 3. api.dev.example.com --- development API; check for leaks.

\# 4. cdn.example.com --- public CDN, low risk.

The agent generated its own reasoning chain without touching the
network---safe, contextual analysis only.

***[2.6.4 Action and Observation]{.smallcaps}***

Now imagine extending the toolset with a lightweight content analyzer
that checks HTML titles or headers for keywords like *"login"* or
*"debug"*. Each run produces an Observation record appended to the
artifact log.

observation = {

\"tool\": \"analyze_titles\",

\"input\": targets,

\"output\": {\"login_hits\": 2, \"debug_hits\": 1},

\"success\": True

}

logger.write(observation)

> [**TIP** Every Action leaves a Trail.]{.smallcaps} In a pipeline,
> these same observation logs become the dataset defenders use to tune
> detection rules.

***[2.6.5 Reflection and Reporting]{.smallcaps}***

After collecting observations, prompt the agent to reflect and summarize
our findings. We provide an example prompt in Listing 2.15.

Listing 2.18 Reflection Phase

summary_prompt = (

\"Summarize our findings from the triage phase. \"

\"List top priorities and any gaps that require manual review.\"

)

report = triage_agent(summary_prompt)

print(report)

\# Example output:

\# High priority: admin.example.com (login portal).

\# Medium: staging.example.com (restricted env).

\# Low: others appear benign.

#Recommend manual validation of authentication on top targets.

The result is a short, auditable report generated entirely from logged
data.

***[2.6.6 Safety Review]{.smallcaps}***

Before you celebrate, confirm the agent respected every safeguard, which
is provided in Table 5.

Table 5. Safety Review Table

  --------------------------------------------------------------------
  **Control**   **Purpose**                               **Status**
  ------------- ----------------------------------------- ------------
  Gate          Manual approval before any external tool  Enabled
                call                                      

  Sandbox       All actions limited to offline data       Verified

  Logging       JSONL artifacts for every step            Complete

  Kill Switch   Operator can stop agent instantly         Armed
  --------------------------------------------------------------------

If all boxes are checked, you've demonstrated controlled autonomy.

***[2.6.7 Reflection and Tuning]{.smallcaps}***

Try tweaking the agent:

- Add a new tool to detect version headers.

- Adjust the ranking criteria (e.g., "impact over exposure").

- Run again and compare the new artifact log.

This iterative improvement process mirrors how real red-team pipelines
evolve---small adjustments, measured results, clear accountability.

> **[TIP]{.smallcaps}** Reproducibility over perfection. The goal isn't
> a flawless AI analyst; it's a repeatable process you can test, audit,
> and improve.

***[2.6.8 Your Own Adaptive Loop]{.smallcaps}***

2.  Replace the dataset with your own recon results.

3.  Modify the reasoning prompt to focus on vulnerability categories
    (e.g., SSL misconfigurations).

4.  Add one new safety gate, such as a rule preventing analysis of
    domains outside a whitelist.

5.  Run and inspect the runs/ directory.

You've just built a safe, adaptive agent that reasons over security
data. In Chapter 3, you'll learn how to connect several of these
agents---Recon, Triage, Report---into a single, auditable pipeline.

***[2.6.9 Triage Summary]{.smallcaps}***

- The Adaptive Triage Agent demonstrates the complete loop: reason **→**
  act **→** observe **→** reflect **→** report**.**

- All actions operate offline and within defined safety gates.

- Structured logging turns one-off experiments into reusable workflows.

- The same architecture will scale seamlessly into multi-agent
  pipelines.

***Summary***

- Agents wrap reasoning around action. Where an LLM predicts the next
  token, an agent predicts the next step---using tools, memory, and
  feedback to pursue a goal.

- The Minimal Agent Spec makes autonomy reproducible. A consistent
  schema for messages, tools, observations, and artifacts allows your
  agents to run anywhere and be inspected later.

- LangChain and AutoGen both satisfy the same core design. Frameworks
  may differ in syntax, but the architecture---plan → act →
  reflect---remains constant.

- Safety is engineered, not assumed. Gates, sandboxing, logging, and
  kill switches keep AI experimentation ethical and auditable.

- The Adaptive Triage Agent demonstrates the full loop. It reasons about
  data, takes controlled action, records evidence, and reports
  findings---all within a defined scope.

- Reproducibility outweighs cleverness. A transparent, logged system can
  be improved and defended; a black-box script cannot.
