'use strict';
// 章节页：双 Tab(文本/原稿/对照) + 右侧章节目录侧边栏
// 状态记忆：localStorage 持久化 当前模式 + 侧边栏开关，跨章节跳转后自动还原
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
  mountFs();
  fillPgv();
});

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

// 右侧滑出章节目录（数据来自 ../data.js -> window.BOOK.nav）
function esc(s){return (s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function fsKey(){ const v = window.BOOK && window.BOOK.id ? window.BOOK.id : ''; return 'pdfbook.fs.' + v; }
function fsLoad(){ try { return localStorage.getItem(fsKey()) === '1'; } catch (e) { return false; } }
function fsSave(on){ try { localStorage.setItem(fsKey(), on ? '1' : '0'); } catch (e) {} }
function mountFs(){
  const cur = document.body && document.body.dataset.ch;
  if (!window.BOOK || !Array.isArray(window.BOOK.nav) || !cur) return;
  const nav = window.BOOK.nav;
  if (!nav.length) return;
  const items = nav.map(n =>
    '<li><a class="lvl' + (n.level || 0) + (n.id === cur ? ' cur' : '') + '" href="' +
    n.url + '">' + esc(n.title) + '</a></li>').join('');
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
  side.innerHTML = '<div class="hd"><h3>章节目录</h3><button class="cl" title="关闭">×</button></div>' +
    '<ol>' + items + '</ol>' + pn;
  document.body.appendChild(btn);
  document.body.appendChild(side);
  const setOpen = (on) => {
    side.classList.toggle('open', on);
    btn.style.right = on ? 'min(320px,80vw)' : '-2px';
    fsSave(on);
  };
  btn.addEventListener('click', () => setOpen(!side.classList.contains('open')));
  side.querySelector('.cl').addEventListener('click', () => setOpen(false));
  setOpen(fsLoad());
}
