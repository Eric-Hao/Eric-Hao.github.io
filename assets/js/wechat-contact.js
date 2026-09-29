(() => {
  document.querySelectorAll('[data-wechat]').forEach(root => {
    const trigger = root.querySelector('.wechat-trigger');
    const panel = root.querySelector('.wechat-popover');
    const status = root.querySelector('.wechat-status');
    let pinned = false;
    const open = value => {
      panel.hidden = !value;
      trigger.setAttribute('aria-expanded', String(value));
      if (!value) status.textContent = '';
    };
    root.addEventListener('pointerenter', e => { if (e.pointerType === 'mouse') open(true); });
    root.addEventListener('pointerleave', () => { if (!pinned && !root.contains(document.activeElement)) open(false); });
    root.addEventListener('focusin', () => open(true));
    root.addEventListener('focusout', () => requestAnimationFrame(() => {
      if (!root.contains(document.activeElement)) { pinned = false; open(false); }
    }));
    trigger.addEventListener('click', () => { pinned = !pinned; open(pinned); });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && !panel.hidden) { pinned = false; trigger.focus(); open(false); }
    });
    document.addEventListener('click', e => {
      if (!root.contains(e.target)) { pinned = false; open(false); }
    });
    root.querySelector('.wechat-copy').addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(root.querySelector('.wechat-id').textContent.trim());
        status.textContent = '已复制 / Copied';
      } catch (_) {
        status.textContent = '请选中上方微信号手动复制';
      }
    });
  });
})();
