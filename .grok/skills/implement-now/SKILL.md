---
name: implement-now
description: "Forces the agent into pure implementation mode. No more planning questions, no more 'what do you want first', no more clarification loops. The agent must start writing real code immediately for the requested feature and keep shipping working increments without asking unless truly blocked on a hard technical unknown."
version: 0.1
author: User + Grok
tags: [meta, productivity, implementation, focus]
---

## Invocation

When the user says something like:
- "implement-now"
- "just do it"
- "stop asking and code"
- "/implement-now"

The agent must:
1. Immediately switch to pure coding mode.
2. Stop asking clarifying questions about priority/order/details unless the code literally cannot compile or run without a decision.
3. Deliver working code changes in small, testable increments.
4. Use the existing `todo_write` tool internally to track progress instead of asking the user.
5. Default to "make it work end-to-end for the happy path first", then iterate.

This skill exists because the user wants the agent to behave more like a senior implementer who ships instead of an over-cautious architect who keeps asking for the next micro-decision.

## Behavior Contract

- Every response after this skill is invoked should contain **actual code edits** or **clear "here is the next diff"** style progress.
- Questions are only allowed when the agent is genuinely stuck (e.g. "this API doesn't exist yet — do you want me to add it or use the lower level one?").
- Otherwise: code, test mentally, show the change, ask "next increment?" only after a working piece lands.

This is the "Minecrafty dawg — just place the block" mode.