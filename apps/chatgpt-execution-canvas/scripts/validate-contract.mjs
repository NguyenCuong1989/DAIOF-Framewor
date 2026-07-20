import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const required = [
  'server/index.ts',
  'server/store.ts',
  'server/skillRouter.ts',
  'web/widget.html',
  'vercel.json',
  '.env.example',
];

const failures = [];
for (const relative of required) {
  try {
    await readFile(resolve(root, relative));
  } catch {
    failures.push(`MISSING:${relative}`);
  }
}

const server = await readFile(resolve(root, 'server/index.ts'), 'utf8');
for (const tool of [
  'get_execution_run',
  'render_execution_canvas',
  'request_execution_approval',
  'decide_execution_approval',
  'advance_execution_run',
]) {
  if (!server.includes(`registerTool('${tool}'`)) failures.push(`TOOL_NOT_REGISTERED:${tool}`);
}

for (const invariant of [
  'text/html;profile=mcp-app',
  'openai/outputTemplate',
  'destructiveHint: true',
  "app.disable('x-powered-by')",
  "express.json({ limit: '256kb' })",
]) {
  if (!server.includes(invariant)) failures.push(`INVARIANT_MISSING:${invariant}`);
}

const router = await readFile(resolve(root, 'server/skillRouter.ts'), 'utf8');
for (const skill of ['find-skills', 'mcp-builder', 'session-logs', 'deploy-to-vercel']) {
  if (!router.includes(`id: '${skill}'`)) failures.push(`SKILL_NOT_ROUTED:${skill}`);
}

if (failures.length) {
  console.error(failures.join('\n'));
  process.exit(1);
}

console.log('EXECUTION_CANVAS_PRODUCTION_CONTRACT=PASS');
