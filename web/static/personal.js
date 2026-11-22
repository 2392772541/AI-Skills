'use strict';
const app = document.querySelector('#app');
const integrated = document.body.dataset.integrated === 'true';
const sources = { unknown: '来源待确认', self: '自己创建', external: '手动安装', builtin: '内置 / 不展示' };
const kinds = { added: '新发现', modified: '已修改', removed: '已移除', restored: '已恢复' };
const guideFields = {
  summary: '它帮你干什么',
  when: '什么时候用',
  needs: '你要给它什么',
  output: '最后得到什么',
  example: '你可以这样说',
  boundary: '使用前要知道'
};

let data = { items: [], events: [], categories: {}, monitor: {} };
let filter = { q: '', source: '', category: '', sort: 'name' };
let activityFilter = { q: '', kind: '', limit: 80 };
let route = '', detailId = '', pending = false, generation = 0, token = '';

const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = (v) => v ? new Date(v).toLocaleString('zh-CN', { hour12: false }) : '尚未完成';
const active = () => data.items.filter((x) => x.status === 'active' && x.source !== 'builtin');
const catLabel = (k) => data.categories[k] || k;
const tag = (t, c = '') => `<span class="tag ${c}">${esc(t)}</span>`;
const guide = (x) => x.guide || { title: x.name, summary: x.description };
const categoryOrder = ['publish', 'bookmarks', 'video', 'video-planning', 'video-motion', 'video-tools', 'media', 'transcription'];
const allCategories = () => [...new Set([...categoryOrder.filter((k) => k in data.categories), ...Object.keys(data.categories), ...active().flatMap((x) => x.categories)])];

// 提取简短清晰的存储位置标签，解决多副本卡片无法分辨来源目录的问题
function formatLocationBadge(x) {
  const p = String(x.path || '');
  const lower = p.toLowerCase();
  if (lower.includes('.codex')) return '📂 .codex 技能目录';
  if (lower.includes('ai-skills')) return '📂 AI-Skills 主库';
  if (lower.includes('.claude')) return '📂 .claude 技能目录';
  if (lower.includes('antigravity')) return '📂 Antigravity 目录';
  const parts = p.split(/[\\/]/).filter(Boolean);
  return parts.length >= 2 ? `📂 ${parts.slice(-2, -1)[0]}` : '📂 本机目录';
}

const callName = (x) => `
  <div class="call-name">
    <div class="call-name-head">
      <span>技能调用标识</span>
      <button type="button" class="copy-name" data-copy="${esc(x.name)}" aria-label="复制调用标识 ${esc(x.name)}">复制标识</button>
    </div>
    <code>$${esc(x.name)}</code>
    <small class="call-hint">可直接描述任务触发，或输入 $${esc(x.name)} / /${esc(x.name)} 指定调用</small>
  </div>`;

function bindCopy() {
  document.querySelectorAll('[data-copy]').forEach((b) => {
    b.onclick = async () => {
      try {
        await navigator.clipboard.writeText('$' + b.dataset.copy);
        b.textContent = '已复制 ✓';
        notice('已复制 $' + b.dataset.copy + '，粘贴到对话中再描述你的需求即可。');
        setTimeout(() => { b.textContent = '复制标识'; }, 2000);
      } catch {
        notice('剪贴板暂不可用，请直接选中上方技能标识复制。');
      }
    };
  });
}

const categoryOptions = (s = '') => allCategories().map((k) => `<option value="${esc(k)}" ${k === s ? 'selected' : ''}>${esc(catLabel(k))}</option>`).join('');

async function api(path, payload) {
  const headers = { 'Content-Type': 'application/json' };
  if (payload && integrated) {
    if (!token) {
      const r = await fetch('/api/session');
      if (!r.ok) throw new Error('本机工作台连接异常');
      token = (await r.json()).token;
    }
    headers['X-Port-Console-Token'] = token;
  }
  const r = await fetch('/api/personal' + path, payload ? { method: 'POST', headers, body: JSON.stringify(payload) } : {});
  const d = await r.json();
  if (!r.ok) {
    if (r.status === 403) token = '';
    throw new Error(d.error || d.monitor?.error || '请求失败');
  }
  return d;
}

