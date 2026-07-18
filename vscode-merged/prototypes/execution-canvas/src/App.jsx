import { useMemo, useState } from 'react';

const files = [
  ['.github', 'folder'], ['.vscode', 'folder'], ['apps', 'folder'], ['api', 'folder', 2],
  ['web', 'folder', 2], ['packages', 'folder'], ['core', 'folder', 2], ['src', 'folder', 3],
  ['index.ts', 'file-code', 4], ['validator.ts', 'file-code', 4, true], ['types.ts', 'file-code', 4],
  ['tests', 'folder', 3], ['package.json', 'json'], ['tsconfig.json', 'json'], ['utils', 'folder'],
  ['.gitignore', 'git-commit'], ['pnpm-lock.yaml', 'file'], ['pnpm-workspace.yaml', 'file'], ['README.md', 'info']
];

const stages = [
  ['Observe', 'completed'], ['Diagnose', 'completed'], ['Patch', 'active'], ['Verify', 'pending'], ['Commit', 'pending']
];

function Icon({ name, className = '' }) {
  return <span aria-hidden="true" className={`codicon codicon-${name} ${className}`} />;
}

function ActivityBar() {
  return <aside className="activity-bar" aria-label="Workbench activity">
    <div className="brand"><Icon name="azure" /></div>
    {['files','search','source-control','debug-alt','extensions','comment-discussion','account','remote-explorer'].map((name, index) =>
      <button key={name} className={`activity-button ${index === 0 ? 'selected' : ''}`} aria-label={name}><Icon name={name}/>{index === 2 && <b>2</b>}</button>
    )}
    <div className="activity-spacer" />
    <button className="activity-button" aria-label="Accounts"><Icon name="account"/></button>
    <button className="activity-button" aria-label="Settings"><Icon name="settings-gear"/></button>
  </aside>;
}

function Explorer() {
  return <aside className="explorer">
    <header><span>EXPLORER</span><Icon name="ellipsis"/></header>
    <div className="workspace-title"><Icon name="chevron-down"/> ACME-SERVICE (WORKSPACE)</div>
    <div className="tree" role="tree">
      <div className="tree-row root"><Icon name="chevron-down"/><span>acme-service</span></div>
      {files.map(([name, icon, depth = 1, active]) =>
        <button key={name} className={`tree-row ${active ? 'active' : ''}`} style={{'--depth': depth}}>
          <Icon name={icon}/><span>{name}</span>{active && <em>M</em>}
        </button>)}
    </div>
    <div className="explorer-bottom">
      <div><Icon name="chevron-right"/> OUTLINE</div><div><Icon name="chevron-right"/> TIMELINE</div>
      <div><Icon name="chevron-down"/> EXECUTION HISTORY</div>
      <p>Today</p><button><Icon name="check"/> Fix validation bug <i>✓</i></button>
      <button><Icon name="circle-outline"/> Refactor rate limiter</button>
      <p>Yesterday</p>
    </div>
  </aside>;
}

function TopBar() {
  return <><div className="menu-bar"><Icon name="azure"/><span>File</span><span>Edit</span><span>Selection</span><span>View</span><span>Go</span><span>Run</span><span>Terminal</span><span>Help</span></div>
    <div className="command-center"><Icon name="arrow-left"/><Icon name="arrow-right"/><button><Icon name="search"/> acme-service (Workspace)</button></div>
    <div className="window-controls"><Icon name="layout-sidebar-left"/><Icon name="layout-panel"/><Icon name="layout-sidebar-right"/><Icon name="layout"/><span>—</span><span>□</span><span>×</span></div></>;
}

function Stepper({ phase }) {
  return <div className="stepper">
    {stages.map(([label, base], index) => {
      const state = phase === 'committed' ? 'completed' : phase === 'verified' && index <= 3 ? 'completed' : base;
      return <div className={`stage ${state}`} key={label}>
        <span>{state === 'completed' ? <Icon name="check"/> : index + 1}</span>
        <strong>{label}</strong><small>{state === 'completed' ? 'Completed' : state === 'active' ? 'In Progress' : 'Pending'}</small>
      </div>;
    })}
  </div>;
}

