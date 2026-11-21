(() => {
  'use strict';

  const desktop = document.querySelector('[data-quick-desktop]');
  if (desktop) {
    document.addEventListener('click', (event) => {
      if (desktop.open && !desktop.contains(event.target)) desktop.open = false;
    });
    desktop.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape' || !desktop.open) return;
      desktop.open = false;
      desktop.querySelector('summary').focus();
    });
  }

  const mobile = document.querySelector('[data-quick-mobile]');
  if (!mobile) return;

  const mobileViewport = window.matchMedia('(max-width: 767px)');
  const quote = document.getElementById('yeu-cau-bao-gia');
  let quoteVisible = false;
  const updateMobileBar = () => {
    mobile.hidden = !mobileViewport.matches || window.scrollY < 240 || quoteVisible;
  };

  if (quote) {
    new IntersectionObserver(([entry]) => {
      quoteVisible = entry.isIntersecting;
      updateMobileBar();
    }).observe(quote);
  }

  window.addEventListener('scroll', updateMobileBar, { passive: true });
  window.addEventListener('pageshow', updateMobileBar);
  mobileViewport.addEventListener('change', updateMobileBar);
  updateMobileBar();
})();
