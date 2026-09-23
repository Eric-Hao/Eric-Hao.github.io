(() => {
  const dialog = document.createElement('dialog');
  dialog.className = 'image-viewer';
  dialog.setAttribute('aria-label', 'Research figure viewer / 论文配图');
  dialog.innerHTML = '<div class="viewer-toolbar"><button type="button" data-close autofocus>Close / 关闭 ×</button><button type="button" data-size aria-pressed="false">Zoom / 放大 ＋</button><button type="button" data-variant hidden>Particle view / 粒子版本</button><a data-original target="_blank" rel="noopener">Original / 原图 ↗</a></div><div class="viewer-stage"><img alt=""></div><p class="viewer-caption"></p>';
  document.body.append(dialog);
  const figure = dialog.querySelector('img');
  const stage = dialog.querySelector('.viewer-stage');
  const zoom = dialog.querySelector('[data-size]');
  let trigger;
  const variant=dialog.querySelector('[data-variant]');
  let particleView=false;
  variant.addEventListener('click',()=>{
    particleView=!particleView;
    figure.src=particleView?trigger.dataset.particleLarge:trigger.dataset.paperOriginal;
    variant.textContent=particleView?'Paper figure / 论文原图':'Particle view / 粒子版本';
    dialog.querySelector('.viewer-caption').textContent=particleView?'Particle interpretation of the paper figure':'Original paper figure';
  });
  document.querySelectorAll('[data-zoom]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0 || !dialog.showModal) return;
      event.preventDefault();
      trigger = link;
      const liveCover = link.querySelector('canvas.physics-particles');
      figure.src = link.dataset.paperOriginal || (liveCover ? liveCover.toDataURL('image/png') : link.href);
      particleView=false;variant.hidden=!link.dataset.particleLarge;variant.textContent='Particle view / 粒子版本';
      figure.alt = link.querySelector('img')?.alt || link.dataset.caption || 'Research figure';
      dialog.querySelector('[data-original]').href = link.dataset.paperOriginal || link.dataset.original || link.href;
      dialog.querySelector('.viewer-caption').textContent = link.dataset.paperOriginal ? 'Original paper figure' : (link.dataset.caption || figure.alt);
      dialog.classList.remove('is-zoomed');
      zoom.setAttribute('aria-pressed', 'false');
      zoom.textContent = 'Zoom / 放大 ＋';
      dialog.showModal();
      document.documentElement.classList.add('viewer-open');
      stage.scrollTo(0, 0);
    });
  });
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('viewer-open');
    trigger?.focus();
  });
  zoom.addEventListener('click', () => {
    const enlarged = dialog.classList.toggle('is-zoomed');
    zoom.setAttribute('aria-pressed', String(enlarged));
    zoom.textContent = enlarged ? 'Fit / 适应屏幕 −' : 'Zoom / 放大 ＋';
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
