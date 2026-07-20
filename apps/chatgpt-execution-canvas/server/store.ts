import { createClient, type SupabaseClient } from '@supabase/supabase-js';

export type Stage = 'observe' | 'diagnose' | 'patch' | 'verify' | 'commit';
export type RunStatus = 'queued' | 'running' | 'passed' | 'failed' | 'canceled';

export interface RunSnapshot {
  id: string;
  session_id: string;
  current_stage: Stage;
  status: RunStatus;
  target_node: string | null;
  repository: string | null;
  git_ref: string | null;
  commit_sha: string | null;
  started_at: string;
  completed_at: string | null;
}

export interface ApprovalSnapshot {
  id: string;
  run_id: string;
  decision: 'pending' | 'approved' | 'rejected' | 'expired' | 'canceled';
  scope: Record<string, unknown>;
  requested_at: string;
  decided_at: string | null;
}

export class ExecutionStore {
  private readonly client: SupabaseClient;

  constructor() {
    const url = process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (!url || !key) {
      throw new Error('SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required');
    }
    this.client = createClient(url, key, {
      auth: { persistSession: false, autoRefreshToken: false },
      db: { schema: 'execution' },
    });
  }

  async getRun(runId: string): Promise<RunSnapshot> {
    const { data, error } = await this.client.from('runs').select('*').eq('id', runId).single();
    if (error) throw new Error(`getRun failed: ${error.message}`);
    return data as RunSnapshot;
  }

  async listEvents(runId: string, limit = 100) {
    const { data, error } = await this.client
      .from('events')
      .select('id,run_id,sequence_no,stage,event_kind,status,payload,occurred_at')
      .eq('run_id', runId)
      .order('sequence_no', { ascending: true })
      .limit(limit);
    if (error) throw new Error(`listEvents failed: ${error.message}`);
    return data ?? [];
  }

  async requestApproval(runId: string, scope: Record<string, unknown>): Promise<ApprovalSnapshot> {
    const { data, error } = await this.client
      .from('approvals')
      .insert({ run_id: runId, scope, decision: 'pending' })
      .select('*')
      .single();
    if (error) throw new Error(`requestApproval failed: ${error.message}`);
    return data as ApprovalSnapshot;
  }

  async decideApproval(approvalId: string, decision: 'approved' | 'rejected'): Promise<ApprovalSnapshot> {
    const { data: current, error: readError } = await this.client
      .from('approvals')
      .select('*')
      .eq('id', approvalId)
      .single();
    if (readError) throw new Error(`approval lookup failed: ${readError.message}`);
    if (current.decision !== 'pending') return current as ApprovalSnapshot;

    const { data, error } = await this.client
      .from('approvals')
      .update({ decision, decided_at: new Date().toISOString() })
      .eq('id', approvalId)
      .eq('decision', 'pending')
      .select('*')
      .single();
    if (error) throw new Error(`decideApproval failed: ${error.message}`);
    return data as ApprovalSnapshot;
  }

  async assertApproved(runId: string, approvalId: string): Promise<void> {
    const { data, error } = await this.client
      .from('approvals')
      .select('id,run_id,decision,expires_at')
      .eq('id', approvalId)
      .eq('run_id', runId)
      .single();
    if (error) throw new Error(`approval verification failed: ${error.message}`);
    if (data.decision !== 'approved') throw new Error('APPROVAL_REQUIRED');
    if (data.expires_at && Date.parse(data.expires_at) <= Date.now()) throw new Error('APPROVAL_EXPIRED');
  }

  async advanceRun(input: {
    runId: string;
    approvalId: string;
    stage: Stage;
    status: RunStatus;
    eventKind: string;
    payload?: Record<string, string | number | boolean | null>;
  }): Promise<RunSnapshot> {
    await this.assertApproved(input.runId, input.approvalId);
    const existingEvents = await this.listEvents(input.runId, 1000);
    const sequenceNo = existingEvents.length === 0
      ? 0
      : Math.max(...existingEvents.map((event: any) => Number(event.sequence_no))) + 1;

    const { error: eventError } = await this.client.from('events').insert({
      run_id: input.runId,
      sequence_no: sequenceNo,
      stage: input.stage,
      event_kind: input.eventKind,
      status: input.status === 'passed' ? 'passed' : input.status === 'failed' ? 'failed' : input.status === 'canceled' ? 'canceled' : 'running',
      payload: input.payload ?? {},
    });
    if (eventError) throw new Error(`event append failed: ${eventError.message}`);

    const { data, error } = await this.client
      .from('runs')
      .update({
        current_stage: input.stage,
        status: input.status,
        completed_at: ['passed', 'failed', 'canceled'].includes(input.status) ? new Date().toISOString() : null,
      })
      .eq('id', input.runId)
      .select('*')
      .single();
    if (error) throw new Error(`advanceRun failed: ${error.message}`);
    return data as RunSnapshot;
  }
}
