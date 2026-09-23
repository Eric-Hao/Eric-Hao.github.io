(() => {
  const svg = document.querySelector('#field');
  if (!svg) return;
  const ns = 'http://www.w3.org/2000/svg';
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const paths = Array.from({ length: 40 }, () => {
    const path = document.createElementNS(ns, 'path');
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', '#b58269');
    path.setAttribute('stroke-width', '.65');
    path.setAttribute('opacity', '.7');
    svg.appendChild(path);
    return path;
  });
  function draw(seconds) {
    // Bounded, slow deformations retain the original silhouette at rest.
    const phase = .42 * Math.sin(seconds * .24);
    const breath = 1 + .025 * Math.sin(seconds * .36);
    const tilt = .045 * Math.sin(seconds * .18);
    const cos = Math.cos(tilt), sin = Math.sin(tilt);
    paths.forEach((path, i) => {
      const v = i / 39;
      let d = '';
      for (let t = 0; t <= 160; t++) {
        const a = t / 160 * Math.PI * 2;
        const wave = a * 3 + v * 3 + phase;
        const x = ((100 + 46 * Math.cos(wave)) * Math.cos(a) + 34 * Math.sin(v * 6.28)) * breath;
        const y = ((94 + 30 * Math.cos(wave)) * Math.sin(a) * (.5 + v * .5) + 50 * Math.cos(v * 3.14)) * breath;
        d += (t ? 'L' : 'M') + (220 + x * cos - y * sin).toFixed(2) + ',' + (192 + x * sin + y * cos).toFixed(2);
      }
      path.setAttribute('d', d + 'Z');
    });
  }
  let visible = false, frame = null, last = null, elapsed = 0;
  function tick(now) {
    if (last === null) last = now;
    if (now - last >= 1000 / 24) {
      elapsed += Math.min(now - last, 100) / 1000;
      last = now;
      draw(elapsed);
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
    last = null;
    if (motion.matches) { elapsed = 0; draw(0); }
    else if (visible && !document.hidden) frame = requestAnimationFrame(tick);
  }
  draw(0);
  new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    sync();
  }).observe(svg);
  document.addEventListener('visibilitychange', sync);
  motion.addEventListener('change', sync);
})();
