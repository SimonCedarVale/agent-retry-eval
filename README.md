# Agent Retry Evaluation

A small Python harness for comparing a retry with failure feedback against a retry with the same feedback plus an explicit reflection. Both branches start from one shared failed attempt and get one retry. The CLI runs a deterministic mock file lookup. Its outcomes demonstrate the evaluation pipeline. A live-model experiment is a separate next step.

## Run locally

Python 3.10 or newer. The prototype uses the standard library.

```sh
python3 -m unittest -v
python3 retry_eval.py
```

- `artifacts/retry_results.jsonl` records the shared failure and both retries with their inputs, task outcome, and simulated tool calls.
- `artifacts/summary.md` summarizes the comparison. The scripted baseline deliberately repeats the failed lookup so both result paths are exercised.

GitHub Actions runs the same commands on pushes and pull requests. You can also run **Retry evaluation** manually from the Actions tab. The run publishes a job summary and a downloadable `retry-eval` artifact.

## Connect a Devin Bot

1. [Connect GitHub](https://docs.devin.ai/integrations/gh) to Devin and select this repository.
2. Tell your [Devin Bot](https://docs.devin.ai/work-with-devin/bots) which repository it owns for this task, then send the instructions below. Run the task once in chat before asking the Bot to repeat it on Mondays through [Devin Automations](https://docs.devin.ai/product-guides/automations).

> Check out the default branch of this repository. Run `python3 -m unittest -v` and then `python3 retry_eval.py`. Read `artifacts/summary.md` and `artifacts/retry_results.jsonl`. Reply in this chat with the commit SHA, whether the tests passed, and the baseline and reflection outcomes and tool-call counts. Clearly label them as scripted mock results. If a command fails, report the first failing command and its error. Keep the run read-only.

The GitHub workflow and Bot use the same command and report format. The workflow checks each code change. The Bot reports the results for the default branch on the reading schedule. The Bot connection and automation are account-side setup steps.

## Extend the experiment

Pass your own attempt, reflection, and success-check callbacks to `compare_retries`. For a live experiment, keep model, task state, tool access, failure feedback, and retry budget identical across both branches. Reset tool state for each branch if the task mutates it. Record reflection generation cost separately and report success and cost across a set of tasks.

Background: [ReAct](https://arxiv.org/abs/2210.03629) and [Reflexion](https://arxiv.org/abs/2303.11366). The harness isolates whether supplying a reflection changes the retry and illustrates one part of the research setup.
