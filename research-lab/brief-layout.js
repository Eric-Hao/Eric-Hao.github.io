(() => {
  document.querySelectorAll('.research-brief').forEach(brief => {
    const card=brief.querySelector('.brief-question');
    const update=()=>brief.style.setProperty('--brief-overlap',`${card.getBoundingClientRect().height / 2}px`);
    new ResizeObserver(update).observe(card);update();
  });
})();
