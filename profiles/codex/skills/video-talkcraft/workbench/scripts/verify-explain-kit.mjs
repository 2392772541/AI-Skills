import { bundle } from '@remotion/bundler';
import { getCompositions, openBrowser, renderStill } from '@remotion/renderer';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = process.cwd();
const out = path.join(root, 'exports', 'explain-kit-qa');
mkdirSync(out, { recursive: true });
const publicDir = path.join(out, 'empty-public');
mkdirSync(publicDir, { recursive: true });
const serveUrl = await bundle({
  entryPoint: path.join(root, 'src/remotion/index.ts'), publicDir,
  outDir: path.join(out, 'bundle'),
  webpackOverride: (c) => ({ ...c, resolve: { ...c.resolve, symlinks: false, alias: {
    ...c.resolve?.alias,
    '@kbsrc': path.join(root, existsSync(path.join(root, 'kbsrc')) ? 'kbsrc' : 'kbsrc-stub'),
    '@tpl': path.join(root, 'tplcards'),
  } } }),
});
const browser = await openBrowser('chrome');
const failures = [];
const checks = [];
try {
  const compositions = (await getCompositions(serveUrl, { puppeteerInstance: browser })).filter((c) => c.id.startsWith('kit-'));
  assert.equal(compositions.length, 20, 'All twenty cards must be registered');
  const overrides = {
    'kit-waterfall': { start: 0, a: -60, b: 20, c: -10 },
    'kit-flow-split': { value0: 0, value1: 0, value2: 100 },
    'kit-slope': { from0: 50, from1: 50, from2: 50, to0: 50, to1: 50, to2: 50 },
    'kit-quadrant': { x0: 0, y0: 0, x1: 100, y1: 100 },
    'kit-object-continuity': { regroup: false, label0: '含中文和English的较长部件名称', detail0: '较长说明用于确认多行文字不会覆盖其他部件的说明和底部备注' },
    'kit-funnel': { value0: 0, value1: 0, value2: 0, value3: 0 },
    'kit-donut': { value0: 0, value1: 0, value2: 0, value3: 0 },
    'kit-pareto': { value0: 0, value1: 0, value2: 0, value3: 0 },
    'kit-histogram': { value0: 0, value1: 0, value2: 0, value3: 0 },
    'kit-rank': { value0: 50, value1: 50, value2: 50, value3: 50, to0: 50, to1: 50, to2: 50, to3: 50 },
    'kit-gantt': { days: 1, start0: 1, end0: 0 },
    'kit-interval': { low0: 80, point0: 20, high0: 10 },
    'kit-bullet': { value0: 0, target0: 100, value1: 100, target1: 0 },
    'kit-heatmap': { cell0: 0, cell1: 100, cell2: 0 },
    'kit-decision': { choice: 'right' },
    'kit-layers': { focus: 4 },
  };
  for (const c of compositions) {
    const logs = [];
    const base = c.defaultProps ?? c.props;
    assert.ok(base && Object.keys(base).length, `${c.id} has editable defaults`);
    for (const [suffix, frame, inputProps] of [
      ['early', 12, base], ['settled', 150, base],
      ['edge', 220, { ...base, ...overrides[c.id], accent: '#984C70', pace: 0.7, transparent: true }],
    ]) {
      await renderStill({ serveUrl, composition: { ...c, props: inputProps }, puppeteerInstance: browser, frame,
        inputProps, output: path.join(out, `${c.id}-${suffix}.png`), imageFormat: 'png',
        onBrowserLog: (log) => { if (log.type === 'error') logs.push(log.text); },
      });
    }
    const hash = (suffix) => createHash('sha256').update(readFileSync(path.join(out, `${c.id}-${suffix}.png`))).digest('hex');
    assert.notEqual(hash('early'), hash('settled'), `${c.id} must change across frames`);
    if (logs.length) failures.push({ id: c.id, logs });
    checks.push({ id: c.id, frames: [12, 150, 220], changedAcrossFrames: true, edgeOverrides: overrides[c.id] ?? {} });
    console.log(`Verified ${checks.length}/20: ${c.id}`);
  }
  assert.equal(failures.length, 0, JSON.stringify(failures));
  const project = { name: '讲解增强-20卡展示', width: 960, height: 540, fps: 30, tracks: [{ id: 'explain-kit', name: '讲解增强', clips: compositions.map((c, i) => ({ id: `kit-${i}`, cardId: c.id, start: i * 180, duration: 180, inOffset: 0, speed: 1, opacity: 1, scale: 1, x: 0, y: 0, props: { pace: 1.5 } })) }] };
  mkdirSync(path.join(root, 'examples'), { recursive: true });
  writeFileSync(path.join(root, 'examples/explain-kit-20.json'), JSON.stringify(project, null, 2));
  writeFileSync(path.join(out, 'verification.json'), JSON.stringify({ checkedAt: new Date().toISOString(), checks, failures }, null, 2));
  console.log('PASS: 60 PNG renders, 20 motion checks, 20 edge renders; showcase JSON written');
} finally {
  await browser.close({ silent: true });
}
