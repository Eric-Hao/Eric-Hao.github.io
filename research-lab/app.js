(() => {
  'use strict';
  const search = document.querySelector('#research-search');
  if (search) {
    const cards = [...document.querySelectorAll('[data-search]')];
    const filters = [...document.querySelectorAll('[data-filter]')];
    let category = 'all';
    const update = () => {
      const words = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      let shown = 0;
      for (const card of cards) {
        const match = (category === 'all' || card.dataset.category === category) && words.every(word => card.dataset.search.includes(word));
        card.hidden = !match;
        if (match) shown++;
      }
      for (const section of document.querySelectorAll('.collection')) section.hidden = ![...section.querySelectorAll('[data-search]')].some(card => !card.hidden);
      document.querySelector('.results-count').textContent = `${shown} ${shown === 1 ? 'entry' : 'entries'}`;
      document.querySelector('.empty-state').hidden = shown > 0;
      for (const filter of filters) {
        const active = filter.dataset.filter === category;
        filter.classList.toggle('is-active', active);
        filter.setAttribute('aria-pressed', String(active));
      }
    };
    filters.forEach(filter => filter.addEventListener('click', () => { category = filter.dataset.filter; update(); }));
    search.addEventListener('input', update);
    document.querySelector('#reset-search').addEventListener('click', () => { search.value = ''; category = 'all'; update(); search.focus(); });
    window.addEventListener('pageshow', update);
    update();
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
