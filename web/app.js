const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const params = new URLSearchParams(window.location.search);

function animate(node, cls = 'live-enter') {
  if (!node) return;
  node.classList.remove(cls);
  void node.offsetWidth;
  node.classList.add(cls);
}

async function getVersions(query) {
  const response = await fetch(`/api/versions?${query}`, { cache: 'no-store', headers: { Accept: 'application/json' } });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || `Live source returned HTTP ${response.status}`);
  return body;
}

function status(node, message, kind = 'idle') {
  node.dataset.state = kind;
  node.querySelector('p').textContent = message;
  animate(node);
}

function safe(value) {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'string') return value;
  return JSON.stringify(value, null, 2);
}

function esc(value) {
  return String(value).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch]);
}

function renderLookup(data) {
  const root = document.querySelector('#lookup-results');
  root.replaceChildren();
  const heading = document.createElement('div');
  heading.className = 'result-heading';
  heading.innerHTML = `<div><p class="eyebrow">LIVE RESPONSE / ${esc(data.source)}</p><h2>${data.versions.length} linked source record${data.versions.length === 1 ? '' : 's'}</h2><p>Retrieved ${esc(new Date(data.retrieved_at).toLocaleString())}. TED change-reference links determine the chain.</p></div><span class="response-total">${esc(data.pairs.length)}<small>VERIFIED LINKS</small></span>`;
  root.append(heading);
  if (!data.versions.length) {
    const empty = document.createElement('p');
    empty.className = 'empty-result';
    empty.textContent = 'TED returned no matching published notice. No local data was substituted.';
    root.append(empty);
  }
  for (const version of data.versions) {
    const card = document.createElement('article');
    card.className = 'edition-card';
    const titles = version['notice-title'] || {};
    const title = titles.eng || Object.values(titles)[0] || 'Title not supplied by TED';
    card.innerHTML = `<div class="edition-index">v${esc(version['notice-version'] ?? '?')}<small>${esc(version.PD || 'DATE NOT PROVIDED')}</small></div><div class="edition-description"><p class="eyebrow">${esc(version['notice-type'] || 'NOTICE TYPE NOT PROVIDED')}</p><h3>${esc(title)}</h3><p>Publication <code>${esc(version.ND || 'not supplied')}</code> · ${esc(version['notice-identifier'] || 'no notice identity')}</p><div class="edition-proof"><span>SHA-256</span><code>${esc(version.record_hash)}</code></div></div><div class="edition-action"><a href="${esc(version.source_url)}" target="_blank" rel="noopener noreferrer">Open TED source ↗</a></div>`;
    root.append(card);
  }
  if (data.pair_available && data.publication) {
    const action = document.createElement('a');
    action.className = 'compare-action';
    action.href = `compare.html?publication=${encodeURIComponent(data.publication)}`;
    action.innerHTML = 'Inspect explicit TED amendment links <b>→</b>';
    root.append(action);
  } else if (data.versions.length) {
    const note = document.createElement('p');
    note.className = 'empty-result';
    note.textContent = data.truncated
      ? 'TED returned more linked records than this bounded lookup can safely retrieve. No incomplete chain will be compared or scored.'
      : 'TED returned no change notice that explicitly references this notice version. Records grouped by procedure, matching title, or nearby date are not treated as amendments.';
    root.append(note);
  }
  root.hidden = false;
  animate(root);
}

const form = document.querySelector('#publication-form');
if (form) {
  const state = document.querySelector('#lookup-status');
  const submit = document.querySelector('#lookup-submit');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const publication = new FormData(form).get('publication').trim();
    if (!/^[0-9]{1,8}-20[0-9]{2}$/.test(publication)) {
      status(state, 'Publication number format is invalid. Enter digits followed by a four-digit year.', 'error');
      return;
    }
    submit.disabled = true;
    form.classList.add('is-loading');
    document.querySelector('#lookup-results').hidden = true;
    status(state, `Requesting publication ${publication} from TED…`, 'loading');
    try {
      const data = await getVersions(`publication=${encodeURIComponent(publication)}`);
      renderLookup(data);
      status(state, `TED responded at ${new Date(data.retrieved_at).toLocaleTimeString()}. This is live source data.`, 'success');
    } catch (error) {
      status(state, `${error.message}. Retry when the source is reachable.`, 'error');
    } finally {
      submit.disabled = false;
      form.classList.remove('is-loading');
    }
  });
}

function flatten(value, prefix = '', out = {}) {
  if (Array.isArray(value)) value.forEach((child, index) => flatten(child, `${prefix}[${index}]`, out));
  else if (value && typeof value === 'object') Object.keys(value).sort().forEach((key) => flatten(value[key], prefix ? `${prefix}.${key}` : key, out));
  else if (prefix) out[prefix] = value;
  return out;
}

