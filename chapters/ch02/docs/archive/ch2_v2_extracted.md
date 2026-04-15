***2***

*Building your first AI agent*

**This chapter covers**

- Contrasting agents with script-based automation

- Modeling agent execution as a control loop

- Defining core agent components and boundaries

- Implementing a minimal agent specification

- Applying agents to recon data triage workflows

In chapter 1, we introduced AI agents and pipelines that bring
reasoning, control, and accountability into offensive security
workflows. We demonstrated why simple scripts and one-off LLM calls
break down in dynamic environments, and why structure becomes crucial
once automation starts making decisions. This chapter moves from theory
to construction by building a real AI agent from the ground up.

The goal is not to build a clever demo or a production system: we
illustrate how wrapping a large language model inside a small set of
explicit components (messages, tools, and artifacts) turns reactive text
generation into a controlled decision-making loop that can be inspected,
replayed, and defended.

We'll start by establishing a clear mental model for how agents work and
by drawing firm boundaries between agents, scripts, and tools. We'll
illustrate how we can build an agent using Python without AI frameworks.
After setting our foundation, we will apply frameworks, such as
LangChain and AutoGen. The chapter concludes with the governance
patterns that ensure agent behavior remains safe and defensible in
real-world engagements.

1.  Limitations of script-based automation

Security professionals have been automating tasks for decades using
scripts, cron jobs, and one-off tools, which have made work faster and
more repeatable. However, these tools share a fundamental limitation:
they require humans to be the primary decision-makers.

A script enables a programmer to write a predefined set of instructions
that the computer can follow to execute a specific task. Scripts
commonly have a fixed file state written by the programmer to access
data and other artifacts. When the environment (e.g., the file system)
changes, scripts can fail outright or produce incorrect output.
Ultimately, these bugs in your scripts grow the attack surface that
attackers can exploit, becoming a liability for your system and your
organization.

Large language models (LLMs) have the reasoning capabilities to solve
these dynamic problems. An LLM can summarize scan output, point out
anomalies, or suggest next steps. However, an LLM alone is not enough:
chatbot models are trained only respond to prompts. By themselves,
chatbots cannot persist states and their memory between different
actions, respond to changes in their environment, and cannot explain or
justify why a particular decision was made. In security contexts, where
a lot is at stake to get things right, this kind of unstructured
reasoning is a liability.

2.  What is an agent?

An agent is a system that can make controlled decisions without human
intervention. The agent model receives input, decides what to do next,
invokes an action, observes the result, and records what happened.
Agents empower security professionals. They enable autonomous task
execution, can respond in dynamic environments, and can operate 24/7.
Together, agents are essential to protecting modern software systems
that are prone to malicious attacks. Figure 2.1 illustrates the
differences between scripts and AI agents.

{Figure 2.1}

Figure 2.1. The difference between a script and an AI agent. Scripts are
an example of procedural programming, in which instructions are followed
step by step. In contrast, an AI agent can reason by itself and act
without human intervention.

The distinction between a script and an AI agent matters because
offensive security workflows are not linear. For the reconnaissance task
we're implementing, reconnaissance feeds triage and triage feeds
prioritization. Failures force reassessment. Automation without
reasoning becomes brittle. A reasoning engine without having control
gates, where humans can intervene when things go wrong, is unsafe.

For penetration testers, bug hunters, and red team operators, the
limiting factor is rarely another software tool. It's volume: a single
engagement can generate hundreds or thousands of endpoints, parameters,
headers, and responses. Scripts can collect all of that data, but they
cannot tell you where to focus.

An agent does not replace human intuition and judgement, but rather
augments it. An agent turns exploratory work into a workflow that can be
reviewed, replayed, and defended by recording an agent's actions,
including the steps that were taken, the tool that were used, and the
responses that were observed.

**[DEFINITIONS]{.smallcaps}** A Large Language Model (LLM) is a
text-prediction engine that is trained to generate a response that is
associated with a textual input. LLMs only generate text, have no memory
between API calls, respond to single prompts, and produce only one
output per input. In contrast, agents are autonomous systems that use an
LLM as the "brain", but add additional capabilities for perception,
memory, planning, interactions with the environment, and actions that
lead to achieving a goal. Agents have memory and can remember context
across multiple interactions. They can also utilize tools, which are
resources that an LLM can leverage to expand its capabilities, such as
custom functions, APIs, databases, MCP servers, and more. Agents possess
reasoning capabilities and can break down complex, multi-step plans,
iteratively working towards objectives without human guidance. Finally,
agents operate in a feedback loop -- they can perceive → reason → act →
observe, and repeat until the goal is achieved. In summary, agents are
pipelines that extend the capabilities of LLMs to operate autonomously.

