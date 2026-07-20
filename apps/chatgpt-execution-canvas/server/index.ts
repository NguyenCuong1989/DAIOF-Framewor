import cors from 'cors';
import express, { type Request, type Response } from 'express';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';
import { planAgentMission } from './agent.js';
import { ExecutionStore } from './store.js';

const PORT = Number(process.env.PORT ?? 8787);
const PUBLIC_ORIGIN = process.env.PUBLIC_ORIGIN ?? `http://localhost:${PORT}`;
const TEMPLATE_URI = 'ui://execution-canvas/widget-v1.html';
const here = dirname(fileURLToPath(import.meta.url));

const stageSchema = z.enum(['observe', 'diagnose', 'patch', 'verify', 'commit']);
const statusSchema = z.enum(['queued', 'running', 'passed', 'failed', 'canceled']);

async function loadWidget(): Promise<string> {
  const candidates = [
    resolve(process.cwd(), 'web/widget.html'),
    resolve(process.cwd(), 'apps/chatgpt-execution-canvas/web/widget.html'),
    resolve(here, '../web/widget.html'),
  ];
  for (const candidate of candidates) {
    try { return await readFile(candidate, 'utf8'); } catch { /* try next */ }
  }
  throw new Error('WIDGET_TEMPLATE_NOT_FOUND');
}

function textResult(structuredContent: Record<string, unknown>, text: string, meta?: Record<string, unknown>) {
  return { structuredContent, content: [{ type: 'text' as const, text }], ...(meta ? { _meta: meta } : {}) };
}

