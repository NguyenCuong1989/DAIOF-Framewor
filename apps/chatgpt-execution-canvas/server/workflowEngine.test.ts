import { describe, expect, it } from 'vitest';
import { capabilityHealth, capabilitiesForMission } from './capabilityRegistry.js';
import { buildWorkflow } from './workflowEngine.js';

describe('capability-aware workflow', () => {
  it('knows its usable capability surface', () => {
    const health = capabilityHealth();
    expect(health.total).toBeGreaterThan(10);
    expect(health.usable).toBe(health.total);
    expect(capabilitiesForMission('deploy').map(item => item.id)).toContain('vercel');
  });

  it('turns a plain chat request into a complete agent workflow', () => {
    const workflow = buildWorkflow('Fix the build failure, test it end to end, then deploy to Vercel');
    expect(workflow.mission).toBe('deploy');
    expect(workflow.stages).toEqual(['understand','discover','plan','execute','verify','recover','finalize']);
    expect(workflow.steps.some(step => step.capability === 'find-skills')).toBe(true);
    expect(workflow.steps.some(step => step.capability === 'webapp-testing')).toBe(true);
    expect(workflow.steps.some(step => step.capability === 'vercel')).toBe(true);
    expect(workflow.approval).toBe('external-effect');
  });

  it('keeps normal chat simple and ungated', () => {
    const workflow = buildWorkflow('Explain the current state');
    expect(workflow.mission).toBe('chat');
    expect(workflow.approval).toBe('none');
  });
});
