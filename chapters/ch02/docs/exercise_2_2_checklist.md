# Exercise 2.2 — Safety Checklist

Before running any agent against a real target, verify every item below.
Check each box as you confirm it.

## Pre-run checklist

- [ ] **Scope defined** — you have written authorisation that names the specific
      systems and IP ranges in scope. Nothing outside that list will be touched.

- [ ] **Sandbox verified** — the agent is running in an isolated environment
      (dedicated VM, container, or air-gapped host). No production credentials
      or sensitive data are present in the environment.

- [ ] **Safety gate configured** — `safety_gate` (Listing 2.8) is wired into
      every action that touches a target. The `prohibited_targets` set in
      `src/safety/gates.py` has been updated to include your production
      hostnames before this run.

- [ ] **Logging enabled** — `ArtifactLogger` (Listing 2.5) is active and
      writing to a persistent directory. You know where the log file is and
      can retrieve it after the run (`logger.path`).

- [ ] **Kill switch active** — `KillSwitch` (Listing 2.10) has been started
      (`kill_switch.start()`) and every agent loop checks `kill_switch.is_active`
      before each iteration. You have a terminal window open and ready to type
      `STOP`.

## After the run

- [ ] Review `runs/<uuid>.jsonl` for any unexpected actions.
- [ ] Retain the log file for the engagement record.
- [ ] Tear down the sandbox environment.
