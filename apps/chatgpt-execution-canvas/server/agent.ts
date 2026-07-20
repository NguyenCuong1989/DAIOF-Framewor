import { approvalBoundary, routeSkillChain, type Mission } from './skillRouter.js';

export interface AgentMissionPlan {
  mission: Mission;
  summary: string;
  skillChain: string[];
  approval: 'none' | 'write' | 'external-effect';
  steps: Array<{ id: string; title: string; mode: 'automatic' | 'approval' }>;
}

const patterns: Array<[Mission, RegExp]> = [
  ['deploy', /\b(deploy\w*|publish\w*|release\w*|production|vercel)\b/i],
  ['test', /\b(test\w*|verify\w*|qa|e2e|playwright|inspector)\b/i],
  ['debug', /\b(debug\w*|fix\w*|error\w*|failed|failure|log\w*|diagnos\w*)\b/i],
  ['code', /\b(code|implement\w*|build\w*|refactor\w*|patch\w*|feature\w*|api|mcp|server|repository)\b/i],
  ['design', /\b(design\w*|ui|ux|layout\w*|brand\w*|canvas|visual\w*)\b/i],
  ['research', /\b(research\w*|search\w*|docs|documentation|lookup\w*|crawl\w*)\b/i],
  ['observe', /\b(observe\w*|monitor\w*|metrics|telemetry|sentry|health)\b/i],
  ['document', /\b(document\w*|readme|spec\w*|proposal\w*|architecture)\b/i],
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
