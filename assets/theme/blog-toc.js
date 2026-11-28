(() => {
  document.querySelectorAll('.sobi-toc-sticky').forEach((sticky) => {
    const toc = sticky.previousElementSibling;
    const articleBody = sticky.closest('.sobi-article-body, .sobi-category-seo-body');
    if (!toc || !articleBody) return;

    const summary = sticky.querySelector('summary');
    let frame = 0;
    const close = () => {
      sticky.open = false;
      summary.focus({ preventScroll: true });
    };
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
    sticky.querySelector('.sobi-toc-close').addEventListener('click', close);
    sticky.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && sticky.open) {
        event.preventDefault();
        close();
      }
    });
    sticky.addEventListener('click', (event) => {
      const link = event.target.closest('a[href^="#"]');
      if (!link) return;
      sticky.open = false;
      const heading = document.getElementById(decodeURIComponent(link.hash.slice(1)));
      if (heading) {
        if (!heading.hasAttribute('tabindex')) heading.setAttribute('tabindex', '-1');
        heading.focus({ preventScroll: true });
      } else {
        summary.focus({ preventScroll: true });
      }
    });
    update();
  });
})();
