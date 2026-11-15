---
name: om-assist
description: >-
  Starts the om side assistant when the owner types /om-assist, so side questions go to their own thread and the main chat stays clean. The assistant never messages the main agent.
---

# om-assist launcher

Only when the owner types `/om-assist`.

1. Start the `om-assist` agent once (`invoke_subagent` or the host's subagent tool), with a short summary of the workspace, the plan file path if any, and the current task. Tell it to greet the owner in its own thread and never message the main agent.
2. Reply in one line with its link: `Assistant ready: [om-assist](conversation://<id>)`.
3. Do not poll it.
