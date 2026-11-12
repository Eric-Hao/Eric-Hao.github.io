(() => {
  'use strict';
  const search = document.querySelector('#research-search');
  if (search) {
    const results = document.querySelector('.research-results');
    const cards = [...results.querySelectorAll('[data-search]')];
    const filters = [...document.querySelectorAll('[data-filter]')];
    const refinements = [...document.querySelectorAll('.filter-panel input')];
    const sorts = [...document.querySelectorAll('[name="sort"]')];
    const views = [...document.querySelectorAll('[data-view]')];
    const popoverButtons = [...document.querySelectorAll('[data-popover]')];
    const allowed = (value, choices, fallback) => choices.includes(value) ? value : fallback;
    const choicesFor = name => refinements.filter(input => input.name === name).map(input => input.value);
    let state;
    let openButton = null;
    const readLocation = () => {
      const params = new URLSearchParams(location.search);
      state = {
        category: allowed(params.get('topic'), filters.map(button => button.dataset.filter), 'all'),
        query: params.get('q') || '',
        years: [...new Set(params.getAll('year').filter(value => choicesFor('year').includes(value)))],
        types: [...new Set(params.getAll('type').filter(value => choicesFor('type').includes(value)))],
        sort: allowed(params.get('sort'), sorts.map(input => input.value), 'newest'),
        view: allowed(params.get('display'), ['grid', 'list'], 'list')
      };
      search.value = state.query;
    };
    const closePopovers = (restoreFocus = false) => {
      const previous = openButton;
      for (const button of popoverButtons) {
        button.setAttribute('aria-expanded', 'false');
        document.getElementById(button.dataset.popover).hidden = true;
      }
      openButton = null;
      if (restoreFocus) previous?.focus();
    };
    const writeLocation = (mode = 'push') => {
      const url = new URL(location.href);
      for (const key of ['topic', 'q', 'year', 'type', 'sort', 'display']) url.searchParams.delete(key);
      if (state.category !== 'all') url.searchParams.set('topic', state.category);
      if (state.query.trim()) url.searchParams.set('q', state.query.trim());
      state.years.forEach(value => url.searchParams.append('year', value));
      state.types.forEach(value => url.searchParams.append('type', value));
      if (state.sort !== 'newest') url.searchParams.set('sort', state.sort);
      if (state.view !== 'list') url.searchParams.set('display', state.view);
      if (url.href !== location.href) history[mode === 'replace' ? 'replaceState' : 'pushState'](null, '', url);
    };
    const update = () => {
      const words = state.query.trim().toLowerCase().split(/\s+/).filter(Boolean);
      let shown = 0;
      for (const card of cards) {
        const match = (state.category === 'all' || card.dataset.category === state.category)
          && (!state.years.length || state.years.includes(card.dataset.year))
          && (!state.types.length || state.types.includes(card.dataset.type))
          && words.every(word => card.dataset.search.includes(word));
        card.hidden = !match;
        if (match) shown++;
      }
      const sorted = [...cards].sort((a, b) => {
        if (state.sort.startsWith('title')) return a.dataset.title.localeCompare(b.dataset.title, 'en', {sensitivity: 'base', numeric: true}) * (state.sort === 'title' ? 1 : -1);
        const ay = Number(a.dataset.year), by = Number(b.dataset.year);
        if (!ay && by) return 1;
        if (ay && !by) return -1;
        return (state.sort === 'oldest' ? ay - by : by - ay) || Number(a.dataset.order) - Number(b.dataset.order);
      });
      const fragment = document.createDocumentFragment();
      sorted.forEach(card => fragment.append(card));
      results.append(fragment);
      results.dataset.layout = state.view;
      document.querySelector('.results-count').textContent = `${shown} ${shown === 1 ? 'entry' : 'entries'}`;
      document.querySelector('.empty-state').hidden = shown > 0;
      document.querySelector('#clear-all').hidden = state.category === 'all' && !words.length && !state.years.length && !state.types.length;
      for (const filter of filters) {
        const active = filter.dataset.filter === state.category;
        filter.classList.toggle('is-active', active);
        filter.setAttribute('aria-pressed', String(active));
      }
      for (const input of refinements) input.checked = (input.name === 'year' ? state.years : state.types).includes(input.value);
      for (const input of sorts) input.checked = input.value === state.sort;
      for (const button of views) {
        const active = button.dataset.view === state.view;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-pressed', String(active));
      }
      const count = state.years.length + state.types.length;
      const badge = document.querySelector('.filter-count');
      badge.hidden = count === 0;
      badge.textContent = count;
      document.querySelector('#filter-toggle').setAttribute('aria-label', count ? `Filter, ${count} selected` : 'Filter research');
      document.querySelector('.search-toggle')?.classList.toggle('has-query', !!words.length);
    };
    const change = (mode = 'push') => { update(); writeLocation(mode); };
    const reset = () => {
      state.category = 'all'; state.query = ''; state.years = []; state.types = [];
      search.value = ''; change(); closePopovers();
    };
    filters.forEach(button => button.addEventListener('click', () => { state.category = button.dataset.filter; change(); closePopovers(); }));
    search.addEventListener('input', () => { state.query = search.value; change('replace'); });
    refinements.forEach(input => input.addEventListener('change', () => {
      state.years = refinements.filter(i => i.name === 'year' && i.checked).map(i => i.value);
      state.types = refinements.filter(i => i.name === 'type' && i.checked).map(i => i.value);
      change();
    }));
    sorts.forEach(input => input.addEventListener('change', () => { state.sort = input.value; change(); closePopovers(true); }));
    views.forEach(button => button.addEventListener('click', () => { state.view = button.dataset.view; change(); closePopovers(); }));
    document.querySelector('#clear-refinements').addEventListener('click', () => { state.years = []; state.types = []; change(); });
    document.querySelector('#clear-all').addEventListener('click', reset);
    document.querySelector('#reset-search').addEventListener('click', () => { reset(); filters[0].focus(); });
    for (const button of popoverButtons) button.addEventListener('click', () => {
      const wasOpen = button === openButton;
      closePopovers();
      if (!wasOpen) {
        openButton = button;
        button.setAttribute('aria-expanded', 'true');
        const panel = document.getElementById(button.dataset.popover);
        panel.hidden = false;
        panel.querySelector('input, button')?.focus();
      }
    });
    document.querySelector('[data-close-popover]').addEventListener('click', () => closePopovers(true));
    document.addEventListener('keydown', event => { if (event.key === 'Escape' && openButton) { event.preventDefault(); closePopovers(true); } });
    document.addEventListener('click', event => {
      if (openButton && !event.target.closest('.popover') && !event.target.closest('[data-popover]')) closePopovers();
    });
    document.addEventListener('focusin', event => {
      if (openButton && !event.target.closest('.popover') && !event.target.closest('[data-popover]')) closePopovers();
    });
    window.addEventListener('popstate', () => { closePopovers(); readLocation(); update(); });
    window.addEventListener('pageshow', () => { readLocation(); update(); });
    readLocation(); update();
  }
  const viewer = document.querySelector('.image-viewer');
  if (viewer) {
    let opener = null;
    const close = () => { if (viewer.open) viewer.close(); };
    for (const button of document.querySelectorAll('.figure-open')) button.addEventListener('click', () => {
      if (viewer.open) return;
      opener = button;
      const image = viewer.querySelector('img');
      image.src = button.dataset.image;
      image.alt = button.querySelector('img').alt;
      viewer.querySelector('p').textContent = button.dataset.caption;
      viewer.showModal();
      document.documentElement.style.overflow = 'hidden';
      viewer.querySelector('.viewer-close').focus();
    });
    viewer.querySelector('.viewer-close').addEventListener('click', close);
    viewer.addEventListener('click', event => { if (event.target === viewer) close(); });
    viewer.addEventListener('close', () => { document.documentElement.style.overflow = ''; opener?.focus(); });
    window.addEventListener('pagehide', close);
  }
  for (const button of document.querySelectorAll('.copy-citation')) button.addEventListener('click', async () => {
    const container = button.closest('.citation');
    const status = container.querySelector('.copy-status');
    try { await navigator.clipboard.writeText(container.querySelector('pre').textContent); status.textContent = 'Citation copied.'; button.textContent = 'Copied'; }
    catch { status.textContent = 'Select and copy the citation below.'; }
  });
  const links = [...document.querySelectorAll('.article-aside nav a')];
  if (links.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) for (const link of links) {
        if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }
    }, { rootMargin: '-15% 0px -60% 0px' });
    document.querySelectorAll('.essay-section').forEach(section => observer.observe(section));
  }
})();
