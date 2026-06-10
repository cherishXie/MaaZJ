#!/usr/bin/env node
import path from "node:path";
import { loadState, phaseAdvice, usage } from "./lib.mjs";

const taskDirArg = process.argv[2];
if (!taskDirArg) {
  usage(null, "Usage: node scripts/agent-workflow/advance.mjs .agent/tasks/<task-id>");
}

const taskDir = path.resolve(taskDirArg);

try {
  const state = loadState(taskDir);
  const advice = phaseAdvice(state);

  console.log(`# Next Agent: ${advice.agent}`);
  console.log("");
  console.log(`Task directory: ${taskDir}`);
  console.log(`Current phase: ${state.phase}`);
  console.log(`Workflow mode: ${state.workflow_mode}`);
  console.log("");
  console.log("## What to do");
  console.log("");
  console.log(advice.action);
  console.log("");
  console.log("## Suggested prompt");
  console.log("");
  console.log("请在 Codex 内使用 multi-agent-refactor 工作流，并显式读取以下任务目录推进到下一个确认点：");
  console.log("");
  console.log(`\`${taskDir}\``);
} catch (error) {
  usage(error.message, "Usage: node scripts/agent-workflow/advance.mjs .agent/tasks/<task-id>");
}
