-- Execution Canvas control-plane persistence.
-- Server-only by design: no browser role receives schema access.

create schema if not exists execution;

revoke all on schema execution from public, anon, authenticated;
grant usage on schema execution to service_role;

create table execution.workspaces (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete restrict,
  name text not null check (char_length(name) between 1 and 120),
  created_at timestamptz not null default now(),
  archived_at timestamptz,
  constraint workspaces_archive_after_create check (archived_at is null or archived_at >= created_at)
);

create table execution.workspace_members (
  workspace_id uuid not null references execution.workspaces(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('owner', 'admin', 'operator', 'viewer')),
  created_at timestamptz not null default now(),
  primary key (workspace_id, user_id)
);

create table execution.sessions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references execution.workspaces(id) on delete cascade,
  created_by uuid not null references auth.users(id) on delete restrict,
  external_session_ref text not null check (char_length(external_session_ref) between 1 and 256),
  title text check (title is null or char_length(title) <= 240),
  status text not null default 'active' check (status in ('active', 'archived', 'failed')),
  created_at timestamptz not null default now(),
  archived_at timestamptz,
  unique (workspace_id, external_session_ref),
  constraint sessions_archive_after_create check (archived_at is null or archived_at >= created_at)
);

create table execution.runs (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references execution.sessions(id) on delete cascade,
  request_ref text check (request_ref is null or char_length(request_ref) <= 256),
  model_ref text check (model_ref is null or char_length(model_ref) <= 160),
  target_node text check (target_node is null or char_length(target_node) <= 160),
  repository text check (repository is null or char_length(repository) <= 320),
  git_ref text check (git_ref is null or char_length(git_ref) <= 320),
  commit_sha text check (commit_sha is null or commit_sha ~ '^[0-9a-f]{7,64}$'),
  current_stage text not null default 'observe'
    check (current_stage in ('observe', 'diagnose', 'patch', 'verify', 'commit')),
  status text not null default 'running'
    check (status in ('queued', 'running', 'passed', 'failed', 'canceled')),
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  constraint runs_complete_after_start check (completed_at is null or completed_at >= started_at)
);

create table execution.approvals (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references execution.runs(id) on delete cascade,
  requested_by uuid references auth.users(id) on delete set null,
  decided_by uuid references auth.users(id) on delete set null,
  scope jsonb not null default '{}'::jsonb check (jsonb_typeof(scope) = 'object'),
  decision text not null default 'pending'
    check (decision in ('pending', 'approved', 'rejected', 'expired', 'canceled')),
  requested_at timestamptz not null default now(),
  decided_at timestamptz,
  expires_at timestamptz,
  constraint approvals_decision_time check (
    (decision = 'pending' and decided_at is null)
    or (decision <> 'pending' and decided_at is not null)
  )
);

create table execution.events (
  id bigint generated always as identity primary key,
  run_id uuid not null references execution.runs(id) on delete cascade,
  sequence_no integer not null check (sequence_no >= 0),
  stage text not null check (stage in ('observe', 'diagnose', 'patch', 'verify', 'commit')),
  event_kind text not null check (char_length(event_kind) between 1 and 96),
  status text not null check (status in ('pending', 'running', 'passed', 'failed', 'canceled')),
  payload jsonb not null default '{}'::jsonb check (jsonb_typeof(payload) = 'object'),
  occurred_at timestamptz not null default now(),
  unique (run_id, sequence_no)
);

create table execution.connector_invocations (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references execution.runs(id) on delete cascade,
  approval_id uuid references execution.approvals(id) on delete set null,
  connector_key text not null check (char_length(connector_key) between 1 and 160),
  operation text not null check (char_length(operation) between 1 and 160),
  status text not null default 'queued'
    check (status in ('queued', 'running', 'passed', 'failed', 'canceled')),
  request_digest text check (request_digest is null or request_digest ~ '^[0-9a-f]{64}$'),
  response_digest text check (response_digest is null or response_digest ~ '^[0-9a-f]{64}$'),
  started_at timestamptz,
  completed_at timestamptz,
  error_code text check (error_code is null or char_length(error_code) <= 160),
  metadata jsonb not null default '{}'::jsonb check (jsonb_typeof(metadata) = 'object'),
  constraint connector_invocations_time_order check (
    completed_at is null or (started_at is not null and completed_at >= started_at)
  )
);

create table execution.artifacts (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references execution.runs(id) on delete cascade,
  artifact_type text not null check (artifact_type in ('build_log', 'runtime_log', 'diff', 'report', 'screenshot', 'other')),
  uri text not null check (char_length(uri) between 1 and 2048),
  sha256 text not null check (sha256 ~ '^[0-9a-f]{64}$'),
  size_bytes bigint check (size_bytes is null or size_bytes >= 0),
  metadata jsonb not null default '{}'::jsonb check (jsonb_typeof(metadata) = 'object'),
  created_at timestamptz not null default now(),
  unique (run_id, sha256)
);

create table execution.checkpoints (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references execution.runs(id) on delete cascade,
  commit_sha text not null check (commit_sha ~ '^[0-9a-f]{7,64}$'),
  rollback_ref text check (rollback_ref is null or char_length(rollback_ref) <= 320),
  artifact_id uuid references execution.artifacts(id) on delete set null,
  created_at timestamptz not null default now(),
  unique (run_id, commit_sha)
);

create index sessions_workspace_created_idx
  on execution.sessions (workspace_id, created_at desc);
create index runs_session_started_idx
  on execution.runs (session_id, started_at desc);
create index runs_status_started_idx
  on execution.runs (status, started_at desc);
create index events_run_occurred_idx
  on execution.events (run_id, occurred_at, id);
create index connector_invocations_run_started_idx
  on execution.connector_invocations (run_id, started_at desc);
create index connector_invocations_connector_status_idx
  on execution.connector_invocations (connector_key, status, started_at desc);
create index approvals_run_decision_idx
  on execution.approvals (run_id, decision, requested_at desc);
create index artifacts_run_type_idx
  on execution.artifacts (run_id, artifact_type, created_at desc);

create or replace function execution.reject_event_mutation()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  raise exception 'execution.events is append-only';
end;
$$;

revoke all on function execution.reject_event_mutation() from public, anon, authenticated;
grant execute on function execution.reject_event_mutation() to service_role;

create trigger events_append_only
before update or delete on execution.events
for each row execute function execution.reject_event_mutation();

alter table execution.workspaces enable row level security;
alter table execution.workspace_members enable row level security;
alter table execution.sessions enable row level security;
alter table execution.runs enable row level security;
alter table execution.approvals enable row level security;
alter table execution.events enable row level security;
alter table execution.connector_invocations enable row level security;
alter table execution.artifacts enable row level security;
alter table execution.checkpoints enable row level security;

revoke all on all tables in schema execution from public, anon, authenticated;
revoke all on all sequences in schema execution from public, anon, authenticated;
grant select, insert, update, delete on all tables in schema execution to service_role;
grant usage, select on all sequences in schema execution to service_role;

alter default privileges in schema execution
  revoke all on tables from public, anon, authenticated;
alter default privileges in schema execution
  revoke all on sequences from public, anon, authenticated;
alter default privileges in schema execution
  revoke execute on functions from public, anon, authenticated;
