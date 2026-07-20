# GPT Execution Canvas — ChatGPT App

Production-oriented ChatGPT Apps SDK implementation of the Execution Canvas lifecycle:

`Observe → Diagnose → Patch → Verify → Commit`

The app is deliberately approval-gated. Read operations can inspect and render execution evidence. Any state transition requires an existing, matching approval row in the server-only `execution` schema.

## Architecture

- **MCP server:** Node.js + `@modelcontextprotocol/sdk`, exposed at `/mcp`.
- **Widget:** portable MCP App HTML resource at `ui://execution-canvas/widget-v1.html`.
- **Persistence:** Supabase/PostgreSQL `execution` schema already defined by `supabase/migrations/20260719070132_execution_canvas_audit.sql`.
- **Security boundary:** Supabase service-role key is server-only. The widget receives no credentials.
- **Audit model:** lifecycle events are append-only; approvals are explicit and scoped.

## Tool surface

| Tool | Effect | Model/UI visibility |
|---|---|---|
| `get_execution_run` | Read run and audit events | model |
| `render_execution_canvas` | Render final state in widget | model + app |
| `request_execution_approval` | Create pending scoped approval | model + app |
| `decide_execution_approval` | Record explicit user decision | app only |
| `advance_execution_run` | Append event and advance an approved run | model + app |

The approval-decision tool is app-only so the visible Approve/Reject controls are the canonical human decision surface. The server still verifies approval state before any run transition.

## Local run

```bash
cp .env.example .env
npm install
npm run typecheck
npm run build
npm start
curl -fsS http://127.0.0.1:8787/healthz
```

For ChatGPT developer-mode testing, expose the server through an HTTPS tunnel and connect the resulting `/mcp` URL.

## Required secrets

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `PUBLIC_ORIGIN` — exact HTTPS widget/server origin used in Apps SDK resource metadata

Store secrets in the deployment provider's secret manager. Never commit them or place them in widget state, tool output, `_meta`, logs, or browser storage.

## Production gates

1. Install from a clean lockfile and pass `npm run typecheck` and `npm run build`.
2. Run MCP Inspector against `/mcp`; verify all descriptors, schemas, annotations, and widget resource metadata.
3. Confirm pending → approved/rejected idempotency.
4. Confirm `advance_execution_run` fails with `APPROVAL_REQUIRED` for missing or rejected approvals.
5. Confirm append-only event enforcement and cross-run approval rejection in PostgreSQL.
6. Test in ChatGPT developer mode through HTTPS.
7. Set a dedicated production domain and exact CSP allowlists.
8. Complete OAuth/org verification if public submission requires user-specific identity.
9. Run security review, abuse tests, privacy-policy review, and submission checklist.

## Design decision

This app uses a decoupled data/render flow: `get_execution_run` returns reusable structured data, then `render_execution_canvas` mounts the UI. This avoids remounting the widget for every read and lets the model reason about evidence before presentation.

## Current boundary

This branch implements the production vertical slice and database-backed approval path. Deployment, ChatGPT connector registration, organization verification, and any signing/identity confirmation remain human approval steps.
