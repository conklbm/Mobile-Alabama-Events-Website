/* Client-side search over /api/search.json (built weekly). No dependencies. */
(function () {
  var INDEX = null, loading = null;
  function load() {
    if (INDEX) return Promise.resolve(INDEX);
    if (!loading) loading = fetch('/api/search.json').then(function (r) { return r.json(); }).then(function (d) { INDEX = d; return d; });
    return loading;
  }
  function norm(s) { return (s || '').toLowerCase().replace(/[’'"]/g, '').replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim(); }
  function search(q, limit) {
    var toks = norm(q).split(' ').filter(Boolean);
    if (!toks.length) return [];
    var out = [];
    INDEX.forEach(function (it) {
      var title = norm(it.t), hay = title + ' ' + norm(it.v) + ' ' + norm(it.c) + ' ' + norm(it.k);
      var ok = toks.every(function (t) { return hay.indexOf(t) > -1; });
      if (!ok) return;
      var score = 0;
      toks.forEach(function (t) { if (title.indexOf(t) === 0) score += 3; else if (title.indexOf(t) > -1) score += 2; else score += 1; });
      if (it.y === 'venue') score += 0.5;
      out.push([score, it]);
    });
    out.sort(function (a, b) { return b[0] - a[0] || (a[1].d || '').localeCompare(b[1].d || ''); });
    return out.slice(0, limit || 50).map(function (x) { return x[1]; });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function item(it) {
    var sub = it.y === 'venue' ? 'Venue · ' + esc(it.c) : esc(it.w || '') + (it.v ? ' · ' + esc(it.v) : '');
    return '<li><a href="' + esc(it.u) + '"><span class="s-title">' + esc(it.t) + '</span><span class="s-sub">' + sub + '</span></a></li>';
  }

  // header box: live dropdown
  var box = document.querySelector('[data-search]');
  if (box) {
    var input = box.querySelector('input'), list = box.querySelector('[data-search-results]');
    var timer;
    function render() {
      var q = input.value.trim();
      if (q.length < 2) { list.hidden = true; list.innerHTML = ''; return; }
      load().then(function () {
        var res = search(q, 8);
        list.innerHTML = res.length ? res.map(item).join('') + '<li class="s-all"><a href="/search/?q=' + encodeURIComponent(q) + '">All results for “' + esc(q) + '”</a></li>'
                                    : '<li class="s-none">Nothing matches “' + esc(q) + '”</li>';
        list.hidden = false;
      });
    }
    input.addEventListener('focus', load);
    input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(render, 120); });
    input.addEventListener('keydown', function (e) { if (e.key === 'Escape') { list.hidden = true; input.blur(); } });
    document.addEventListener('click', function (e) { if (!box.contains(e.target)) list.hidden = true; });
  }

  // /search/ page: full results
  var page = document.querySelector('[data-search-page]');
  if (page) {
    var q = new URLSearchParams(location.search).get('q') || '';
    var pin = page.querySelector('input'); if (pin) pin.value = q;
    var out = page.querySelector('[data-search-page-results]');
    if (q.trim().length) {
      document.title = '“' + q + '” — Mobile Bay Events';
      load().then(function () {
        var res = search(q, 100);
        out.innerHTML = res.length ? '<p class="count-line">' + res.length + ' result' + (res.length === 1 ? '' : 's') + ' for “' + esc(q) + '”</p><ul class="s-list">' + res.map(item).join('') + '</ul>'
                                   : '<p class="empty">Nothing matches “' + esc(q) + '”. Try a venue, an artist, or a word from the title.</p>';
      });
    }
  }
})();
