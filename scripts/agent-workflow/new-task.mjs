#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import {
  repoRootFromScript,
  normalizeSlug,
  todayId,
  readText,
  writeNewFile,
  renderTemplate,
  uniqueTaskDir,
  writeCurrentTask,
  loadState,
  usage
} from "./lib.mjs";

const titleInput = process.argv.slice(2).join(" ").trim();
if (!titleInput) {
  usage(null, 'Usage: node scripts/agent-workflow/new-task.mjs "task title or slug"');
}

const repoRoot = repoRootFromScript();
const baseTaskId = `${todayId()}-${normalizeSlug(titleInput)}`;
const { taskId, taskDir } = uniqueTaskDir(repoRoot, baseTaskId);
const templateDir = path.join(repoRoot, ".agent", "templates");
const timestamp = new Date().toISOString();
const values = {
  task_id: taskId,
  title: titleInput,
  request: titleInput,
  timestamp
};

fs.mkdirSync(path.join(taskDir, "archive"), { recursive: true });

const files = [
  ["task.template.md", "task.md"],
  ["state.template.json", "state.json"],
  ["plan.template.md", "plan.md"],
  ["review.template.md", "review.md"],
  ["decision.template.md", "decision.md"],
  ["implementation.template.md", "implementation.md"],
  ["test.template.md", "test.md"],
  ["final.template.md", "final.md"]
];

try {
  for (const [templateName, outputName] of files) {
    const templatePath = path.join(templateDir, templateName);
    if (!fs.existsSync(templatePath)) {
      throw new Error(`template does not exist: ${templatePath}`);
    }
    const rendered = renderTemplate(readText(templatePath), values);
    writeNewFile(path.join(taskDir, outputName), rendered);
  }

  const state = loadState(taskDir);
  writeCurrentTask(repoRoot, state, taskDir);
} catch (error) {
  usage(error.message, 'Usage: node scripts/agent-workflow/new-task.mjs "task title or slug"');
}

console.log(`Created task: .agent/tasks/${taskId}`);
console.log("Current task updated: .agent/current-task.json");
console.log(`Next: fill .agent/tasks/${taskId}/task.md, then continue in Codex with multi-agent-refactor.`);