function diffRecords(prior, current) {
  const before = flatten(prior), after = flatten(current);
  return [...new Set([...Object.keys(before), ...Object.keys(after)])].sort()
    .filter((field) => JSON.stringify(before[field]) !== JSON.stringify(after[field]))
    .map((field) => ({ field, prior: before[field], current: after[field] }));
}

function renderPair(data, selectedPair = 0) {
  const output = document.querySelector('#compare-output');
  const versions = data.versions;
  const pair = data.pairs[selectedPair];
  if (!pair) return;
  const prior = versions[pair.prior_index], current = versions[pair.current_index];
  if (!prior || !current) return;
  const changes = diffRecords(prior, current);
  const rows = changes.length ? changes.map((change) => `<article class="live-diff-row"><div class="live-diff-field"><span>CHANGED SOURCE FIELD</span><code>${esc(change.field)}</code></div><div class="live-diff-values"><div><small>PRIOR VALUE</small><pre>${esc(safe(change.prior))}</pre></div><b aria-hidden="true">→</b><div><small>CURRENT VALUE</small><pre>${esc(safe(change.current))}</pre></div></div></article>`).join('') : '<p class="empty-result">No scalar field differences were found in the fields returned by TED. This does not prove the full documents are identical.</p>';
  const options = data.pairs.map((candidate, index) => {
    const left = versions[candidate.prior_index], right = versions[candidate.current_index];
    return `<option value="${index}">${esc(left.ND || 'prior')} → ${esc(right.ND || 'change notice')}</option>`;
  }).join('');
  output.innerHTML = `<div class="pair-selectors"><label>Explicit source reference<select id="pair-choice">${options}</select></label><span aria-hidden="true">BT-758</span><a class="back-desk" href="index.html">New lookup ↗</a></div><div class="source-provenance"><div><span>CHANGED NOTICE / SOURCE</span><a href="${esc(prior.source_url)}" target="_blank" rel="noopener noreferrer">${esc(prior.ND || 'Open source')} ↗</a><code>${esc(prior.record_hash)}</code></div><div><span>AMENDMENT / SOURCE</span><a href="${esc(current.source_url)}" target="_blank" rel="noopener noreferrer">${esc(current.ND || 'Open source')} ↗</a><code>${esc(current.record_hash)}</code></div></div><div class="diff-summary"><span class="delta-count">${changes.length}</span><div><strong>Field differences in the records joined by TED's amendment reference</strong><small>Direct structural comparison · no generated summary · no validator score</small></div></div><div class="live-diff-list">${rows}</div>`;
  output.hidden = false;
  output.querySelector('#pair-choice').value = String(selectedPair);
  output.querySelector('#pair-choice').addEventListener('change', (event) => renderPair(data, Number(event.currentTarget.value)));
  animate(output, 'diff-enter');
}

async function loadCompare(publication) {
  const state = document.querySelector('#compare-status');
  const reload = document.querySelector('#reload-live');
  const output = document.querySelector('#compare-output');
  output.hidden = true;
  if (!publication) {
    status(state, 'No TED publication is selected. Start at the live desk and open a source with an explicit amendment link.', 'error');
    return;
  }
  reload.disabled = true;
  status(state, 'Refreshing notice versions from TED…', 'loading');
  try {
    const data = await getVersions(`publication=${encodeURIComponent(publication)}`);
    if (!data.pair_available) throw new Error('TED does not provide a complete explicit amendment link for this publication');
    document.querySelector('#pair-title').textContent = data.versions.find((entry) => entry.ND === publication)?.['notice-title']?.eng || publication;
    document.querySelector('#pair-meta').textContent = `${data.pairs.length} explicit amendment link${data.pairs.length === 1 ? '' : 's'} · source publication ${publication} · retrieved ${new Date(data.retrieved_at).toLocaleString()}`;
    document.querySelector('#pair-state').innerHTML = '<i></i> IDENTITY LINK VERIFIED';
    renderPair(data, 0);
    status(state, `TED explicitly linked ${data.pairs.length} change notice(s) to this record.`, 'success');
  } catch (error) {
    status(state, `${error.message}. No stored or sample records were used.`, 'error');
  } finally {
    reload.disabled = false;
  }
  history.replaceState({}, '', `compare.html?publication=${encodeURIComponent(publication)}`);
}

const comparePage = document.querySelector('[data-page="compare"]');
if (comparePage) {
  document.querySelector('#reload-live').addEventListener('click', () => loadCompare(params.get('publication')));
  if (params.has('publication')) loadCompare(params.get('publication'));
}

// Small disclosure interactions remain available without hover or motion.
document.querySelectorAll('.role-row summary').forEach((summary) => {
  summary.addEventListener('click', () => requestAnimationFrame(() => animate(summary.parentElement, 'role-enter')));
});
