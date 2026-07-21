import { randomUUID } from 'node:crypto';
import { capabilitiesForMission } from './capabilityRegistry.js';
import { planAgentMission } from './agent.js';

export type WorkflowStage = 'understand' | 'discover' | 'plan' | 'execute' | 'verify' | 'recover' | 'finalize';

export interface WorkflowStep {
  id: string;
  stage: WorkflowStage;
  capability: string;
  mode: 'automatic' | 'approval';
  state: 'queued' | 'blocked';
  expectedEvidence: string;
}

export interface WorkflowPlan {
  id: string;
  request: string;
  mission: ReturnType<typeof planAgentMission>['mission'];
  approval: ReturnType<typeof planAgentMission>['approval'];
  stages: WorkflowStage[];
  steps: WorkflowStep[];
  invariants: string[];
}

const stageOrder: WorkflowStage[] = ['understand', 'discover', 'plan', 'execute', 'verify', 'recover', 'finalize'];

function stageForCapability(id: string): WorkflowStage {
  if (id === 'conversation') return 'understand';
  if (id === 'find-skills' || id === 'files-library') return 'discover';
  if (id === 'workflow-engine' || id === 'skill-creator') return 'plan';
  if (/test|validate|inspector|session-logs|sentry|audit/.test(id)) return 'verify';
  if (/deploy|vercel|github/.test(id)) return 'execute';
  return 'execute';
}

export function buildWorkflow(request: string): WorkflowPlan {
  const missionPlan = planAgentMission(request);
  const capabilities = capabilitiesForMission(missionPlan.mission);
  const seen = new Set<string>();
  const ordered = capabilities.filter(capability => {
    if (seen.has(capability.id)) return false;
    seen.add(capability.id);
    return true;
  });

  const steps = ordered.map((capability, index): WorkflowStep => {
    const gated = capability.approval !== 'never';
    return {
      id: `${index + 1}:${capability.id}`,
      stage: stageForCapability(capability.id),
      capability: capability.id,
      mode: gated ? 'approval' : 'automatic',
      state: gated ? 'blocked' : 'queued',
      expectedEvidence: capability.evidence,
    };
  });

  return {
    id: randomUUID(),
    request: request.trim(),
    mission: missionPlan.mission,
    approval: missionPlan.approval,
    stages: stageOrder,
    steps,
    invariants: [
      'read before write',
      'discover capabilities before execution',
      'verify every mutation',
      'recover from evidence, never from guesses',
      'finalize only with observable evidence',
    ],
  };
}
