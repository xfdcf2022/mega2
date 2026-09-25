'use strict';
window.searchTitles = (q) => {
  q = (q || '').trim().toLowerCase();
  return (window.SEARCH || []).filter(r => (r.t + ' ' + (r.c || '')).toLowerCase().includes(q));
};