function notice(t) {
  const el = document.querySelector('#notice');
  if (el) el.textContent = t;
}

function head(t, s, a = '', e = '个人技能资产') {
  return `<div class="page-head"><div><div class="eyebrow">${esc(e)}</div><h1>${esc(t)}</h1><p class="sub">${esc(s)}</p></div>${a}</div>`;
}

function connection(error) {
  const el = document.querySelector('#connection');
  el.classList.toggle('error', !!error);
  el.textContent = error
    ? `● 本机服务异常 · ${error}`
    : `● 技能监控${data.monitor.running ? '运行中' : '未启动'} · ${fmt(data.monitor.scanned_at)}`;
}

async function load(renderPage = true) {
  try {
    data = await api('');
    connection(data.monitor.error);
    if (renderPage) render();
    return true;
  } catch (e) {
    connection(e.message);
    if (!data.items.length) {
      const projHref = integrated ? '/#projects' : 'http://127.0.0.1:8787/#projects';
      app.innerHTML = `<div class="empty"><p>${esc(e.message)}</p><p><a class="button primary" href="${projHref}">前往项目控制启动服务</a></p></div>`;
    }
    return false;
  }
}

function render() {
  const parts = location.hash.replace(/^#\/?/, '').split('/');
  route = parts[0] || 'skills';
  detailId = parts[1] || '';
  document.querySelectorAll('[data-nav]').forEach((a) => a.classList.toggle('active', a.dataset.nav === route));
  if (route === 'skills' && detailId) { renderDetail(); return; }
  generation++;
  if (route === 'categories') { renderCategories(); return; }
  if (route === 'activity') { renderActivity(); return; }
  if (route === 'monitor') { renderMonitor(); return; }

  const rows = active();
  const fav = route === 'favorites';
  const usedCatCount = new Set(rows.flatMap((x) => x.categories)).size;
  const totalCatCount = allCategories().length;

  app.innerHTML = head(
    fav ? '我的收藏' : '我的技能库',
    fav ? '把高频使用的技能收藏在这里，日常创作随时取用。' : '不用死记英文参数，用大白话看懂每个技能能帮你解决什么问题。',
    '<button class="button primary" id="scan" type="button">↻ 同步技能</button>',
    fav ? '常用技能收藏' : '个人技能资产'
  ) +
  `<div class="stats">${[
    ['活跃技能总数', rows.length, '已自动排除系统内置与备份目录'],
    ['已覆盖分类', usedCatCount, `共预设 ${totalCatCount} 个用途分类，支持自定义`],
    ['手动安装', rows.filter((x) => x.source === 'external').length, '来自外部仓库安装或人工确认'],
    ['自建原创', rows.filter((x) => x.source === 'self').length, '由你本人沉淀并标记的技能']
  ].map(([l, n, s]) => `<div class="stat"><span class="label">${l}</span><b>${n}</b><small>${s}</small></div>`).join('')}</div>` +
  `<div class="toolbar">
    <div class="search"><input id="search" type="search" aria-label="搜索技能" placeholder="想做什么？比如：改文章、做视频、整理笔记、发小红书…" value="${esc(filter.q)}"></div>
    <select id="source" aria-label="来源筛选"><option value="">全部来源</option>${Object.entries(sources).filter(([k]) => k !== 'builtin').map(([k, v]) => `<option value="${k}" ${filter.source === k ? 'selected' : ''}>${v}</option>`).join('')}</select>
    <select id="category" aria-label="分类筛选"><option value="">全部分类</option>${categoryOptions(filter.category)}</select>
    <select id="sort" aria-label="排序方式">
      <option value="name" ${filter.sort === 'name' ? 'selected' : ''}>按名称排序</option>
      <option value="new" ${filter.sort === 'new' ? 'selected' : ''}>最近发现</option>
      <option value="modified" ${filter.sort === 'modified' ? 'selected' : ''}>最近修改</option>
    </select>
  </div><div id="results"></div>`;

  bindScan();
  renderCards();
  document.querySelector('#search').addEventListener('input', (e) => { filter.q = e.target.value; renderCards(); });
  for (const id of ['source', 'category', 'sort']) {
    document.querySelector('#' + id).addEventListener('change', (e) => { filter[id] = e.target.value; renderCards(); });
  }
}

function renderCards() {
  const items = active();
  const counts = [
    items.length,
    new Set(items.flatMap((x) => x.categories)).size,
    items.filter((x) => x.source === 'external').length,
    items.filter((x) => x.source === 'self').length
  ];
  document.querySelectorAll('.stats b').forEach((el, i) => { el.textContent = counts[i]; });

  const hasFilter = Boolean(filter.q.trim() || filter.source || filter.category);
  const totalFavorites = items.filter((x) => x.favorite).length;

  const rows = items.filter((x) =>
    (route !== 'favorites' || x.favorite) &&
    (!filter.source || x.source === filter.source) &&
    (!filter.category || x.categories.includes(filter.category)) &&
    (!filter.q || `${x.name} ${Object.values(guide(x)).join(' ')} ${x.description} ${x.note} ${x.path}`.toLowerCase().includes(filter.q.toLowerCase()))
  );

  rows.sort((a, b) => filter.sort === 'name'
    ? a.name.localeCompare(b.name)
    : String(b[filter.sort === 'new' ? 'first_seen' : 'modified_at']).localeCompare(String(a[filter.sort === 'new' ? 'first_seen' : 'modified_at']))
  );

  let emptyHtml = '';
  if (!rows.length) {
    if (route === 'favorites' && totalFavorites === 0 && !hasFilter) {
      emptyHtml = `
        <div class="empty">
          <p>还没有收藏任何技能。在技能卡片右上角点击「☆」星标即可把常用技能收进这里。</p>
          <p><a class="button primary" href="#/skills">去浏览全部技能</a></p>
        </div>`;
    } else {
      emptyHtml = `
        <div class="empty">
          <p>${route === 'favorites' ? '当前筛选条件下没有匹配的收藏技能。' : '没有找到匹配的技能，试试换个日常说法或清空筛选条件。'}</p>
          ${hasFilter ? '<p><button class="button" id="clear-filter" type="button">清空筛选条件</button></p>' : ''}
        </div>`;
    }
  }

  document.querySelector('#results').innerHTML =
    `<div class="result-label">
      <span>共 ${rows.length} 项技能${filter.category ? ' · ' + esc(catLabel(filter.category)) : ''}${hasFilter ? '（已筛选）' : ''}</span>
      <span>每张卡片均提供大白话用途与对话示例</span>
    </div>` +
    (rows.length ? `<div class="cards">${rows.map((x) => {
      const g = guide(x);
      const locBadge = formatLocationBadge(x);
      return `
      <article class="card">
        <div class="card-top">
          <div class="skill-icon ${esc(x.categories[0])}">${esc(({ video: '▷', image: '◈', office: '✧', modeling: '◇', notes: '▤', automation: '⌘', publish: '↗' })[x.categories[0]] || '⌁')}</div>
          <div class="card-top-right">
            ${x.copies > 1 ? `<span class="tag copy-loc-tag" title="${esc(x.path)}">${esc(locBadge)}</span>` : ''}
            <button type="button" aria-label="${x.favorite ? '取消收藏' : '收藏'} ${esc(x.name)}" class="favorite ${x.favorite ? 'on' : ''}" data-fav="${x.id}">${x.favorite ? '★' : '☆'}</button>
          </div>
        </div>
        <h3 class="card-title"><a href="#/skills/${x.id}">${esc(g.title)}</a></h3>
        ${callName(x)}
        <p class="description">${esc(g.summary)}</p>
        <div class="try-line"><strong>开口示例：</strong>${esc(g.example || '先帮我介绍这个技能的用法。')}</div>
        <div class="tags">
          ${x.categories.map((c) => tag(catLabel(c))).join('')}
          ${tag(sources[x.source], x.source)}
          ${x.copies > 1 ? tag(`${x.copies} 个独立副本`, 'dup') : ''}
          ${x.guide_status === 'pending' ? tag('说明待整理') : ''}
          ${x.guide_status === 'stale' ? tag('说明待复核') : ''}
        </div>
        <div class="card-foot">
          <span title="${esc(x.path)}">${esc(locBadge)} · ${x.file_count} 个文件</span>
          <a href="#/skills/${x.id}">看怎么用 →</a>
        </div>
      </article>`;
    }).join('')}</div>` : emptyHtml);

  bindCopy();
  const clear = document.querySelector('#clear-filter');
  if (clear) clear.onclick = () => { filter = { q: '', source: '', category: '', sort: 'name' }; render(); };

  document.querySelectorAll('[data-fav]').forEach((b) => {
    b.onclick = async () => {
      const row = data.items.find((x) => x.id === b.dataset.fav);
      b.disabled = true;
      pending = true;
      try {
        await api('/label', { id: row.id, favorite: !row.favorite });
        await load(false);
        renderCards();
      } catch (e) {
        notice(e.message);
        b.disabled = false;
      } finally {
        pending = false;
      }
    };
  });
}

function bindScan() {
  const b = document.querySelector('#scan');
  if (b) {
    b.onclick = async () => {
      b.disabled = true;
      b.textContent = '正在核对…';
      try {
        await api('/scan', {});
        await load();
        notice('已与本机技能目录完成同步。');
      } catch (e) {
        notice(e.message);
        b.disabled = false;
        b.textContent = '↻ 同步技能';
      }
    };
  }
}

async function renderDetail() {
  const stamp = ++generation;
  const x = data.items.find((item) => item.id === detailId);
  if (!x) {
    app.innerHTML = '<div class="empty"><p>没找到这个技能。</p><p><a class="button primary" href="#/skills">返回我的技能</a></p></div>';
    return;
  }
  const g = guide(x);
  const siblings = active().filter((item) => item.name === x.name && item.id !== x.id);

  app.innerHTML = '<div class="back-row"><a class="back" href="#/skills">← 返回我的技能</a></div>' +
    head(g.title, `${x.name} · ${formatLocationBadge(x)}`, '', '技能大白话指南') +
    callName(x) +
    `<div class="detail-grid">
      <div>
        <section class="panel guide-panel">
          <h2>先看这份大白话说明</h2>
          ${x.guide_status === 'stale' ? '<div class="warning">该技能的底层 SKILL.md 已更新，以下说明供参考，建议核对下方原始说明。</div>' : ''}
          ${x.guide_status === 'pending' ? '<div class="warning">这是新发现的技能，尚未整理大白话说明，可在右侧补充保存。</div>' : ''}
          ${siblings.length ? `<div class="warning">提示：本机存在同名技能的其他独立副本（位于 <code>${esc(siblings.map((s) => s.path).join('；'))}</code>），当前查看的是 <code>${esc(x.path)}</code>。</div>` : ''}
          ${Object.entries(guideFields).map(([k, v]) => `<section class="guide-block"><h3>${v}</h3><p>${esc(g[k])}</p></section>`).join('')}
          <small class="muted-guide">${x.guide_status === 'manual' ? '当前说明由你在本机工作台手动保存。' : '根据技能定义提炼整理，原始 SKILL.md 保留在下方供随时核对。'}</small>
        </section>
        <details class="panel raw-skill">
          <summary>查看原始 SKILL.md 说明（需要核对细节时展开）</summary>
          <pre id="skill-text">正在读取…</pre>
        </details>
      </div>
      <div>
        <section class="panel">
          <h2>整理到我的分类</h2>
          <form id="labels">
            <label class="field">技能来源
              <select id="edit-source">${Object.entries(sources).map(([k, v]) => `<option value="${k}" ${x.source === k ? 'selected' : ''}>${v}</option>`).join('')}</select>
            </label>
            <div class="field">勾选用途分类
              <div class="category-checks">${Object.entries(data.categories).map(([k, v]) => `<label><input type="checkbox" name="category" value="${k}" ${x.categories.includes(k) ? 'checked' : ''}>${esc(v)}</label>`).join('')}</div>
            </div>
            <label class="field">自定义分类
              <input id="custom-categories" value="${esc(x.categories.filter((c) => !data.categories[c]).join('，'))}" placeholder="如：工作常用，正在打磨" maxlength="328">
            </label>
            <p class="form-help">多个分类用逗号分隔，保存后自动同步到分类页（最多 8 个）。</p>
            <label class="field">个人使用备注
              <textarea id="edit-note" maxlength="2000" placeholder="记下你的触发技巧或注意事项">${esc(x.note)}</textarea>
            </label>
            <label class="toggle"><input type="checkbox" id="edit-favorite" ${x.favorite ? 'checked' : ''}> 加入我的收藏</label>
            <button class="button primary save-button" type="submit">保存分类与标记</button>
          </form>
        </section>
        <details class="panel">
          <summary>补充或修改大白话说明</summary>
          <form id="guide-editor">
            <label class="field">中文展示名称<input name="title" value="${esc(g.title)}" maxlength="2000"></label>
            ${Object.entries(guideFields).map(([k, v]) => `<label class="field">${v}<textarea name="${k}" maxlength="2000">${esc(g[k])}</textarea></label>`).join('')}
            <button class="button primary" type="submit">保存我的说明</button>
          </form>
        </details>
        <details class="panel">
          <summary>文件位置与副本信息</summary>
          <p>${esc(x.source_evidence || '暂无自动安装凭据，可在上方手动确认来源')}</p>
          <div class="path">${esc(x.path)}</div>
          <p>首次发现：${fmt(x.first_seen)}<br>最近修改：${fmt(x.modified_at)}<br>当前状态：${x.status === 'active' ? '文件正常' : '文件已移除'}</p>
          ${siblings.length ? `<p class="warning">同名其他副本：${siblings.map((s) => `<a href="#/skills/${s.id}">切换查看 (${esc(formatLocationBadge(s))}) →</a>`).join(' ')}</p>` : ''}
          <p>包含 ${x.file_count} 个文件：</p>
          <ul class="files">${x.files.map((f) => `<li>${esc(f)}</li>`).join('')}</ul>
        </details>
      </div>
    </div>`;

  bindCopy();

  async function saveForm(event, payload, message) {
    event.preventDefault();
    const b = event.target.querySelector('button');
    b.disabled = true;
    pending = true;
    try {
      await api('/label', { id: x.id, ...payload });
      await load(false);
      if (payload.guide_override) await renderDetail();
      notice(message);
    } catch (err) {
      notice(err.message);
    } finally {
      b.disabled = false;
      pending = false;
    }
  }

  document.querySelector('#labels').onsubmit = (e) => {
    const selected = [...document.querySelectorAll('input[name="category"]:checked')].map((c) => c.value);
    const custom = document.querySelector('#custom-categories').value
      .split(/[,，]/)
      .map((c) => c.trim())
      .filter(Boolean)
      .map((c) => Object.keys(data.categories).find((k) => data.categories[k] === c) || c);
    return saveForm(e, {
      source: document.querySelector('#edit-source').value,
      note: document.querySelector('#edit-note').value,
      favorite: document.querySelector('#edit-favorite').checked,
      categories: [...new Set([...selected, ...custom])]
    }, '分类与标记已保存，后续自动同步也会保留。');
  };

  document.querySelector('#guide-editor').onsubmit = (e) => {
    const values = {};
    for (const field of e.target.querySelectorAll('[name]')) values[field.name] = field.value;
    return saveForm(e, { guide_override: values }, '自定义大白话说明已保存，不会被自动扫描覆盖。');
  };

  try {
    const d = await api('/detail?id=' + encodeURIComponent(x.id));
    if (stamp === generation) document.querySelector('#skill-text').textContent = d.text;
  } catch (e) {
    if (stamp === generation) document.querySelector('#skill-text').textContent = x.status === 'missing' ? '文件已移除，仅保留历史记录。' : e.message;
  }
}

function renderCategories() {
  const rows = active();
  const descriptions = {
    video: '把文案和素材做成视频，或剪辑调整成片',
    publish: '成品做好以后，上传到 B 站、抖音、小红书等平台',
    bookmarks: '批量收集网页或视频链接，归档进收藏夹',
    transcription: '把音视频里的讲话转写成结构化文字稿',
    'video-planning': '先确定视频怎么讲、分镜节奏与画面风格',
    'video-motion': '花字标题、信息包装卡片、转场和动画组件',
    'video-tools': '检查视频工程、导出成片或转换制作流程',
    media: '为视频准备音乐、音效、TTS 配音与视觉素材',
    image: '做封面配图、信息图表、海报和设计稿',
    slides: '制作汇报 PPT、演示文稿和网页幻灯片',
    writing: '写文章、润色改稿、去 AI 味、提炼卖点',
    notes: '课程消化、复习笔记与知识图谱整理',
    research: '全网查资料、读网页、竞品调研与产品分析',
    office: '飞书文档、多维表格、日程与协同任务',
    files: '整理本机文件夹、素材库与网盘资源',
    modeling: '三维建模、材质布光、骨骼动画与渲染导出',
    development: '梳理需求、编写程序、排错调试与工程验证',
    automation: '定时巡检、重复动作编排与自动触发任务',
    skills: '发现、安装、体检、制作和维护 AI 技能',
    settings: '调整软件配置、环境切换与状态备份',
    other: '新发现或尚未归入特定场景的技能'
  };

  // 将有技能的活跃分类排在前面，0 技能的空分类弱化置于末尾，避免点进空列表失望
  const catStats = allCategories().map((k) => ({
    key: k,
    count: rows.filter((x) => x.categories.includes(k)).length
  })).sort((a, b) => (a.count === 0) - (b.count === 0) || b.count - a.count);

  app.innerHTML = head(
    '按用途找技能',
    '从你手头正要做的事情出发。进入任意技能详情页，还可以自由调整分类或新建专属分类。',
    '<button class="button primary" id="scan" type="button">↻ 同步技能</button>',
    '按场景找技能'
  ) + `<div class="category-grid">${catStats.map(({ key, count }) => `
    <button type="button" class="category-card ${count === 0 ? 'is-empty' : ''}" data-category="${esc(key)}" ${count === 0 ? 'disabled' : ''}>
      <span>${esc(catLabel(key))}</span>
      <b>${count}</b>
      <p>${esc(descriptions[key] || '你自定义的专属用途分类')}</p>
      <small>${count > 0 ? '查看这些技能 →' : '当前暂无归入此类的技能'}</small>
    </button>`).join('')}</div>`;

  bindScan();
  document.querySelectorAll('[data-category]:not(:disabled)').forEach((b) => {
    b.onclick = () => {
      filter = { q: '', source: '', category: b.dataset.category, sort: 'name' };
      location.hash = '/skills';
    };
  });
}

// 折叠连续针对同一技能同类型的重复事件，避免后台高频修改刷屏
function groupEvents(events) {
  const grouped = [];
  for (const e of events) {
    const prev = grouped[grouped.length - 1];
    if (prev && prev.id === e.id && prev.kind === e.kind && prev.path === e.path) {
      prev.repeat = (prev.repeat || 1) + 1;
    } else {
      grouped.push({ ...e, repeat: 1 });
    }
  }
  return grouped;
}

function renderActivity() {
  const grouped = groupEvents(data.events || []);
  const q = activityFilter.q.trim().toLowerCase();
  const filtered = grouped.filter((e) => {
    if (activityFilter.kind && e.kind !== activityFilter.kind) return false;
    if (!q) return true;
    return `${e.name} ${e.path} ${kinds[e.kind] || e.kind}`.toLowerCase().includes(q);
  });
  const visible = filtered.slice(0, activityFilter.limit);

  app.innerHTML = head(
    '技能变更',
    '新增、修改或移除本机技能文件后，这里会自动记录轨迹（连续重复修改已自动合并降噪）。',
    '<button class="button primary" id="scan" type="button">↻ 同步技能</button>',
    '文件同步动态'
  ) +
  `<div class="toolbar">
    <div class="search"><input id="act-search" type="search" placeholder="搜索技能名称或目录路径…" value="${esc(activityFilter.q)}"></div>
    <select id="act-kind" aria-label="变更类型筛选">
      <option value="">全部变更类型</option>
      ${Object.entries(kinds).map(([k, v]) => `<option value="${k}" ${activityFilter.kind === k ? 'selected' : ''}>${v}</option>`).join('')}
    </select>
  </div>
  <section class="panel">
    <div class="panel-title-row">
      <h2>最近动态</h2>
      <span class="tag">匹配 ${filtered.length} 条记录（原始保留上限 1000 条）</span>
    </div>
    <div id="event-list">
      ${visible.length ? visible.map((e) => `
        <div class="event">
          <div>${tag(kinds[e.kind] || e.kind, e.kind)}${e.repeat > 1 ? ` <span class="tag">×${e.repeat}</span>` : ''}</div>
          <div><a href="#/skills/${e.id}"><strong>${esc(e.name)}</strong></a><small>${esc(e.path)}</small></div>
          <time>${fmt(e.at)}</time>
        </div>`).join('') : '<div class="empty">没有匹配的变更记录。</div>'}
    </div>
    ${filtered.length > visible.length ? `<div class="load-more-row"><button class="button" id="load-more-events" type="button">加载更多记录（剩余 ${filtered.length - visible.length} 条）</button></div>` : ''}
  </section>`;

  bindScan();
  document.querySelector('#act-search').addEventListener('input', (e) => {
    activityFilter.q = e.target.value;
    activityFilter.limit = 80;
    renderActivity();
    const input = document.querySelector('#act-search');
    if (input) { input.focus(); input.setSelectionRange(input.value.length, input.value.length); }
  });
  document.querySelector('#act-kind').addEventListener('change', (e) => {
    activityFilter.kind = e.target.value;
    activityFilter.limit = 80;
    renderActivity();
  });
  const moreBtn = document.querySelector('#load-more-events');
  if (moreBtn) {
    moreBtn.onclick = () => {
      activityFilter.limit += 100;
      renderActivity();
    };
  }
}

function renderMonitor() {
  const m = data.monitor;
  const hidden = data.items.filter((x) => x.source === 'builtin');
  app.innerHTML = head(
    '技能监控',
    '关闭网页后，本机后台服务仍会持续留意新安装或新建的技能文件。',
    '<button class="button primary" id="scan" type="button">↻ 同步技能</button>',
    '后台自动发现'
  ) +
  `<section class="panel">
    <h2>自动发现状态</h2>
    <div class="monitor-state">● ${m.error ? '遇到问题' : m.running ? '正在运行' : '尚未运行'}</div>
    <p>巡检周期：每次检查完成后间隔 ${m.interval} 秒自动复查。<br>最近一次成功检查：${fmt(m.scanned_at)}${m.duration ? `（耗时 ${Math.round(m.duration * 1000)} ms）` : ''}</p>
    ${m.error ? `<div class="warning">${esc(m.error)}。已安全保留上次扫描快照，不会误判文件丢失。</div>` : ''}
    <h2 class="section-subhead">正在监控的本机目录</h2>
    ${(m.roots || []).map((r) => `<div class="path path-box">📂 ${esc(r)}</div>`).join('')}
    <p>在上述目录新建包含 <code>SKILL.md</code> 的文件夹即可自动纳入管理。尚未整理大白话说明的新技能会标注“说明待整理”。</p>
  </section>
  <section class="panel">
    <h2>自动过滤与防干扰规则</h2>
    <p>系统内置技能、插件缓存、归档目录与带 backup 后缀的备份目录会自动排除；你在详情页手动标记为“内置 / 不展示”的技能也不会混入日常列表。</p>
    <details>
      <summary>查看本次扫描跳过的系统/备份目录（${m.ignored?.length || 0}）</summary>
      <ul class="files">${(m.ignored || []).map((p) => `<li>${esc(p)}</li>`).join('')}</ul>
    </details>
  </section>
  <section class="panel">
    <h2>已手动隐藏的技能</h2>
    ${hidden.length ? hidden.map((x) => `<p><a href="#/skills/${x.id}">${esc(guide(x).title)} (${esc(x.name)}) →</a></p>`).join('') : '<p>暂无手动隐藏项（系统内置与缓存目录已自动排除）。</p>'}
  </section>`;
  bindScan();
}

if (integrated) {
  document.querySelectorAll('.project-nav').forEach((a) => {
    a.href = a.getAttribute('href').replace('http://127.0.0.1:8787', '');
  });
  const brandLink = document.querySelector('.brand');
  if (brandLink) brandLink.href = '/#ports';
}

window.addEventListener('hashchange', () => { notice(''); render(); window.scrollTo(0, 0); });
load();

setInterval(async () => {
  if (pending) return;
  const before = JSON.stringify([data.items, data.events]);
  if (!await load(false) || before === JSON.stringify([data.items, data.events])) return;
  if ((route === 'skills' && !detailId) || route === 'favorites') renderCards();
  else if (route === 'activity') renderActivity();
  else if (route === 'categories') renderCategories();
}, 8000);
