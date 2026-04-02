---
name: lms
description: Use the LMS tools to interact with the Learning Management System backend
always: true
---

# LMS Skill

Use the LMS tools to interact with the Learning Management System backend.

## Available Tools

- `mcp_lms_lms_labs` — Get the list of available labs
- `mcp_lms_lms_health` — Check the LMS backend health
- `mcp_lms_lms_scores` — Get scores for a specific lab or all labs
- `mcp_lms_lms_learners` — Get learner information

## Usage Patterns

### When user asks about labs

When the user asks about available labs or wants to choose a lab:

1. Call `mcp_lms_lms_labs()` to get the list of labs
2. If the user needs to choose a lab and there are multiple options, use `mcp_webchat_ui_message` with `type: "choice"` to present the lab options as structured UI choices
3. Each choice should have:
   - `label`: Short, readable lab name (e.g., "Lab 01 – Products, Architecture & Roles")
   - `value`: The lab identifier that can be used in follow-up tool calls

### When user asks about health

When the user asks if the backend is healthy or how the system is doing:

1. Call `mcp_lms_lms_health()` to check the backend status
2. Report the health status and any relevant metrics (e.g., number of items in the system)

### When user asks about scores

When the user asks about scores:

1. If a specific lab is mentioned, call `mcp_lms_lms_scores(lab="<lab_name>")`
2. If no lab is specified and there are multiple labs, use `mcp_webchat_ui_message` with `type: "choice"` to let the user select which lab's scores to view
3. If no lab is specified but you want to show all scores, call `mcp_lms_lms_scores()` without arguments and format the results in a readable table

### When user asks about learners

When the user asks about learners or group performance:

1. Call `mcp_lms_lms_learners()` with appropriate filters
2. Present the results in a clear, structured format

## Cooperation with Structured UI

This skill cooperates with the shared `structured-ui` skill by:

1. Providing short, readable lab labels for choice prompts
2. Providing stable lab values that can be reused in follow-up tool calls
3. Using `mcp_webchat_ui_message` for interactive choices when the user needs to select among multiple options
4. Falling back to plain text responses when there's only one sensible option or when the channel doesn't support structured UI

## Example Interactions

**User:** "What labs are available?"
**Agent:** Calls `mcp_lms_lms_labs()` and presents the list.

**User:** "Show me the scores" (without specifying a lab)
**Agent:** Uses `mcp_webchat_ui_message` with a choice of labs, or calls `mcp_lms_lms_scores()` for all labs if appropriate.

**User:** "Is the LMS backend healthy?"
**Agent:** Calls `mcp_lms_lms_health()` and reports the status.

**User:** "Lab 01" (after being shown a choice)
**Agent:** Calls `mcp_lms_lms_scores(lab="Lab 01")` or the appropriate tool with the selected lab value.
