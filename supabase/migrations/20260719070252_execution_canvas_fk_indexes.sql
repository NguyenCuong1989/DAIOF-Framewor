create index workspaces_owner_idx
  on execution.workspaces (owner_id);

create index workspace_members_user_idx
  on execution.workspace_members (user_id, workspace_id);

create index sessions_created_by_idx
  on execution.sessions (created_by, created_at desc);

create index approvals_requested_by_idx
  on execution.approvals (requested_by, requested_at desc)
  where requested_by is not null;

create index approvals_decided_by_idx
  on execution.approvals (decided_by, decided_at desc)
  where decided_by is not null;

create index connector_invocations_approval_run_idx
  on execution.connector_invocations (approval_id, run_id)
  where approval_id is not null;

create index checkpoints_artifact_run_idx
  on execution.checkpoints (artifact_id, run_id)
  where artifact_id is not null;