async function createMcpServer() {
  const store = new ExecutionStore();
  const server = new McpServer({ name: 'GPT Execution Canvas', version: '0.4.0' }, { capabilities: { tools: {}, resources: {} } });

  server.registerResource('execution-canvas-widget', TEMPLATE_URI, {}, async () => ({
    contents: [{
      uri: TEMPLATE_URI,
      mimeType: 'text/html;profile=mcp-app',
      text: await loadWidget(),
      _meta: {
        ui: { prefersBorder: true, domain: PUBLIC_ORIGIN, csp: { connectDomains: [PUBLIC_ORIGIN], resourceDomains: [PUBLIC_ORIGIN] } },
        'openai/widgetDescription': 'Conversational IDE agent with automatic skill routing, approval-gated writes, audit evidence, and explicit commit control.',
        'openai/widgetPrefersBorder': true,
        'openai/widgetDomain': PUBLIC_ORIGIN,
      },
    }],
  }));

  server.registerTool('execute_agent_mission', {
    title: 'Execute an IDE agent mission',
    description: 'Primary entry point. Give the agent one natural-language request. It classifies the mission, selects the required skills, runs safe read-only work automatically, and stops only at a real write or external-effect approval boundary.',
    inputSchema: {
      message: z.string().min(1).max(4000),
      workspace: z.object({
        repository: z.string().max(240).optional(),
        gitRef: z.string().max(240).optional(),
        targetNode: z.string().max(160).optional(),
      }).optional(),
    },
    outputSchema: {
      mission: z.string(),
      summary: z.string(),
      skillChain: z.array(z.string()),
      approval: z.enum(['none', 'write', 'external-effect']),
      steps: z.array(z.record(z.string(), z.unknown())),
      workspace: z.record(z.string(), z.unknown()),
    },
    annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: true, idempotentHint: true },
    _meta: {
      ui: { resourceUri: TEMPLATE_URI, visibility: ['model', 'app'] },
      'openai/outputTemplate': TEMPLATE_URI,
      'openai/widgetAccessible': true,
      'openai/toolInvocation/invoking': 'Routing skills and preparing the mission…',
      'openai/toolInvocation/invoked': 'Mission prepared',
    },
  }, async ({ message, workspace }) => {
    const plan = planAgentMission(message);
    const next = plan.approval === 'none'
      ? 'Safe steps can run automatically.'
      : plan.approval === 'write'
        ? 'Proceed automatically through analysis and stop once for the scoped workspace write.'
        : 'Proceed automatically through build and verification and stop once before the external effect.';
    return textResult({ ...plan, workspace: workspace ?? {} }, `${plan.mission}: ${plan.skillChain.join(' → ')}. ${next}`);
  });

  server.registerTool('get_execution_run', {
    title: 'Get execution run',
    description: 'Inspect one execution run, lifecycle stage, approval state, and audit events without changing anything.',
    inputSchema: { runId: z.string().uuid() },
    outputSchema: { run: z.record(z.string(), z.unknown()), events: z.array(z.record(z.string(), z.unknown())) },
    annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  }, async ({ runId }) => {
    const [run, events] = await Promise.all([store.getRun(runId), store.listEvents(runId)]);
    return textResult({ run, events }, `Loaded run ${runId} at stage ${run.current_stage}.`);
  });

  server.registerTool('render_execution_canvas', {
    title: 'Render execution canvas',
    description: 'Render an execution run after its data has been loaded.',
    inputSchema: { run: z.record(z.string(), z.unknown()), events: z.array(z.record(z.string(), z.unknown())), approval: z.record(z.string(), z.unknown()).optional() },
    outputSchema: { run: z.record(z.string(), z.unknown()), events: z.array(z.record(z.string(), z.unknown())), approval: z.record(z.string(), z.unknown()).optional() },
    annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
    _meta: { ui: { resourceUri: TEMPLATE_URI, visibility: ['model', 'app'] }, 'openai/outputTemplate': TEMPLATE_URI, 'openai/widgetAccessible': true },
  }, async ({ run, events, approval }) => textResult({ run, events, ...(approval ? { approval } : {}) }, `Rendered execution run ${String(run.id ?? '')}.`));

  server.registerTool('request_execution_approval', {
    title: 'Request execution approval',
    description: 'Create one narrowly scoped pending approval immediately before a workspace write or external effect.',
    inputSchema: { runId: z.string().uuid(), scope: z.object({ action: z.string().min(1).max(160), target: z.string().min(1).max(320), summary: z.string().min(1).max(1200), risk: z.enum(['low', 'medium', 'high']) }) },
    outputSchema: { approval: z.record(z.string(), z.unknown()) },
    annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false, idempotentHint: false },
    _meta: { ui: { resourceUri: TEMPLATE_URI, visibility: ['model', 'app'] }, 'openai/outputTemplate': TEMPLATE_URI, 'openai/widgetAccessible': true },
  }, async ({ runId, scope }) => {
    const approval = await store.requestApproval(runId, scope);
    const [run, events] = await Promise.all([store.getRun(runId), store.listEvents(runId)]);
    return textResult({ approval }, `Approval ${approval.id} is pending for ${scope.action}.`, { run, events, approval });
  });

  server.registerTool('decide_execution_approval', {
    title: 'Approve or reject execution',
    description: 'Record the user decision for the exact displayed action.',
    inputSchema: { approvalId: z.string().uuid(), decision: z.enum(['approved', 'rejected']) },
    outputSchema: { approval: z.record(z.string(), z.unknown()) },
    annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false, idempotentHint: true },
    _meta: { ui: { resourceUri: TEMPLATE_URI, visibility: ['app'] }, 'openai/outputTemplate': TEMPLATE_URI, 'openai/widgetAccessible': true },
  }, async ({ approvalId, decision }) => {
    const approval = await store.decideApproval(approvalId, decision);
    const [run, events] = await Promise.all([store.getRun(approval.run_id), store.listEvents(approval.run_id)]);
    return textResult({ approval }, `Approval ${approval.id} is ${approval.decision}.`, { run, events, approval });
  });

  server.registerTool('advance_execution_run', {
    title: 'Advance approved execution run',
    description: 'Append a verified lifecycle event and advance a run only after matching explicit approval.',
    inputSchema: { runId: z.string().uuid(), approvalId: z.string().uuid(), stage: stageSchema, status: statusSchema, eventKind: z.string().min(1).max(96), payload: z.record(z.string(), z.union([z.string(), z.number(), z.boolean(), z.null()])).optional() },
    outputSchema: { run: z.record(z.string(), z.unknown()), events: z.array(z.record(z.string(), z.unknown())) },
    annotations: { readOnlyHint: false, destructiveHint: true, openWorldHint: false, idempotentHint: false },
    _meta: { ui: { resourceUri: TEMPLATE_URI, visibility: ['model', 'app'] }, 'openai/outputTemplate': TEMPLATE_URI, 'openai/widgetAccessible': true },
  }, async (input) => {
    const run = await store.advanceRun(input);
    const events = await store.listEvents(input.runId);
    return textResult({ run, events }, `Run ${run.id} advanced to ${run.current_stage} with status ${run.status}.`);
  });

  return server;
}

export const app = express();
app.disable('x-powered-by');
app.use(cors({ origin: false }));
app.use(express.json({ limit: '256kb' }));
app.get('/healthz', (_req, res) => res.json({ ok: true, service: 'gpt-execution-canvas', version: '0.4.0' }));
app.all('/mcp', async (req: Request, res: Response) => {
  const server = await createMcpServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  res.on('close', () => { void transport.close(); void server.close(); });
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});
app.use((error: unknown, _req: Request, res: Response, _next: unknown) => {
  const message = error instanceof Error ? error.message : 'Internal error';
  console.error(JSON.stringify({ level: 'error', message }));
  res.status(message.includes('APPROVAL_') ? 409 : 500).json({ error: message });
});

if (!process.env.VERCEL) {
  app.listen(PORT, '0.0.0.0', () => console.log(JSON.stringify({ level: 'info', event: 'server_started', port: PORT, origin: PUBLIC_ORIGIN })));
}

export default app;
