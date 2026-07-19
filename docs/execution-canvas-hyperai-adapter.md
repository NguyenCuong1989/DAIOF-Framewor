# Execution Canvas HyperAI adapter contract

## Purpose

The native Chat view writes sanitized lifecycle events to a durable local outbox. Delivery is asynchronous and must never block model execution, tools, approvals, checkpoints, or the existing VS Code session store.

## Native configuration

- `chat.executionCanvas.audit.enabled`: boolean, default `false`.
- `chat.executionCanvas.audit.endpoint`: loopback HTTP endpoint, default `http://127.0.0.1:9001/api/v1/execution-canvas/events`.
- Non-loopback endpoints are rejected by the native adapter.
- No Supabase credential is accepted or stored by the native application.

## Request

`POST /api/v1/execution-canvas/events`

```json
{
  "version": 1,
  "events": [
    {
      "id": "uuid",
      "sessionId": "native-session-reference",
      "sequenceNo": 0,
      "stage": "observe",
      "eventKind": "addRequest",
      "status": "running",
      "occurredAt": "2026-07-19T00:00:00.000Z",
      "payload": {}
    }
  ]
}
```

Limits enforced by the native side:

- 32 events per request.
- 512 events retained in the workspace outbox.
- 2 second request timeout.
- Payload values are scalar only; prompts, responses, tool payloads, file contents, and credentials are excluded.
- Sequence state persists across application restarts.

## Backend obligations

HyperAI API must:

1. Authenticate the local caller using the node-level mechanism already owned by HyperAI; never accept a Supabase service key from the renderer.
2. Reject unknown request versions and malformed batches.
3. Treat `event.id` as the idempotency key and return success for an already accepted event.
4. Resolve or create the authorized workspace, session, and run mapping.
5. Insert events in sequence order and preserve the database append-only rule.
6. Return a non-2xx response if the full batch is not durably accepted.
7. Log only IDs, counts, status codes, and timing; never log raw event payloads.
8. Use the backend-held Supabase service-role credential.

## Success response

Any 2xx response means every event in the submitted batch is durably accepted or was previously accepted. Partial success is prohibited in version 1.

```json
{
  "version": 1,
  "accepted": 5,
  "duplicates": 0
}
```

## Failure behavior

- Network failure, timeout, or non-2xx: retain the batch in the local outbox.
- Outbox overflow: drop the oldest events and emit a local warning.
- Invalid/non-loopback endpoint: refuse delivery and retain the outbox.
- Chat execution continues in all adapter failure modes.

## Rollout gate

1. Native compile and unit tests.
2. HyperAI endpoint contract tests.
3. Offline/restart/outbox overflow tests.
4. Idempotent replay test.
5. Supabase row parity against native event trace.
6. Enable audit flag on Titan GT77 only.
7. Keep database read path disabled until parity and rollback tests pass.
