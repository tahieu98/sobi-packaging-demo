(() => {
    const archive = document.querySelector('.sobi-archive');
    if (!archive) return;

    const sort = archive.querySelector('[data-sobi-sort]');
    sort.addEventListener('change', () => sort.form.requestSubmit());
    archive.classList.add('sobi-archive-sort-enhanced');

    const panel = archive.querySelector('.sobi-archive-filter-panel');
    const opener = archive.querySelector('[data-sobi-filter-open]');
    const dialog = document.createElement('dialog');
    if (!dialog.showModal) return;

    const mobile = matchMedia('(max-width: 1180px)');
    const sidebar = panel.parentElement;
    dialog.className = 'sobi-archive-dialog';
    dialog.setAttribute('aria-labelledby', 'sobi-archive-filter-label');
    archive.append(dialog);
    archive.classList.add('sobi-archive-enhanced');

    opener.addEventListener('click', () => {
        dialog.append(panel);
        dialog.showModal();
        opener.setAttribute('aria-expanded', 'true');
        panel.querySelector('[data-sobi-filter-close]').focus();
    });

    panel.querySelector('[data-sobi-filter-close]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', (event) => {
        if (event.target === dialog) {
            const rect = dialog.getBoundingClientRect();
            if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) {
                dialog.close();
            }
        }
    });
    dialog.addEventListener('close', () => {
        sidebar.append(panel);
        opener.setAttribute('aria-expanded', 'false');
        if (mobile.matches) opener.focus();
    });
    mobile.addEventListener('change', () => {
        if (!mobile.matches && dialog.open) dialog.close();
    });
})();
