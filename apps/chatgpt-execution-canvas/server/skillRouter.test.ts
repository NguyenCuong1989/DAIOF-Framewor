import { describe, expect, it } from 'vitest';
import { approvalBoundary, routeSkillChain } from './skillRouter.js';

describe('production skill router', () => {
  it('routes build through discovery before MCP construction', () => {
    const chain = routeSkillChain('build');
    expect(chain.map(skill => skill.id)).toEqual(['find-skills', 'mcp-builder']);
    expect(approvalBoundary(chain)).toBe('write');
  });

  it('routes deployment through build and observability before external effect', () => {
    const chain = routeSkillChain('deploy');
    expect(chain.map(skill => skill.id)).toEqual([
      'find-skills',
      'mcp-builder',
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
});
