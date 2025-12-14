from adapters.langchain.agent import build_langchain_agent
from mytools import ping_host

agent_run = build_langchain_agent([ping_host])

targets = ["example.com", "no-such-host.local"]

for host in targets:
    print(">>", agent_run(f"Check reachability of {host}"))
