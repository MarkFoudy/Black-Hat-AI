from adapters.langchain.agent import build_langchain_agent
from mytools import ping_host

agent_run = build_langchain_agent([ping_host])

targets = ["example.com", "no-such-host.local"]

def confirm(prompt: str) -> bool:
    reply = input(f"[Confirm] {prompt} (y/n): ")
    return reply.lower().startswith("y")

if confirm("Proceed with external ping tests?"):
    for host in targets:
        agent_run(f"Check reachability of {host}")
else:
    print("Aborted by user.")
