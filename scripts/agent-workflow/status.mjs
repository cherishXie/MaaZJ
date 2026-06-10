#!/usr/bin/env node
import path from "node:path";
import { loadState, phaseAdvice, usage } from "./lib.mjs";

const taskDirArg = process.argv[2];
if (!taskDirArg) {
  usage(null, "Usage: node scripts/agent-workflow/status.mjs .agent/tasks/<task-id>");
}

const taskDir = path.resolve(taskDirArg);

try {
  const state = loadState(taskDir);
  const advice = phaseAdvice(state);

  console.log(`Task: ${state.task_id}`);
  console.log(`Title: ${state.title}`);
  console.log(`Phase: ${state.phase}`);
  console.log(`Next agent: ${state.next_agent || advice.agent}`);
  console.log(`Workflow mode: ${state.workflow_mode}`);
  console.log(`Versions: plan=${state.plan_version}, review=${state.review_version}, implementation=${state.implementation_version}`);
  console.log(`Approved: ${Boolean(state.approved)}`);
  console.log(`Blocked: ${Boolean(state.blocked)}`);
  console.log(`Manual approval required: ${Boolean(state.manual_approval_required)}`);
  console.log(`Confirmation required: ${Boolean(state.confirmation_required)}`);
  if (state.confirmation_reason) {
    console.log(`Confirmation reason: ${state.confirmation_reason}`);
  }
  if (state.last_decision) {
    console.log(`Last decision: ${state.last_decision}`);
  }
  if (state.last_error) {
    console.log(`Last error: ${state.last_error}`);
  }
  console.log(`Next step: ${advice.action}`);
} catch (error) {
  usage(error.message, "Usage: node scripts/agent-workflow/status.mjs .agent/tasks/<task-id>");
}
