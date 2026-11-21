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
})();