Now that we've distinguished a script from an AI agent let's dive into
how an agent works. The following section breaks down the agent into
five essential components: the messages, tools, memory, controller, and
artifacts that comprise the agent loop.

3.  Anatomy of an agent

An agent is a structured loop that connects five core components,
enabling agents to perform complex tasks, including reasoning, action,
observation, reflection, and recording. Figure 2.1 shows a schematic
representation of a single agentic loop. By iterating through these
components, agents can perform tasks previously reserved for humans.

2.2.1 Core components

AI agents comprise five key components summarized in Table 2.1:
messages, tools, memory, agent controllers, and artifacts. We describe
these components in more depth below.

Table 2.1. Core agent components

  ---------------------------------------------------------------------------
  Component    Role                  Typical Artifact     Why It Matters
  ------------ --------------------- -------------------- -------------------
  Message      A single              { \"role\":          Structures
               communication unit    \"system\",          reasoning history,
               between the system,   \"content\":         and makes loops
               user, and model.      \"Analyze scan       reproducible.
                                     results\" }          

  Tool         An external           Function handle, CLI Turns reasoning
               capability the agent  command, or REST     into measurable
               can call---scripts,   call                 action.
               APIs, scanners.                            

  Memory       Storage for past      Conversation buffer  Provides context
               messages, results,    or vector store      and continuity
               and summaries.                             between steps.

  Agent        The controller that   Plan object or       Transforms model
  controller   determines *the next  next-action list     predictions into an
               action*.                                   intentional
                                                          workflow.

  Artifact     The durable record of JSONL log, Markdown  Enables auditing,
               what happened.        report, database row replay, and
                                                          defensive analysis.
  ---------------------------------------------------------------------------

*Messages* are a structured unit of communication within a conversation
between the user and the LLM. They are the building blocks that form a
prompt, which are the input you send to an AI model to get a response.
It's usually a question or a command, like "List 5 poems Emily Dickinson
wrote". In turn-based interactions (e.g., chatbots), the prompt is
usually a single message. However, agents typically construct a prompt
from multiple messages that work together.

> **Chain of Thought (CoT) and reasoning**
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
respond to simple messages, whereas agents can interact with the outside
world. *Tools* enable LLMs not only to converse but also to interact
with the outside world. They consist of custom functions, API calls, or
database queries that an agent needs to execute to complete a given
task. This is important for several reasons: for example, to retrieve
real-time information, an agent needs access to the internet, as LLMs
are limited by the knowledge they acquired during training. Or if you
want an LLM to perform a mathematical operation, tools are great because
LLMs are known to hallucinate, especially when it comes to mathematical
reasoning questions. Tools are specialized instruments that the agent
can pick up and use when needed, when they cannot reason through the
task.

![A diagram of a software company AI-generated content may be
incorrect.](media/image1.png){width="5.249016841644794in"
height="2.7478991688538934in"}

Figure 2.2. An agent schematic. An AI agent consists of a controller
that orchestrates the execution of data inputs, function calls, and
model outputs. Model outputs and other logging information is saved into
artifacts, which are persistent files. A model can interact with the
world using tools, which are functions that AI model can implement. A
model can use multiple tools, expanding their utility.

As described in the previous section, an *agent* is a pipeline that
receives messages, determines when to utilize tools, accesses memory,
and generates responses. They follow a reasoning loop: understanding the
request, determining what information or actions are needed, calling the
appropriate tools, synthesizing results, and responding appropriately to
fulfill a user's request. It is a decision maker that orchestrates and
coordinates all components to accomplish tasks effectively.

Agents are powerful because they also consider prior interactions.
*Memory* is the way they retain information across interactions. Without
a memory component, each conversation would start fresh with no context.
Imagine having to copy and paste a previous conversation to get a
relevant response -- that is a terrible user experience! Memory can be
short-term (e.g., the past N number of messages in the conversation) or
long-term -- facts from past sessions that are stored in a special
container called a vector database. Memory is crucial because it makes
an agent feel like a personalized assistant as you use it over time.

Finally, agents can create *artifacts*, tangible outputs of the model.
These include documents, code files, reports, and charts. Artifacts are
typically formatted, saved, and can be downloaded or edited further by a
human (or another LLM). Altogether, these components form the basis of a
modern AI agent workflow.

2.2.2 The ReAct agent loop

Figure 2.3 shows how these core agentic components combine to solve the
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

The original ReAct implementation used only the Reasoning, Action, and
Observation loop, limiting its performance in real-world applications.
Since then, additional processes have been introduced and integrated
into the workflow to significantly improve an agent's general
performance, including:

- Reflection: The model performs a meta-cognitive evaluation of its own
  performance, which can inform its next steps.

- Recording: The information, context, learnings, logs, and model
  outputs from the session are stored for future reference and
  decision-making purposes.

While it seems simple, ReAct is powerful because it enables LLMs to act
as autonomous agents. The reasoning component grounds actions in reality
and helps prevent hallucinations. Additionally, the loop is flexible. It
enables the AI agent to adjust its plan based on what it discovers. Most
importantly, the agentic decision-making process is transparent,
allowing the user to understand how the model arrived at its decisions.

![A diagram of a process AI-generated content may be
incorrect.](media/image2.png){width="3.112412510936133in"
height="3.078170384951881in"}

Figure 2.3. A ReAct agent consists of 5 steps that are iterated until
they converge to a desired outcome: 1) Reason → Use the LLM to plan a
step. 2) Act → Execute that step with a tool. 3) Observe → Capture the
result. 4) Reflect → Update memory and decide again. 5) Record → Write
everything to an artifact.

