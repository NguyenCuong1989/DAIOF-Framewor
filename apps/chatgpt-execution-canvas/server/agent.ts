import { approvalBoundary, routeSkillChain, type Mission } from './skillRouter.js';

export interface AgentMissionPlan {
  mission: Mission;
  summary: string;
  skillChain: string[];
  approval: 'none' | 'write' | 'external-effect';
  steps: Array<{ id: string; title: string; mode: 'automatic' | 'approval' }>;
}

const patterns: Array<[Mission, RegExp]> = [
  ['deploy', /\b(deploy|publish|release|production|vercel)\b/i],
  ['test', /\b(test|verify|qa|e2e|playwright|inspector)\b/i],
  ['debug', /\b(debug|fix|error|failed|failure|log|diagnos)\w*\b/i],
  ['code', /\b(code|implement|build|refactor|patch|feature|api|mcp|server|repository)\b/i],
  ['design', /\b(design|ui|ux|layout|brand|canvas|visual)\b/i],
  ['research', /\b(research|search|docs|documentation|lookup|crawl)\b/i],
  ['observe', /\b(observe|monitor|metrics|telemetry|sentry|health)\b/i],
  ['document', /\b(document|readme|spec|proposal|architecture)\b/i],
];

export function inferMission(message: string): Mission {
  for (const [mission, pattern] of patterns) {
    if (pattern.test(message)) return mission;
  }
  return 'chat';
}

export function planAgentMission(message: string): AgentMissionPlan {
  const normalized = message.trim();
  if (!normalized) throw new Error('EMPTY_MISSION');

  const mission = inferMission(normalized);
  const chain = routeSkillChain(mission);
  const boundary = approvalBoundary(chain);
  const steps = chain.map((skill, index) => ({
    id: `${index + 1}:${skill.id}`,
    title: skill.id,
    mode: skill.approval === 'never' ? 'automatic' as const : 'approval' as const,
  }));

  return {
    mission,
    summary: normalized,
    skillChain: chain.map(skill => skill.id),
    approval: boundary,
    steps,
  };
}
