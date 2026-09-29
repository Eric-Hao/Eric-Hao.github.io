(() => {
  document.querySelector('[data-history-back]')?.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (window.history.length > 1) {
      event.preventDefault();
      window.history.back();
    }
  });
  const dialog = document.createElement('dialog');
  dialog.className = 'image-viewer';
  dialog.setAttribute('aria-label', 'Research figure viewer / 论文配图');
  dialog.innerHTML = '<button class="viewer-stage" type="button" autofocus aria-label="Close enlarged image / 关闭大图"><img alt=""></button><p class="viewer-caption"></p>';
  document.body.append(dialog);
  const figure = dialog.querySelector('img');
  const stage = dialog.querySelector('.viewer-stage');
  let trigger;
  document.querySelectorAll('[data-zoom]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0 || !dialog.showModal) return;
      event.preventDefault();
      trigger = link;
      const liveCover = link.querySelector('canvas.physics-particles');
      figure.src = link.dataset.paperOriginal || (liveCover ? liveCover.toDataURL('image/png') : link.href);
      figure.alt = link.querySelector('img')?.alt || link.dataset.caption || 'Research figure';
      dialog.querySelector('.viewer-caption').textContent = link.dataset.paperOriginal ? 'Original paper figure' : (link.dataset.caption || figure.alt);
      dialog.showModal();
      document.documentElement.classList.add('viewer-open');
      stage.scrollTo(0, 0);
    });
  });
  stage.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('viewer-open');
    trigger?.focus();
  });
  document.querySelectorAll('[data-copy-bib]').forEach(button => {
    button.addEventListener('click', async () => {
      const code = document.getElementById(button.getAttribute('aria-controls'));
      const status = button.closest('.citation').querySelector('.copy-status');
      try {
        await navigator.clipboard.writeText(code.textContent);
        status.textContent = 'Copied / 已复制';
      } catch {
        const range = document.createRange();
        range.selectNodeContents(code);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        status.textContent = 'Select Copy or press Ctrl/Cmd+C / 请复制选中的引用代码';
      }
    });
  });
})();