2.2.3. The scope and responsibility of an agent

A key question is, why does all this matter? Why do we need to
complicate a simple LLM API call with all these additional components?
Simple automation systems like LLMs can return responses to prompts
(e.g., Tell me what is the capital of Kansas), but an LLM alone can't
reason about complex user queries, like mathematical reasoning problems
In critical applications like cybersecurity, which carry high stakes and
have legal and operational consequences, we need to be able to trust how
models arrive at their decisions.

By connecting an LLM with additional parts like messages, tools, memory,
and artifacts, you make an AI agent's behavior observable. We can store
the LLM's reasoning as an artifact and visualize the steps it took to
reach its conclusion. Gaining insights into the reasoning process allows
us to refine it further and put in control mechanisms with human
intervention.

**NOTE** An LLM provides reasoning, but only an agent provides
structure, control, and accountability.

Transparency into the reasoning process allows security testers to use
AI safely: every decision, every action, every result is logged as an
artifact through telemetry tools, which automatically collect, transmit,
and analyze data. For example, teams can use a tool like LangSmith to
manage LLM logs, metrics, and traces, and track events for enhanced
debugging and auditing.

Individual agents are well-suited to bounded security tasks such as
reconnaissance, triage, or analysis. As systems become more complex,
artifacts become more important. When multiple agents are chained
together, artifacts serve as the interface between stages---a pattern
explored further in Chapter 3.

Just as importantly, an agent is defined by what it is not. Agents are
not autonomous free-for-all systems, and they are they replacements for
tools or scripts. They do not create new capabilities. They coordinate
existing ones through controlled reasoning, explicit actions, and
recorded outcomes.

2.3 The minimal agent specification

This section translates the agent concepts introduced earlier into code.
We define a minimal agent specification: the smallest set of interfaces
and data structures an agent must support to be portable, testable, and
safe.

Think of this specification as an API contract. Every agent in this
book, regardless of framework, follows it. By defining agents in terms
of explicit messages, tool invocations, observations, and recorded
artifacts, agent behavior remains consistent, auditable, and defensible.

The specification is deliberately framework-agnostic. You can swap out
any AI library and the surrounding workflows still hold. The contract
defines *what* an agent must do and record, not *how* any framework
implements those behaviors.

**NOTE** The goal of the minimal agent specification is portability and
auditability, not feature completeness.

