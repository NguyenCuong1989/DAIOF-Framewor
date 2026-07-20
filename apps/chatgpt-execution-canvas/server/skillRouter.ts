import { z } from 'zod';

export const missionSchema = z.enum([
  'design',
  'build',
  'verify',
  'deploy',
  'observe',
  'document',
]);

export type Mission = z.infer<typeof missionSchema>;

export interface SkillDescriptor {
  readonly id: string;
  readonly missions: readonly Mission[];
  readonly mutating: boolean;
  readonly approval: 'never' | 'before-write' | 'before-external-effect';
  readonly requires?: readonly string[];
}

const catalog = [
  { id: 'find-skills', missions: ['design', 'build', 'verify', 'deploy', 'observe', 'document'], mutating: false, approval: 'never' },
  { id: 'mcp-builder', missions: ['build', 'verify'], mutating: true, approval: 'before-write', requires: ['find-skills'] },
  { id: 'canvas-design', missions: ['design'], mutating: true, approval: 'before-write', requires: ['find-skills'] },
  { id: 'brand-guidelines', missions: ['design'], mutating: true, approval: 'before-write', requires: ['canvas-design'] },
  { id: 'mermaid-diagrams', missions: ['design', 'document'], mutating: true, approval: 'before-write', requires: ['find-skills'] },
  { id: 'session-logs', missions: ['verify', 'observe'], mutating: false, approval: 'never', requires: ['find-skills'] },
  { id: 'sentry-cli', missions: ['verify', 'observe'], mutating: false, approval: 'never', requires: ['session-logs'] },
  { id: 'deploy-to-vercel', missions: ['deploy'], mutating: true, approval: 'before-external-effect', requires: ['mcp-builder', 'session-logs'] },
  { id: 'doc-coauthoring', missions: ['document'], mutating: true, approval: 'before-write', requires: ['find-skills'] },
] as const satisfies readonly SkillDescriptor[];

const byId = new Map(catalog.map(skill => [skill.id, skill]));

function addWithDependencies(id: string, output: SkillDescriptor[], seen: Set<string>): void {
  if (seen.has(id)) return;
  const skill = byId.get(id);
  if (!skill) throw new Error(`SKILL_NOT_REGISTERED:${id}`);
  for (const dependency of skill.requires ?? []) addWithDependencies(dependency, output, seen);
  seen.add(id);
  output.push(skill);
}

export function routeSkillChain(mission: Mission): SkillDescriptor[] {
  const selected = catalog.filter(skill => skill.missions.includes(mission));
  const output: SkillDescriptor[] = [];
  const seen = new Set<string>();
  for (const skill of selected) addWithDependencies(skill.id, output, seen);
  return output;
}

export function approvalBoundary(chain: readonly SkillDescriptor[]): 'none' | 'write' | 'external-effect' {
  if (chain.some(skill => skill.approval === 'before-external-effect')) return 'external-effect';
  if (chain.some(skill => skill.approval === 'before-write')) return 'write';
  return 'none';
}

export const skillCatalog = catalog;
