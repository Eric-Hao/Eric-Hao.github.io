(async () => {
  const host = document.querySelector('.hero .field');
  if (!host) return;
  const hero = host.closest('.hero');
  const artSpace = hero.querySelector('.hero-art-space');
  const canvas = document.createElement('canvas');
  canvas.className = 'hero-stars';
  host.replaceChildren(canvas);
  const ctx = canvas.getContext('2d');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const hash = n => { const v = Math.sin(n * 127.1 + 311.7) * 43758.5453; return v - Math.floor(v); };
  const smooth = x => { x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };
  // Use the bundled face consistently across devices before sampling its outlines.
  try { await document.fonts.load('500 200px Lora'); } catch (_) { /* Georgia remains readable offline. */ }
  const words = ['reasoning', 'creating', 'understanding'];
  const wordTargets = words.map(word => {
    const mask = document.createElement('canvas');
    mask.width = 1024; mask.height = 300;
    const ink = mask.getContext('2d');
    ink.fillStyle = '#fff'; ink.textBaseline = 'middle';
    // A measured serif silhouette echoes the editorial heading.
    const fontFamily = 'Lora, Georgia, serif';
    ink.font = `500 200px ${fontFamily}`;
    const fontSize = Math.min(230, 200 * 920 / ink.measureText(word).width);
    ink.font = `500 ${fontSize}px ${fontFamily}`;
    ink.textAlign = 'center';
    ink.fillText(word, 512, 145);
    const pixels = ink.getImageData(0, 0, 1024, 300).data, points = [];
    for (let y = 5; y < 295; y += 2) for (let x = 5; x < 1019; x += 2) {
      if (pixels[(y * 1024 + x) * 4 + 3] > 100) points.push({x:x / 1024, y:y / 300});
    }
    return points;
  });
  // Stable particles disperse between words; no abrupt jump between text masks.
  const stars = Array.from({length: Math.max(...wordTargets.map(p => p.length))}, (_, i) => ({
    x: hash(i + 1), y: hash(i + 4100), z: hash(i + 7200),
    delay: hash(i + 11000) * .45, size: .3 + hash(i + 21000) * .55,
    warm: hash(i + 19000) > .93
  }));
  const sprites = ['218,228,235', '235,207,167'].map(rgb => {
    const c = document.createElement('canvas'); c.width = c.height = 48;
    const g = c.getContext('2d'), gradient = g.createRadialGradient(24, 24, 0, 24, 24, 24);
    gradient.addColorStop(0, `rgba(${rgb},.8)`);
    gradient.addColorStop(.12, `rgba(${rgb},.9)`);
    gradient.addColorStop(.35, `rgba(${rgb},.2)`);
    gradient.addColorStop(1, `rgba(${rgb},0)`);
    g.fillStyle = gradient; g.fillRect(0, 0, 48, 48); return c;
  });
  let width = 440, height = 390, frame = null, last = null, time = 3, visible = false;
  let region = { x: 0, y: 0, width: 440, height: 390 };
  const pointer = { x: 0, y: 0, tx: 0, ty: 0 };
  function draw(t) {
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    ctx.fillStyle = '#060e14'; ctx.fillRect(0, 0, width, height);
    const haze = ctx.createRadialGradient(width * .48, height * .53, 0, width * .5, height * .5, width * .65);
    haze.addColorStop(0, '#0b151d'); haze.addColorStop(1, '#060e14');
    ctx.fillStyle = haze; ctx.fillRect(0, 0, width, height);
    ctx.globalCompositeOperation = 'source-over';
    // The surrounding starfield remains present when the research theme has formed.
    for (let i = 0; i < 180; i++) {
      const x = (hash(i + 31000) * width + pointer.x * 5 + width) % width;
      const y = (hash(i + 32000) * height + pointer.y * 5 + height) % height;
      ctx.globalAlpha = .12 + hash(i + 33000) * .35;
      ctx.fillStyle = '#b8c5ce'; ctx.fillRect(x, y, .6 + hash(i + 34000), .6 + hash(i + 34000));
    }
    const phase = t % 9;
    const wordIndex = reduced.matches ? 0 : Math.floor(t / 9) % words.length;
    const targets = wordTargets[wordIndex];
    canvas.dataset.word = words[wordIndex];
    stars.forEach((s, i) => {
      const gather = reduced.matches ? 1 : smooth((phase - s.delay) / 2) * (1 - smooth((phase - 6 - s.delay) / 2));
      const drift = (1 - gather);
      const target = targets[Math.floor(i * targets.length / stars.length)];
      const angle = t * (.025 + s.z * .025) + s.z * Math.PI * 2;
      const sx = s.x + Math.cos(angle) * .04, sy = s.y + Math.sin(angle) * .04;
      const x = sx * width * drift + (region.x + target.x * region.width) * gather + pointer.x * (7 + s.z * 13) * (.35 + drift * .65);
      const y = sy * height * drift + (region.y + target.y * region.height) * gather + pointer.y * (7 + s.z * 13) * (.35 + drift * .65);
      const flicker = .78 + .22 * Math.sin(t * 1.4 + i * 2.1);
      const size = Math.max(.5, Math.min(region.width / 440, 1.4) * s.size) * (1 + .2 * drift);
      ctx.globalAlpha = (.45 + s.z * .5) * flicker;
      ctx.fillStyle = s.warm ? '#e8cfaa' : '#e1e8ed';
      ctx.beginPath(); ctx.arc(x, y, size, 0, Math.PI * 2); ctx.fill();
      if (i % 17 === 0) {
        ctx.globalAlpha = .6 * flicker;
        const glow = size * (s.z > .85 ? 22 : 12);
        ctx.drawImage(sprites[s.warm ? 1 : 0], x - glow / 2, y - glow / 2, glow, glow);
      }
    });
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
    // Keep the copy quiet without separating the visual into a boxed illustration.
    const shade = ctx.createLinearGradient(0, 0, width, 0);
    shade.addColorStop(0, 'rgba(6,14,20,.93)');
    shade.addColorStop(.42, 'rgba(6,14,20,.78)');
    shade.addColorStop(.7, 'rgba(6,14,20,0)');
    shade.addColorStop(1, 'rgba(6,14,20,0)');
    ctx.fillStyle = shade; ctx.fillRect(0, 0, width, height);
    const fade = ctx.createLinearGradient(0, 0, 0, height);
    fade.addColorStop(0, 'rgba(6,14,20,1)');
    fade.addColorStop(.18, 'rgba(6,14,20,0)');
    fade.addColorStop(.72, 'rgba(6,14,20,0)');
    fade.addColorStop(1, 'rgba(6,14,20,1)');
    ctx.fillStyle = fade; ctx.fillRect(0, 0, width, height);
  }
  function tick(now) {
    if (last === null) last = now;
    if (now - last >= 1000 / 30) {
      time += Math.min(now - last, 100) / 1000; last = now;
      pointer.x += (pointer.tx - pointer.x) * .075; pointer.y += (pointer.ty - pointer.y) * .075;
      draw(time);
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null; last = null;
    if (reduced.matches) { pointer.x = pointer.y = pointer.tx = pointer.ty = 0; draw(3); }
    else if (visible && !document.hidden) frame = requestAnimationFrame(tick);
  }
  new ResizeObserver(() => {
    const box = host.getBoundingClientRect(); width = Math.max(1, box.width); height = Math.max(1, box.height);
    const slot = artSpace.getBoundingClientRect();
    const rw = slot.width;
    const rh = Math.min(slot.height, rw * 300 / 1024);
    region = {x: slot.left - box.left + (slot.width - rw) / 2, y: slot.top - box.top + (slot.height - rh) / 2, width: rw, height: rh};
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); draw(reduced.matches ? 3 : time);
  }).observe(host);
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); }).observe(host);
  hero.addEventListener('pointermove', event => {
    if (event.pointerType !== 'mouse' || reduced.matches) return;
    const box = host.getBoundingClientRect();
    pointer.tx = Math.max(-1, Math.min(1, (event.clientX - box.left) / box.width * 2 - 1));
    pointer.ty = Math.max(-1, Math.min(1, (event.clientY - box.top) / box.height * 2 - 1));
  }, { passive: true });
  hero.addEventListener('pointerleave', () => { pointer.tx = pointer.ty = 0; });
  document.addEventListener('visibilitychange', sync); reduced.addEventListener('change', sync);
})();

// Animate once on entry; content stays available without JavaScript or motion.
(() => {
  const rows = document.querySelectorAll('#super-resolution .research-row');
  if (!rows.length || !('IntersectionObserver' in window)) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const animations = new Set();
  const observer = new IntersectionObserver(entries => {
    let index = 0;
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      if (reduced.matches || !entry.target.animate) return;
      const animation = entry.target.animate([
        { opacity: 0, transform: 'translateY(10px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ], { duration: 750, delay: index++ * 100, easing: 'cubic-bezier(.215,.61,.355,1)', fill: 'backwards' });
      animations.add(animation);
      animation.onfinish = animation.oncancel = () => animations.delete(animation);
    });
  }, { threshold: .08 });
  rows.forEach(row => observer.observe(row));
  reduced.addEventListener('change', () => {
    if (reduced.matches) animations.forEach(animation => animation.cancel());
  });
})();
