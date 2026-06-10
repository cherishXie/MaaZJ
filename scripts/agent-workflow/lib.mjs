import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const WORKFLOW_FILES = [
  "task",
  "plan",
  "review",
  "decision",
  "implementation",
  "test",
  "final"
];

export function usage(message, text) {
  if (message) {
    console.error(`Error: ${message}`);
  }
  console.error(text);
  process.exit(1);
}

export function repoRootFromScript() {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
}

export function normalizeSlug(input) {
  const slug = String(input || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, "-")
    .replace(/^-+|-+$/g, "");

  return slug || "task";
}

export function todayId(date = new Date()) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export function currentTaskPath(repoRoot) {
  return path.join(repoRoot, ".agent", "current-task.json");
}

export function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

export function writeNewFile(filePath, content) {
  if (fs.existsSync(filePath)) {
    throw new Error(`file already exists: ${filePath}`);
  }
  fs.writeFileSync(filePath, content, "utf8");
}

export function renderTemplate(template, values) {
  return template.replace(/\{\{([a-zA-Z0-9_]+)\}\}/g, (match, key) => {
    return Object.prototype.hasOwnProperty.call(values, key) ? values[key] : match;
  });
}

export function ensureStateDefaults(state) {
  return {
    task_id: state.task_id || "",
    title: state.title || "",
    phase: state.phase || "created",
    next_agent: Object.prototype.hasOwnProperty.call(state, "next_agent")
      ? state.next_agent
      : "planner",
    workflow_mode: state.workflow_mode || "safe",
    plan_version: Number(state.plan_version) || 0,
    review_version: Number(state.review_version) || 0,
    implementation_version: Number(state.implementation_version) || 0,
    approved: Boolean(state.approved),
    blocked: Boolean(state.blocked),
    manual_approval_required: state.manual_approval_required !== false,
    confirmation_required: Boolean(state.confirmation_required),
    confirmation_reason: state.confirmation_reason || "",
    created_at: state.created_at || new Date().toISOString(),
    updated_at: state.updated_at || new Date().toISOString(),
    last_decision: state.last_decision || "",
    last_error: state.last_error || ""
  };
}

export function loadState(taskDir) {
  const statePath = path.join(taskDir, "state.json");
  if (!fs.existsSync(taskDir)) {
    throw new Error(`task directory does not exist: ${taskDir}`);
  }
  if (!fs.existsSync(statePath)) {
    throw new Error(`state.json does not exist: ${statePath}`);
  }

  try {
    return ensureStateDefaults(JSON.parse(readText(statePath)));
  } catch (error) {
    throw new Error(`state.json is not valid JSON: ${error.message}`);
  }
}

export function saveState(taskDir, state) {
  const statePath = path.join(taskDir, "state.json");
  const nextState = ensureStateDefaults(state);
  nextState.updated_at = new Date().toISOString();
  fs.writeFileSync(statePath, `${JSON.stringify(nextState, null, 2)}\n`, "utf8");
}

export function uniqueTaskDir(repoRoot, baseTaskId) {
  const tasksRoot = path.join(repoRoot, ".agent", "tasks");
  let taskId = baseTaskId;
  let taskDir = path.join(tasksRoot, taskId);
  let index = 2;

  while (fs.existsSync(taskDir)) {
    taskId = `${baseTaskId}-${index}`;
    taskDir = path.join(tasksRoot, taskId);
    index += 1;
  }

  return { taskId, taskDir };
}

export function writeCurrentTask(repoRoot, state, taskDir) {
  const relativeTaskDir = path.relative(repoRoot, taskDir).replace(/\\/g, "/");
  const payload = {
    task_dir: relativeTaskDir,
    task_id: state.task_id,
    title: state.title,
    updated_at: new Date().toISOString()
  };
  fs.writeFileSync(currentTaskPath(repoRoot), `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

export function phaseAdvice(state) {
  const table = {
    created: {
      agent: "planner",
      action: "读取 task.md 和 state.json，产出 plan.md，并将 phase 更新为 plan_review。"
    },
    planning: {
      agent: "planner",
      action: "继续完善 plan.md，并将 phase 更新为 plan_review。"
    },
    plan_review: {
      agent: "reviewer",
      action: "审查 plan.md，产出 review.md；approved 则进入 approved，否则进入 plan_revision。"
    },
    plan_revision: {
      agent: "planner",
      action: "根据 review.md 修订 plan.md，产出 decision.md，再回到 plan_review。"
    },
    approved: {
      agent: "implementer",
      action: "按 plan.md 实现最小必要改动，产出 implementation.md，进入 code_review。"
    },
    implementing: {
      agent: "implementer",
      action: "根据 code review 的 must-fix 修复，更新 implementation.md，回到 code_review。"
    },
    code_review: {
      agent: "reviewer",
      action: "审查当前 diff；有 must-fix 回 implementing，通过则进入 testing。"
    },
    testing: {
      agent: "tester",
      action: "运行可用检查并产出 test.md；通过进入 done，失败进入 implementing 或 blocked。"
    },
    done: {
      agent: "summarizer",
      action: "读取任务文件和 diff，产出 final.md，并保持 phase 为 done。"
    },
    blocked: {
      agent: state.next_agent || "user",
      action: "先处理 state.json 中 last_error 和 confirmation_reason 描述的阻塞项。"
    }
  };

  return table[state.phase] || {
    agent: state.next_agent || "unknown",
    action: `未知 phase: ${state.phase}。请检查 state.json。`
  };
}

export function nextArchivePath(taskDir, baseName, version) {
  const archiveDir = path.join(taskDir, "archive");
  fs.mkdirSync(archiveDir, { recursive: true });

  const ext = baseName === "state" ? "json" : "md";
  let index = Number(version) || 0;
  if (index <= 0) {
    index = 1;
  }

  let candidate = path.join(archiveDir, `${baseName}-v${index}.${ext}`);
  while (fs.existsSync(candidate)) {
    index += 1;
    candidate = path.join(archiveDir, `${baseName}-v${index}.${ext}`);
  }
  return candidate;
}