At this point, you already have everything required to build a working
agent. In the next section, we assemble the smallest possible
implementation that satisfies this specification. It uses exactly two
tools, passes a single artifact between them, and stops. There is no
memory, no optimization, and no framework-specific abstraction. The goal
is not intelligence---it's clarity.

2.4. Building the minimal agent

Up to this point, we've described agents conceptually: how they differ
from scripts and how their components fit together. This section
demonstrates the smallest possible implementation that satisfies the
agent model defined earlier.

In the code walkthrough below, we implement a very simple agent without
memory, optimization, and network access. The goal is to make the
mechanics of agency explicit.

**TIP** If this implementation makes sense, the structure of every agent
in this book will make sense.

This agent does exactly five things:

1.  Decide which tool to run

2.  Execute the first tool

3.  Record the result as an artifact

4.  Pass that artifact to a second tool

5.  Stop

    2.4.1 What this agent does

The agent processes a small piece of input text and produces a short
summary artifact:

- Tool A extracts URLs from the input

- Tool B summarizes the extracted URLs

- The agent controls execution order and records each step

All input is local and deterministic. No live network calls are made.

2.4.2 Messages and observations

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

- 

- *Tool*: The results from tool execution. These can include outputs
  from external systems (e.g., APIs, databases, custom tools) and
  observations the agent uses for reasoning.

**TIP** We recommend that you store your artifacts in simple formats
that JSON can handle. This means using basic types like strings,
numbers, booleans, arrays, and objects to avoid complex types that
require special conversions. For the data-centered developer, if you are
storing numerical data in NumPy arrays or similar objects, you need to
convert them to lists. Python objects need to be converted to
dictionaries. This practice ensures that your information can be
visualized in logs, dashboards, and other visual representations of your
data.

We define how to set the Message and Observation classes in Listing 2.1.
The Message class stores information passed through the agent, including
the role, content, the timestamp of the generated message, and
additional metadata. The Observations class captures what happened after
an action and includes information such as the tool name, model
inputs/outputs, error codes when they occur, and other key information
for model monitoring and error tracing.

Listing 2.1 Message and observation schemas

from pydantic import BaseModel, Field

from datetime import datetime

from typing import Optional, Dict, Any

class Message(BaseModel):

role: str \# \"system\", \"user\", \"agent\", \"tool\"

content: str \# natural-language text

timestamp: datetime = Field(default_factory=datetime.utcnow)

meta: Optional\[Dict\[str, Any\]\] = None

class Observation(BaseModel):

tool_name: str

input: Dict\[str, Any\]

output: Dict\[str, Any\]

success: bool

error: Optional\[str\] = None

timestamp: datetime = Field(default_factory=datetime.utcnow)

2.4.2 Tools

Tools are how an agent interacts with the world, and they include
anything from a custom function you wrote (e.g., a regex parser) to an
API call from an external service (e.g., a vulnerability scanner).

> **[NOTE]{.smallcaps}** The input and output data formats should follow
> the same schema that was provided in the Observations class we defined
> in Listing 2.1. This is to ensure that we can trace the movement of
> data across different agent modules.

In Listing 2.2, we define a schema for the base class Tools, which
include metadata like the tool name, description, and a method .invoke()
that can be used to run any kind of function, invoke an API, or do some
other task.

**Listing 2.2 The tool schema**

class Tool:

name: str

description: str

def invoke(self, input: Dict\[str, Any\]) -\> Dict\[str, Any\]:

\"\"\"Run the tool and return structured output.\"\"\"

raise NotImplementedError

2.4.3. Tool A: extract URLs

In Listing 2.3, we define a tool that scans input text and extracts
anything that looks like a URL. The tool will inherit the invocation
method we defined in the base class Tool.

**Listing 2.3** **ExtractUrlsTool**

import re

class ExtractUrlsTool(Tool):

name = \"extract_urls\"

def invoke(self, input: dict) -\> dict:

