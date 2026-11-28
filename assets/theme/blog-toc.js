(() => {
  const sticky = document.querySelector('.sobi-toc-sticky');
  if (!sticky) return;

  const toc = sticky.previousElementSibling;
  const articleBody = sticky.closest('.sobi-article-body');
  const summary = sticky.querySelector('summary');
  let frame = 0;

  const update = () => {
    frame = 0;
    const visible = toc.getBoundingClientRect().bottom <= 0
      && articleBody.getBoundingClientRect().bottom > window.innerHeight * 0.35;
    sticky.hidden = !visible;
    if (!visible) sticky.open = false;
  };
  const schedule = () => {
    if (!frame) frame = requestAnimationFrame(update);
  };
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  window.addEventListener('load', schedule, { once: true });
  sticky.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && sticky.open) {
      sticky.open = false;
      summary.focus();
    }
  });
  sticky.addEventListener('click', (event) => {
    if (event.target.closest('a[href^="#"]')) {
      sticky.open = false;
      summary.focus({ preventScroll: true });
    }
  });
  update();
})();