function ExecutionCanvas() {
  const [phase, setPhase] = useState('dry');
  const [tests, setTests] = useState('not-run');
  const [diffOpen, setDiffOpen] = useState(true);
  const [message, setMessage] = useState('');
  const phaseLabel = useMemo(() => phase === 'committed' ? 'Committed · checkpoint 9b8e4f1' : phase === 'verified' ? 'Verified · tests passed' : 'DRY RUN — No changes will be made', [phase]);

  const runTests = () => {
    setTests('running');
    window.setTimeout(() => { setTests('passed'); setPhase('verified'); }, 700);
  };
  const apply = () => {
    if (tests !== 'passed') { runTests(); return; }
    setPhase('committed');
  };

  return <main className="chat-workspace">
    <div className="editor-tab"><Icon name="sparkle"/> GPT: Execution Canvas <Icon name="close"/></div>
    <section className="conversation">
      <div className="message-head"><span className="gpt-mark"><Icon name="sparkle"/></span><b>GPT</b><span>Today at 10:42 AM</span></div>
      <p className="intro">Here&apos;s the execution plan for your request. All actions are simulated in dry-run mode.</p>
      <article className="canvas">
        <header className="canvas-head"><div><h1>Execution Canvas {phase === 'dry' && '(Dry Run)'}</h1><p><span><Icon name="device-desktop"/> Local Workspace</span><span><Icon name="device-desktop"/> Target: Titan GT77</span></p></div><div><small>Generated Jul 18, 2026, 10:42 AM</small><button><Icon name="copy"/> Copy plan</button><button><Icon name="ellipsis"/></button></div></header>
        <Stepper phase={phase}/>
        <section className="patch-panel">
          <div className="patch-title"><b>3</b><h2>Patch</h2><span>Propose and validate changes</span><em className={phase === 'dry' ? '' : 'good'}>{phaseLabel} <Icon name="info"/></em></div>
          <dl><dt>Target</dt><dd>Local workspace → Titan GT77</dd><dt>Repository</dt><dd>~/work/acme-service (main)</dd><dt>Files</dt><dd>packages/core/src/validator.ts</dd></dl>
          <button className="disclosure" onClick={() => setDiffOpen(!diffOpen)}><Icon name={diffOpen ? 'chevron-down' : 'chevron-right'}/> Proposed change</button>
          {diffOpen && <div className="change-row"><span>1 file changed</span><b>+12</b><em>−3</em><code>packages/core/src/validator.ts</code><b>+12</b><em>−3</em></div>}
          <div className="summary-row"><span><Icon name="chevron-down"/> Diff summary</span><ul><li>Add stricter email validation (RFC 5322 subset)</li><li>Trim input before validation</li><li>Return detailed error codes</li></ul></div>
          <div className="gate-row"><span><Icon name="beaker"/> Test gate</span><div><b>Unit tests (vitest)</b><code>pnpm -w test --filter @acme/core</code></div><em className={tests === 'passed' ? 'good' : ''}><Icon name={tests === 'running' ? 'loading' : tests === 'passed' ? 'pass-filled' : 'circle-outline'} className={tests === 'running' ? 'spin' : ''}/> {tests === 'running' ? 'Running' : tests === 'passed' ? 'Passed' : 'Not run'}</em></div>
          <div className="rollback-row"><span><Icon name="shield"/> Rollback checkpoint</span><div><b>git stash (tracked)</b><code>stash@{'{0}'} (simulated)</code></div><em><Icon name="pass-filled"/> Ready</em></div>
        </section>
        <footer className="actions">
          <button className="primary" onClick={apply}><Icon name={phase === 'committed' ? 'check' : 'play'}/> {phase === 'committed' ? 'Patch committed' : tests === 'passed' ? 'Apply verified patch' : 'Verify & apply patch'}</button>
          <button onClick={() => setDiffOpen(true)}><Icon name="diff"/> Open diff</button><button onClick={runTests}><Icon name="run-tests"/> Run tests</button><button><Icon name="ellipsis"/></button>
        </footer>
      </article>
      <section className="composer"><textarea value={message} onChange={e => setMessage(e.target.value)} placeholder="Ask GPT or type @ to attach context"/><div><span><button><Icon name="attach"/> Add context</button><button><Icon name="list-tree"/> Plan <Icon name="chevron-down"/></button><button><Icon name="search"/> Search</button><button><Icon name="server"/> MCP</button><button><Icon name="organization"/> Sub-agents</button></span><span><button>GPT-4.1 <Icon name="chevron-down"/></button><button className="send" disabled={!message}><Icon name="send"/></button></span></div></section>
      <small className="disclaimer">GPT can make mistakes. Review all changes carefully.</small>
    </section>
  </main>;
}

function StateDelta() {
  return <aside className="state-delta"><header>STATE DELTA <span><Icon name="refresh"/><Icon name="menu"/><Icon name="close"/></span></header>
    <div className="delta-meta"><span>Workspace</span><b>Local (dry run)</b><span>Branch</span><b>main</b></div>
    <h3><Icon name="chevron-down"/> 1 file changed</h3>
    <h4><Icon name="file-code"/> packages/core/src/validator.ts</h4>
    <div className="code-label">Before <span>(main)</span></div><pre className="before"><code>42  export function isValidEmail(
43    input: string
44  ): boolean {'{'}
45    const emailRegex = /^[^\s@]+@...
46    return emailRegex.test(input);
47  {'}'}</code></pre>
    <div className="code-label">After <span>(Proposed)</span></div><pre className="after"><code>42  export function isValidEmail(
43    input: string
44  ): boolean {'{'}
45    const normalized = input.trim();
46    const emailRegex = /^[^\s@]+@...
47    const ok = emailRegex.test(
48      normalized
49    );
50    return ok;
51  {'}'}</code></pre>
    <div className="delta-summary"><span>Change summary</span><b>+12</b><em>−3</em><span>Status</span><strong>Dry run <Icon name="info"/></strong></div>
  </aside>;
}

function StatusBar() { return <footer className="status-bar"><span><Icon name="remote"/></span><span><Icon name="source-control"/> main*</span><span><Icon name="sync"/> 0</span><span><Icon name="error"/> 0</span><span><Icon name="warning"/> 0</span><i/><span><Icon name="device-desktop"/> Titan GT77 (local)</span><span>UTF-8</span><span>LF</span><span><Icon name="symbol-property"/> TypeScript</span><span><Icon name="check-all"/> Prettier</span><span><Icon name="bell"/></span></footer>; }

export function App() {
  return <div className="app-shell"><TopBar/><ActivityBar/><Explorer/><ExecutionCanvas/><StateDelta/><StatusBar/></div>;
}
