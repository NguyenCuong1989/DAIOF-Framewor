import { routeSkillChain, skillCatalog, type Mission } from './skillRouter.js';

export type CapabilityKind = 'native' | 'skill' | 'connector' | 'runtime';
export type CapabilityState = 'ready' | 'configured' | 'degraded' | 'unavailable';

export interface CapabilityDescriptor {
  id: string;
  kind: CapabilityKind;
  missions: readonly Mission[];
  state: CapabilityState;
  mutating: boolean;
  approval: 'never' | 'before-write' | 'before-external-effect';
  evidence: string;
}

const native: CapabilityDescriptor[] = [
  { id: 'conversation', kind: 'native', missions: ['chat','research','design','code','debug','test','deploy','observe','document'], state: 'ready', mutating: false, approval: 'never', evidence: 'MCP natural-language entrypoint' },
  { id: 'workflow-engine', kind: 'native', missions: ['research','design','code','debug','test','deploy','observe','document'], state: 'ready', mutating: false, approval: 'never', evidence: 'discover-plan-execute-verify-recover-finalize' },
  { id: 'approval-gateway', kind: 'native', missions: ['design','code','debug','test','deploy','document'], state: 'ready', mutating: false, approval: 'never', evidence: 'server-enforced scoped approval' },
  { id: 'audit-ledger', kind: 'native', missions: ['debug','test','deploy','observe'], state: 'ready', mutating: false, approval: 'never', evidence: 'append-only execution events' },
];

const connectors: CapabilityDescriptor[] = [
  { id: 'github', kind: 'connector', missions: ['code','debug','test','deploy','observe','document'], state: 'configured', mutating: true, approval: 'before-write', evidence: 'repository and CI connector' },
  { id: 'vercel', kind: 'connector', missions: ['deploy','observe'], state: 'configured', mutating: true, approval: 'before-external-effect', evidence: 'deployment and runtime logs connector' },
  { id: 'files-library', kind: 'connector', missions: ['research','design','code','debug','test','document'], state: 'configured', mutating: false, approval: 'never', evidence: 'Library semantic retrieval' },
];

const skills: CapabilityDescriptor[] = skillCatalog.map(skill => ({
  id: skill.id,
  kind: 'skill',
  missions: skill.missions,
  state: 'ready',
  mutating: skill.mutating,
  approval: skill.approval,
  evidence: `skill:${skill.id}`,
}));

const skillsById = new Map(skills.map(skill => [skill.id, skill]));

export const capabilityRegistry: readonly CapabilityDescriptor[] = [...native, ...connectors, ...skills];

export function capabilitiesForMission(mission: Mission): CapabilityDescriptor[] {
  const platformCapabilities = [...native, ...connectors].filter(capability => capability.missions.includes(mission));
  const routedSkills = routeSkillChain(mission).map(skill => {
    const capability = skillsById.get(skill.id);
    if (!capability) throw new Error(`CAPABILITY_NOT_REGISTERED:${skill.id}`);
    return capability;
  });
  return [...platformCapabilities, ...routedSkills];
}

export function capabilityHealth() {
  const totals = capabilityRegistry.reduce<Record<CapabilityState, number>>((acc, item) => {
    acc[item.state] += 1;
    return acc;
  }, { ready: 0, configured: 0, degraded: 0, unavailable: 0 });
  return { total: capabilityRegistry.length, states: totals, usable: totals.ready + totals.configured };
}
