'use strict';
// 章节页：双 Tab(文本/原稿/对照) + 右侧章节目录侧边栏
// 状态记忆：localStorage 持久化 当前模式 + 侧边栏开关，跨章节跳转后自动还原
// 目录双模式：书签目录(bm) ⇄ 印刷目录(tp，来自 Inhalt 页坐标解析)
document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tabs button');
  const panels = document.querySelectorAll('section.list');
  if (tabs.length) {
    const vol = window.BOOK && window.BOOK.id ? window.BOOK.id : '';
    const key = 'pdfbook.tab.' + vol;
    const loadTab = () => { try { return localStorage.getItem(key); } catch (e) { return null; } };
    const saveTab = (k) => { try { localStorage.setItem(key, k); } catch (e) {} };
    const show = (k) => {
      tabs.forEach(b => b.classList.toggle('on', b.dataset.tab === k));
      panels.forEach(s => s.classList.toggle('hidden', !s.classList.contains('tab-' + k)));
    };
    const first = tabs[0].dataset.tab;
    let init = loadTab();
    if (init === null || !Array.from(tabs).some(b => b.dataset.tab === init)) init = first;
    show(init);
    tabs.forEach(b => b.addEventListener('click', () => { show(b.dataset.tab); saveTab(b.dataset.tab); }));
  }
  mountTocMode();
  mountFs();
  fillPgv();
});

// ---------- 目录双模式 ----------
function tpKey() {
  const v = window.BOOK && window.BOOK.id ? window.BOOK.id : '';
  return 'pdfbook.tdm.' + v;
}
function tpLoad() { try { return localStorage.getItem(tpKey()) === 'tp'; } catch (e) { return false; } }
function tpSave(on) { try { localStorage.setItem(tpKey(), on ? 'tp' : 'bm'); } catch (e) {} }
function hasTp() { return window.BOOK && Array.isArray(window.BOOK.tp) && window.BOOK.tp.length; }
function modeNav() { return tpLoad() && hasTp() ? window.BOOK.tp : window.BOOK.nav; }

function tocBtnRow() {
  const d = document.createElement('div');
  d.className = 'tocmode';
  d.innerHTML = '<button data-m="bm">书签</button><button data-m="tp" class="tp">印刷目录</button>';
  return d;
}
function setTocBtn(row, on) {
  row.querySelectorAll('button').forEach(b => b.classList.toggle('on', (b.dataset.m === 'tp') === on));
}

// 卷页（章节目录页）：两种目录可切换
function mountTocMode() {
  const box = document.getElementById('tocList');
  if (!box || !window.BOOK || !Array.isArray(window.BOOK.nav)) return;
  let row = null;
  if (hasTp()) {
    row = tocBtnRow();
    const m = document.getElementById('tocMode');
    if (m) { m.appendChild(row); m.hidden = false; }
  }
  const render = () => {
    const on = tpLoad() && hasTp();
    if (row) setTocBtn(row, on);
    const nav = on ? window.BOOK.tp : window.BOOK.nav;
    box.innerHTML = nav.map(n => {
      const s = on && n.print_start ? '<span>S.' + n.print_start + '</span>' : '';
      return '<li><lvl>L' + (n.level || 0) + '</lvl><a href="' + n.url + '">' + esc(n.title) +
        '</a>' + s + '</li>';
    }).join('');
  };
  if (row) row.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    tpSave(b.dataset.m === 'tp');
    render();
  });
  render();
}

// 底部栏 上一章/下一章
function fillPgv() {
  const pv = document.getElementById('pgPrev'), nx = document.getElementById('pgNext');
  if (!pv && !nx) return;
  const cur = document.body && document.body.dataset.ch;
  const has = window.BOOK && Array.isArray(window.BOOK.nav) && cur;
  if (!has) { pv && (pv.style.display = 'none'); nx && (nx.style.display = 'none'); return; }
  const nav = window.BOOK.nav, i = nav.findIndex(n => n.id === cur);
  const p = nav[i - 1], q = nav[i + 1];
  if (p) { pv.href = p.url; pv.textContent = '← 上一章'; pv.title = p.title; }
  else pv.setAttribute('disabled', '');
  if (q) { nx.href = q.url; nx.textContent = '下一章 →'; nx.title = q.title; }
  else nx.setAttribute('disabled', '');
}

// 右侧滑出章节目录
function esc(s){return (s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function fsKey(){ const v = window.BOOK && window.BOOK.id ? window.BOOK.id : ''; return 'pdfbook.fs.' + v; }
function fsLoad(){ try { return localStorage.getItem(fsKey()) === '1'; } catch (e) { return false; } }
function fsSave(on){ try { localStorage.setItem(fsKey(), on ? '1' : '0'); } catch (e) {} }
function mountFs(){
  const cur = document.body && document.body.dataset.ch;
  if (!window.BOOK || !Array.isArray(window.BOOK.nav) || !cur) return;
  const itemsHtml = () => {
    const on = tpLoad() && hasTp();
    const nav = on ? window.BOOK.tp : window.BOOK.nav;
    return nav.map(n => {
      const isCur = on ? (cur && n.url && n.url.indexOf('/' + cur + '-') >= 0) : (n.id === cur);
      return '<li><a class="lvl' + (n.level || 0) + (isCur ? ' cur' : '') + '" href="' +
        n.url + '">' + esc(n.title) + '</a></li>';
    }).join('');
  };
  const nav = window.BOOK.nav;
  if (!nav.length) return;
  const i = nav.findIndex(n => n.id === cur);
  const p = nav[i - 1], q = nav[i + 1];
  const pn = '<div class="pn">' +
    (p ? '<a href="' + p.url + '">← ' + esc(p.title).slice(0, 18) + '</a>' : '<span></span>') +
    (q ? '<a href="' + q.url + '">' + esc(q.title).slice(0, 18) + ' →</a>' : '<span></span>') +
    '</div>';
  const btn = document.createElement('button');
  btn.className = 'fs-btn'; btn.id = 'fsBtn'; btn.textContent = '章节目录';
  btn.title = '切换章节';
  const side = document.createElement('aside');
  side.className = 'fside'; side.id = 'fsSide';
  const hd = document.createElement('div');
  hd.className = 'hd';
  hd.innerHTML = '<h3>章节目录</h3>';
  const cl = document.createElement('button');
  cl.className = 'cl'; cl.title = '关闭'; cl.innerHTML = '&times;';
  hd.appendChild(cl);
  let row = null;
  if (hasTp()) { row = tocBtnRow(); }
  const ol = document.createElement('ol');
  const refill = () => { ol.innerHTML = itemsHtml(); if (row) setTocBtn(row, tpLoad() && hasTp()); };
  side.appendChild(hd);
  if (row) side.appendChild(row);
  refill();
  side.appendChild(ol);
  const wrapP = document.createElement('div'); wrapP.innerHTML = pn; side.appendChild(wrapP.firstChild);
  document.body.appendChild(btn);
  document.body.appendChild(side);
  if (row) row.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    tpSave(b.dataset.m === 'tp');
    refill();
  });
  const setOpen = (on) => {
    side.classList.toggle('open', on);
    btn.style.right = on ? 'min(320px,80vw)' : '-2px';
    fsSave(on);
  };
  btn.addEventListener('click', () => setOpen(!side.classList.contains('open')));
  cl.addEventListener('click', () => setOpen(false));
  setOpen(fsLoad());
}
