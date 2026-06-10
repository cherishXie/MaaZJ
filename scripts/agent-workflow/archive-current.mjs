#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { WORKFLOW_FILES, loadState, nextArchivePath, usage } from "./lib.mjs";

const taskDirArg = process.argv[2];
const fileKey = process.argv[3];

if (!taskDirArg || !fileKey) {
  usage(null, "Usage: node scripts/agent-workflow/archive-current.mjs .agent/tasks/<task-id> <task|plan|review|decision|implementation|test|final>");
}

if (!WORKFLOW_FILES.includes(fileKey)) {
  usage(`unsupported file key: ${fileKey}`, "Usage: node scripts/agent-workflow/archive-current.mjs .agent/tasks/<task-id> <task|plan|review|decision|implementation|test|final>");
}

const taskDir = path.resolve(taskDirArg);

try {
  const state = loadState(taskDir);
  const source = path.join(taskDir, `${fileKey}.md`);
  if (!fs.existsSync(source)) {
    throw new Error(`source file does not exist: ${source}`);
  }

  const versionField = `${fileKey}_version`;
  const fallbackVersion = fileKey === "plan"
    ? state.plan_version
    : fileKey === "review"
      ? state.review_version
      : fileKey === "implementation"
        ? state.implementation_version
        : 1;

  const target = nextArchivePath(taskDir, fileKey, state[versionField] || fallbackVersion);
  fs.copyFileSync(source, target);
  console.log(`Archived ${source} -> ${target}`);
} catch (error) {
  usage(error.message, "Usage: node scripts/agent-workflow/archive-current.mjs .agent/tasks/<task-id> <task|plan|review|decision|implementation|test|final>");
}
