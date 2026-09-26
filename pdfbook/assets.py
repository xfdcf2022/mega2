# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

CSS = """/* site.css */
:root{--bg:#faf7f2;--fg:#26221c;--accent:#8a3b12;--muted:#6b6255;--line:#e3ddd2;
--serif:Georgia,'Noto Serif SC','Songti SC',serif;--sans:system-ui,'PingFang SC',sans-serif}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font:17px/1.7 var(--serif);background:var(--bg);color:var(--fg)}
nav.bar{position:sticky;top:0;z-index:9;background:#fff;border-bottom:1px solid var(--line);
display:flex;gap:12px;align-items:center;padding:8px 14px;font-family:var(--sans);font-size:.92em}
nav.bar a{color:var(--accent);text-decoration:none}
main{max-width:46rem;margin:0 auto;padding:18px 16px 90px}
h1,h2,h3{line-height:1.3;font-family:var(--sans)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin:16px 0}
.gcard{border:1px solid var(--line);padding:14px 16px;border-radius:10px;text-decoration:none;
color:inherit;display:block;background:#fff}
.gcard h3{margin:0 0 4px;color:var(--accent);font-size:1.02em}
.gcard span{color:var(--muted);font-size:.85em}
.toc{list-style:none;padding:0;margin:8px 0}
.toc li{display:flex;gap:10px;align-items:baseline;padding:5px 0;border-bottom:1px dotted #e8e2d6}
.toc lvl{color:var(--muted);font-size:.8em;min-width:2.2em}
.toc a{color:var(--fg);text-decoration:none}
.toc a:hover{color:var(--accent)}
.tabs{margin:14px 0;display:flex;gap:8px;font-family:var(--sans)}
.tabs button{border:1px solid #ccc;background:#fff;padding:6px 16px;border-radius:6px;cursor:pointer}
.tabs button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.hidden{display:none}
.dualrow{display:flex;gap:16px;align-items:flex-start;margin:10px 0 22px;padding-bottom:14px;
border-bottom:1px solid var(--line)}
.dual-wide{max-width:92rem;margin:0 auto;padding:18px 16px 90px}
.dtext{flex:1 1 46%;min-width:0}
.dimg{flex:1 1 54%;min-width:0}
.dimg img{width:100%;height:auto;box-shadow:0 1px 5px rgba(0,0,0,.22)}
@media(max-width:760px){.dualrow{flex-direction:column}}
.pg{display:inline-block;margin:14px 0 2px;padding:1px 8px;font-size:.76em;color:var(--muted);
background:#f2ecdf;border-radius:4px;font-family:var(--sans)}
aside.fn{font-size:.85em;color:#555;border-top:1px solid var(--line);margin:8px 0 14px;padding-top:6px}
aside.fn.hdr{display:block;margin:2px 0 0;padding:0 0 2px;border:0;font-size:.78em;color:#999;font-style:italic;font-family:var(--sans)}
.pgv{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid var(--line);
display:flex;justify-content:space-between;align-items:center;padding:8px 16px;font-family:var(--sans)}
.pgv a{color:var(--accent);text-decoration:none}
.pgv .pnbar{display:flex;gap:10px}
.pgv .pnbar a{border:1px solid var(--line);border-radius:6px;padding:4px 12px;background:#fbf7ef}
.pgv .pnbar a:hover{border-color:var(--accent)}
.pgv .pnbar a[disabled]{pointer-events:none;opacity:.35}
.pgv .pgrange{color:var(--muted);font-size:.85em}
img.leaf{max-width:100%;height:auto;box-shadow:0 1px 5px rgba(0,0,0,.28);margin:12px auto;display:block}
.fs-btn{position:fixed;right:-2px;top:42%;z-index:20;writing-mode:vertical-rl;background:var(--accent);
color:#fff;border:none;border-radius:8px 0 0 8px;padding:12px 6px;cursor:pointer;font-size:.85em;
font-family:var(--sans);letter-spacing:.12em}
.fside{position:fixed;top:0;right:0;bottom:0;width:min(320px,80vw);background:#fff;border-left:1px solid var(--line);
z-index:30;transform:translateX(102%);transition:transform .18s ease;overflow-y:auto;padding:14px 12px;
font-family:var(--sans)}
.fside.open{transform:none}
.fside .hd{display:flex;justify-content:space-between;align-items:center;margin:2px 0 8px}
.fside h3{margin:0;font-size:.95em}
.fside .cl{background:none;border:none;color:var(--muted);font-size:1.2em;cursor:pointer}
.fside ol{list-style:none;margin:0;padding:0}
.fside li{margin:0}
.fside a{display:block;padding:5px 8px;border-radius:6px;color:var(--fg);text-decoration:none;
font-size:.88em;line-height:1.35;border-left:2px solid transparent}
.fside a:hover{background:#f4eee1}
.fside a.cur{border-left-color:var(--accent);color:var(--accent);background:#faf4e8;font-weight:600}
.lvl0{padding-left:2px}.lvl1{padding-left:12px}.lvl2{padding-left:24px}.lvl3{padding-left:36px}
.fside .pn{display:flex;gap:8px;margin-top:14px;border-top:1px solid var(--line);padding-top:10px;font-size:.85em}
.fside .pn a{flex:1;border:1px solid var(--line);text-align:center;padding:6px;color:var(--accent)}
.tocmode{display:inline-flex;gap:4px;margin:0 0 10px;font-family:var(--sans)}
.tocmode button{border:1px solid var(--line);background:#fff;color:var(--muted);
  font-size:.8em;padding:4px 10px;border-radius:16px;cursor:pointer}
.tocmode button.on{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
.fside .tocmode{display:flex;margin:0 0 8px}
.fside .tocmode button{flex:1;text-align:center}
@media(max-width:640px){body{font-size:15px}}
"""

J_APP = """'use strict';
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
"""

J_SEARCH = """'use strict';
window.searchTitles = (q) => {
  q = (q || '').trim().toLowerCase();
  return (window.SEARCH || []).filter(r => (r.t + ' ' + (r.c || '')).toLowerCase().includes(q));
};
"""

# data 通过 <script src> 注入，file:// 下可用
ASSETS = {
    "css/site.css": CSS,
    "js/app.js": J_APP,
    "js/search.js": J_SEARCH,
    "js/i18n.js": 'window.I18N={zh:{title:"静态章节阅读站"},de:{title:"Statische Lesestätte"}};',
}


def install(a_dir: Path) -> None:
    for rel, content in ASSETS.items():
        f = Path(a_dir) / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8")