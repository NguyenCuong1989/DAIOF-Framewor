import { describe, expect, it } from 'vitest';
import { planAgentMission } from './agent.js';
import { approvalBoundary, routeSkillChain } from './skillRouter.js';

describe('conversational IDE skill router', () => {
  it('routes coding through discovery before MCP construction', () => {
    const chain = routeSkillChain('code');
    expect(chain.map(skill => skill.id)).toEqual(['find-skills', 'mcp-builder']);
    expect(approvalBoundary(chain)).toBe('write');
  });

  it('routes deployment through testing and observability before external effect', () => {
    const chain = routeSkillChain('deploy');
    expect(chain.map(skill => skill.id)).toEqual([
      'find-skills',
      'mcp-builder',
      'mcp-cli',
      'webapp-testing',
      'session-logs',
      'deploy-to-vercel',
    ]);
    expect(approvalBoundary(chain)).toBe('external-effect');
  });

  it('keeps observation read-only', () => {
    const chain = routeSkillChain('observe');
    expect(chain.map(skill => skill.id)).toEqual(['find-skills', 'session-logs', 'sentry-cli']);
    expect(approvalBoundary(chain)).toBe('none');
  });

  it('turns a plain chatbot request into an IDE mission plan', () => {
    const plan = planAgentMission('Fix the MCP server error, test it, then prepare deployment');
    expect(plan.mission).toBe('deploy');
    expect(plan.approval).toBe('external-effect');
    expect(plan.skillChain.at(-1)).toBe('deploy-to-vercel');
  });
});