urls = re.findall(r\"https?://\[\^\\s\]+\", input\[\"text\"\])

return {\"urls\": urls}

This tool performs a single task and has no awareness of execution
context. It does not decide when it runs or how its output will be used.

2.4.4 Tool B: summarize URLs

In Listing 2.4, the second tool consumes the artifact produced by the
first tool and generates a short summary.

**Listing 2.4** **SummarizeUrlsTool**

class SummarizeUrlsTool(Tool):

name = \"summarize_urls\"

def invoke(self, input: dict) -\> dict:

return {

\"count\": len(input\[\"urls\"\]),

\"summary\": f\"Found {len(input\[\'urls\'\])} URLs.\"

}

Like the first tool, it consumes structured input and produces
structured output without knowledge of upstream or downstream behavior.

2.4.5 Artifacts and logging

Every agent run produces some data, plans, actions, results, and
reflections. We treat these outputs as artifacts, and we will save them
in JSONL (one JSON object per line) format. In Listing 2.5, we define
the artifact logger class that saves all model outputs to the JSONL log.
The log file will be stored in the directory run_dir. New traces will be
appended to this file as a new line. Artifact logging is important
because it provides an audit trail for your agent and allows you to
prove exactly what your agent did during any security task (e.g., a
penetration test). Logs are essential for assessments and debugging.
Additionally, from a compliance and legal protection standpoint, logs
demonstrate that your agent adhered to the scope of the security testing
project.

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

2.4.6. The minimal agent loop

An agent is responsible for deciding execution order and recording
outcomes. Listing 2.6 defines a minimal agent class that uses the two
tools we wrote to extract and summarize URLs.

Listing 2.6. MinimalAgent

class MinimalAgent:

def \_\_init\_\_(self, tools, logger):

self.tools = {tool.name: tool for tool in tools}

self.logger = logger

def run(self, text: str):

plan = \"extract_urls\"

observation_1 = self.tools\[plan\].invoke({\"text\": text})

self.logger.write({

\"tool\": plan,

\"input\": {\"text\": text},

\"output\": observation_1

})

plan = \"summarize_urls\"

observation_2 = self.tools\[plan\].invoke(observation_1)

self.logger.write({

\"tool\": plan,

\"input\": observation_1,

\"output\": observation_2

})

return observation_2

That is the entire loop. There are no callbacks, no implicit state, and
no framework-managed behavior. Only explicit decisions, actions,
observations, and recorded outcomes.

2.4.7 Putting it together

At this point, we can run the agent, which is shown in Listing 2.7.
We'll use the ArtifactLogger class to capture artifacts produced by the
model. We'll also instantiate a minimal agent model that will run our
two tools.

Listing 2.7. Running the agent

logger = ArtifactLogger()

agent = MinimalAgent(

tools=\[ExtractUrlsTool(), SummarizeUrlsTool()\],

logger=logger

)

result = agent.run(

\"Check https://example.com and https://admin.example.com/login\"

)

print(result)

  --------------- -------------------------------- ----------------------
                                                   

                                                   

                                                   

                                                   

                                                   

                                                   
  --------------- -------------------------------- ----------------------

This small set of rules is all you need to build interoperable agents.
Everything else, including the framework abstractions, fancy
orchestration, and memory stores, sits on top of this layer.

Exercise 2.1. Build your own tool

Write a simple Tool subclass that performs a harmless text operation,
such as counting words in a string or extracting URLs from JSON. Then
log the input and output using ArtifactLogger. You've just implemented
half of a working agent.

In the next section, we'll apply safety and governance tools to our
agent to ensure we don't break anything.

1.  

  ----------------- --------------------------------
                    

                    

                    

                    

                    

                    

                    
  ----------------- --------------------------------

- 
- 
- 

<!-- -->

- 
- 

1.  
2.  

- 
- 
- 
- 

1.  
2.  
3.  

- 
- 
- 
- 1.  

1.  
2.  
3.  
4.  
5.  
6.  

- 
- 

  ------------- --------------------------- -------------------------
                                            

                                            

                                            

                                            

                                            
  ------------- --------------------------- -------------------------

1.  
2.  
3.  

- 

- 

- 

- 2.5 Safety and governance

By now, your agent can reason, act, and reflect without constant human
supervision. That autonomy is exactly what makes it useful, and what
makes it dangerous if left unchecked. In offensive security, automation
must always operate within clearly defined boundaries. A well-designed
agent doesn't just work; it knows where it may not work.

This section turns those ethical ideas from Chapter 1 into technical
controls: safety gates, sandboxing, logging, and auditability. These
concepts are not meant to add bureaucratic overhead, but they are
established engineering principles that transform clever scripts into
trustworthy systems.

2.5.1 Why safety matters

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

If it can't be audited, it isn't safe

Logging and human approval aren't red tape; they're how we prove
integrity to clients, legal teams, and ourselves.

2.5.2 Building safety gates

As we briefly discussed in Chapter 1, a *gate* is any checkpoint that
enforces review or conditions before a step continues. Gates can be
manual (requiring human input) or automated (rules that stop unsafe
operations or other LLMs that judges whether an operation is unsafe).

In Listing 2.8, we implement a simple safety gate that does two
things: 1) it automatically blocks an agent from touching critical
infrastructure if the target contains any of the following strings:
"prod", "payment", or "core-db". 2) For all other targets, it pauses
execution and asks the operator for specific approval before proceeding.

Listing 2.8 Simple Gate Implementation

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

**TIP** Design gates first, then tools. It's easier to expand
authorization later than to rebuild a system that assumed unlimited
freedom.

2.5.3 Sandboxing and isolation

Even approved actions should run in a controlled environment.
*Sandboxing* is running code in an isolated environment that restricts
access to the broader system. It's a place where experiments can be
conducted while restricting access to the broader system.

AI agents automatically generate and execute code you haven't personally
reviewed, which can cause several unintended side effects that can be
dangerous. Sandboxing ensures these errors happen in a contained
environment. It's a final line of defense when safety gates and human
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
error in reasoning logic), the system remains intact.

2.5.4 Comprehensive logging

AI agents reason about what they do, choose tools, and execute commands
automatically. If something goes wrong (or even if it goes right), you
need to know what the agent decided to do, why it made that choice, when
did it happen, and did it succeed or fail. This helps us prove that we
stayed within our authorized bounds.

As defined in Section 2.2.5, your ArtifactLogger schema specifies the
input and output arguments captured. We can expand it to capture
metadata that supports replay and accountability, shown in Listing 2.9.

Listing 2.9 Adding a New Record to the Artifact

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

Defense through transparency

Your logs are valuable to defenders too. Blue-team engineers can replay
your logs to:

Understand attacker behavior: How did the agent chain exploits? What
patterns emerged?

Develop detections: What network traffic did the recon phase generate?
Can we write SIEM rules to catch it?

Test incident response: Can our SOC team identify the attack in our
logs? How long did detection take?

Improve defenses: Which vulnerabilities did the agent prioritize? Should
we patch those first?

Good offensive data is good defensive data. Comprehensive logs make the
entire organization more secure.

2.5.5 Operational policies

Before any engagement, formalize these rules:

- 

- Authorized scope only -- Define targets, time windows, and prohibited
  actions in writing.

- 

- Human review required. Every agent run must include at least one
  approval gate.

- 

- Data minimization -- Agents should never collect or store unnecessary
  personal data.

- 

- Deletion on completion -- Purge artifacts after the engagement unless
  required for audit.

- Responsible disclosure -- Report vulnerabilities privately and within
  agreed timelines.

These policies make it possible to innovate responsibly.

2.5.6 Implementing kill switches

Sometimes the safest response is to stop the action immediately*.* We
need to build in killswitches that prevents our agents from doing more
harm. Listing 2.10 implements a global killswitch that runs in the
background and continuously monitors for a manual abort command,
allowing you to immediately halt all agent operations if something goes
wrong.

Listing 2.10 Global kill switches

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

- The monitor method continuously waits for keyboard input. When you
  type "STOP", it sets active=True and stops the agent.

- We use the threading library to run the process in the background,
  allowing the agent to work normally while the kill switch silently
  listens for the abort command.

Exercise 2.3. Your safety checklist

Draft a short checklist you'll use before every agent run:

> ☐ Defined scope
>
> ☐ Sandbox verified
>
> ☐ Gate configured
>
> ☐ Logging enabled
>
> ☐ Kill switch active

Run the checklist manually once; in the following chapter we'll automate
it in your pipelines.

2.5.7 Safety and governance summary

- Safety gates enforce review and prevent unauthorized actions.

- Sandboxing isolates tools and limits damage.

- Comprehensive logs provide traceability and support defensive
  analysis.

- Operational policies formalize ethical boundaries.

- Kill switches ensure human control, even in automated systems.

You've built a responsible agent that thinks before it acts. Now we'll
see it operate end-to-end when we build a triage agent in the next
section.

2.6. The triage agent

You've built all the pieces: messages, tools, memory, adapters, and
safety gates. Now it's time to connect them into a triage agent that can
read reconnaissance data, reason about what matters, and produce a
ranked summary while staying inside ethical boundaries. Figure 2.5 shows
what we expect to build in the end of this capstone project.

![](media/image4.png){width="4.700694444444444in"
height="0.6869564741907261in"}

Figure 2.5. The triage flow. This diagram shows how information moves
through the loop and how every transition is logged for replay.

2.6.1 What is triage?

Running a reconnaissance tool like nmap against a target is
straightforward. The hardest part comes afterward, when you're starting
at pages of output and you're trying to figure out what matters.

Even a small bug bounty scope generates a lot of noise: dozens of hosts,
common ports, repetitive service banners, and buried within all of that,
a few details that matter. At this stage, the bottleneck isn't your
tools; it's attention. This is where agents come in handy.

For our purposes, the agent never scans, probes, or exploits any network
resources. All reconnaissance has already been completed using tools you
already know and trust. The agent comes in after recon. It works
entirely on saved output files, and its job is simple: to review the
recon results and help you decide where to focus first.

For bug bounty hunters, this matters. Time spent scrolling through noise
is time not spent validating real findings. An AI agent does not replace
your skill or judgement. It removes friction from the lowest-value part
of your workflow so you can focus on what actually pays off.

2.6.2 nmap output

Let's look at what typical reconnaissance outputs look like. Assume
you've already identified a set of public-facing hostnames and scanned
them with nmap for basic service discovery. The network traffic has
already happened.

Listing 2.11 is a simplified, human-readable representation of the nmap
output:

Listing 2.11. nmap output

Host: api.example.com

80/tcp open http Apache httpd 2.4.41

443/tcp open https Apache httpd 2.4.41

8443/tcp open https Jetty 9.4.18

Host: admin.example.com

22/tcp open ssh OpenSSH 7.2p2

443/tcp open https nginx 1.18.0

Host: files.example.com

21/tcp open ftp vsftpd 3.0.3

80/tcp open http nginx 1.14.2

Host: legacy.example.com

23/tcp open telnet

80/tcp open http Apache httpd 2.2.34

Nothing here looks unusual at first glance. Most of it is familiar, and
that's exactly the problem. As scopes grow, output becomes repetitive.
Ports 80 and 443 appear everywhere. Web servers blur together. Version
strings stop meaning anything. The details that matter, such as unusual
ports, legacy services, and exposed admin interfaces get buried in the
noise.

This is where an AI agent helps. The agent doesn't need to understand
how nmap works or how the scan was configured. It simply treats the
output as a document and answers a narrow question: "Which hosts or
services stand out enough to justify further investigation?". No
exploitation. No scanning. No assumptions about what comes next.

nmap XML output in production workflows

In real bug bounty programs and client engagements, you'll typically use
structured output formats such as -oX (XML) or -oA (all formats). These
preserve additional metadata, such as timing information, script output,
and host states that can be useful in larger automation pipelines.

This chapter uses a simplified, human-readable representation to keep
the focus on how the agent makes decision, not on parsing complexity.
The same agent logic applies when consuming structured XML or JSON files
in production.

2.6.3 Agent decision scope and constraints

The agent's job is not to find vulnerabilities. That expectation is
unrealistic and sets you up for disappointment. Instead, the agent has a
much more practical role: reduce noise and surface signals so you can
make decisions faster and more consistency.

In practice, the agent performs a small number of well-defined tasks:

- Flags unusual exposure. Services and ports that do not appear
  everywhere. HTTPS on 443 is expected. An admin interface on 8443 or a
  legacy service on 21 or 23 is not.

- Spot odd combinations. Catch service pairings that do not belong
  together, such as public FTP alongside a web application or SSH
  exposed on a host that otherwise appears to serve only web traffic.

- Group similar hosts. Cluster hosts with identical service stacks so
  that you can avoid redundant testing while making outliers easier to
  spot.

- Surface red flags. Highlight legacy protocols, end-of-life software,
  and services that shouldn't be internet-facing. These are things
  experienced testers recognize instinctively. The agent makes that
  instinct explicit and repeatable.

The agent functions as a filter and reduces them to a short list of
hosts worth your attention. It also leaves a clear trail showing how it
reached those conclusions. This separation keeps the workflow safe,
scoped, and defensible while delivering value at the point where most
bug hunters lose time: the first pass through noisy recon data.

2.6.4 Triage artifacts

After reviewing your recon data, the agent produces something new: a
prioritized triage summary. This artifact is not a report or a
vulnerability list: it is a prioritized triage summary designed for
quick review. Based on the earlier nmap output, an example summary might
look like what's shown in Listing 2.12.

Listing 2.12. High-interest findings:

1\. legacy.example.com

\- Telnet (23/tcp) exposed publicly

\- Apache httpd 2.2.34 (end-of-life)

Reason: Multiple legacy services on a public host

2\. files.example.com

\- FTP (21/tcp) exposed alongside HTTP

Reason: Public FTP service paired with web server

3\. api.example.com

\- HTTPS service on 8443/tcp (Jetty 9.4.18)

Reason: Non-standard admin or management interface

Lower-interest findings:

\- admin.example.com

\- SSH (22/tcp) and HTTPS (443/tcp)

Reason: Common service combination with no immediate anomalies

This is the output that the agent is optimized to produce: concise,
opinionated, and easy to act on. There is no exploit speculation, no CVE
matching, and no severity scoring. Each item includes a brief
explanation of why it was flagged. This lets you agree, disagree, or dig
deeper. The reasoning is preserved, so when you return to this
engagement days later, you don't have to reconstruct your thinking from
memory.

For individual hunters, this changes how work begins. Instead of
re-reading raw scan output, you start with a focused list of the most
promising targets. For teams, the artifact can be a shared reference.
Triage decisions are transparent: anyone can see what was flagged and
why, making handoffs and collaboration easier. Figure 2.6 summarizes the
agent we've built.

![](media/image5.png){width="5.096347331583552in"
height="1.4606277340332459in"}

**Figure 2.**6. Triage agent summary. The agent transforms raw recon
output into a short, prioritized summary that highlights hosts and
services that require human attention.

2.6.5 Practical benefits and safety constraints

For bug hunters, the bottleneck in recon is rarely tooling; it is the
time and attention required to turn raw output into decisions. Scans
finish quickly. Triage does not. This workflow addresses that gap
directly.

The agent doesn't automate exploitation or replacing your judgment. It
handles the most repetitive part of the process: the first pass through
recon data. The agent applies the same reasoning an experienced tester
would: flagging anomalies, grouping similar hosts, and surfacing
outliers. However, the agent can do it consistently and without fatigue.

That consistency matters. When working large scopes or moving quickly,
it is easy to miss something obvious or spend too long chasing low-value
targets. The agent does not solve this by being smarter; it solves it by
being predictable. Every decision is recorded, and every flag has an
explanation.

This approach also avoids the pitfalls of so-called "AI-powered
scanning." The agent never touches the network, never expands scope, and
never probes targets. Everything it sees is data you already collected.
Everything it produces is an artifact you can inspect, share, or
discard. For newer bug hunters, this kind of agent acts as a forcing
function. It makes the reasoning behind recon triage explicit. Over
time, that feedback sharpens intuition instead of replacing it.

The agent does not find bugs, write reports, or make decisions you
cannot undo. It shortens the distance between "scan finished" and
"here's what deserves testing next." That is the appropriate role for
automation in offensive security, and it sets the foundation for the
multi-agent workflows introduced in the next chapter.

  ----------- ----------------------------------------- ---------
                                                        

                                                        

                                                        

                                                        
  ----------- ----------------------------------------- ---------

- 
- 
- 

2.  
3.  
4.  
5.  

- 
- 
- 
- 

***Summary***

- Agents wrap reasoning around action. Where an LLM predicts the next
  token, an agent predicts the next step---using tools, memory, and
  feedback to pursue a goal.

- The Minimal Agent Spec makes autonomy reproducible. A consistent
  schema for messages, tools, observations, and artifacts allows your
  agents to run anywhere and be inspected later.

- 

- Safety is engineered, not assumed. Gates, sandboxing, logging, and
  kill switches keep AI experimentation ethical and auditable.

- The Triage Agent demonstrates the full loop. It reasons about data,
  takes controlled action, records evidence, and reports findings---all
  within a defined scope.

- 
