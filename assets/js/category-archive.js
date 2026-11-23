(() => {
  'use strict';
  const archive = document.querySelector('.sobi-archive');
  if (!archive) return;

  const form = archive.querySelector('#sobi-archive-filter');
  const results = archive.querySelector('#sobi-archive-results');
  const grid = results.querySelector('.sobi-product-grid');
  const count = results.querySelector('.sobi-archive-count');
  const searchInput = form.elements.tim_mau;
  const params = new URLSearchParams(location.search);
  const normalize = value => value.normalize('NFD').replace(/\p{M}/gu, '').replace(/đ/gi, 'd').toLocaleLowerCase('vi').trim();
  const search = (params.get('tim_mau') || '').slice(0, 100);
  searchInput.value = search;
  const selected = new Map();
  for (const checkbox of form.querySelectorAll('input[type="checkbox"]')) {
    checkbox.checked = params.getAll(checkbox.name).includes(checkbox.value);
    if (checkbox.checked) {
      const group = selected.get(checkbox.name) ?? [];
      group.push(checkbox.value);
      selected.set(checkbox.name, group);
    }
  }

  const sort = archive.querySelector('[data-sobi-sort]');
  const requestedSort = params.get('sort');
  if ([...sort.options].some(option => option.value === requestedSort)) sort.value = requestedSort;
  const listView = params.get('hien_thi') === 'danh-sach';
  const cleanUrl = new URL(form.action, document.baseURI);
  const baseUrl = new URL(cleanUrl);
  for (const [key, values] of selected) {
    for (const value of values) baseUrl.searchParams.append(key, value);
  }
  if (search) baseUrl.searchParams.set('tim_mau', search);
  if (sort.value !== 'newest') {
    cleanUrl.searchParams.set('sort', sort.value);
    baseUrl.searchParams.set('sort', sort.value);
  }
  if (listView) {
    cleanUrl.searchParams.set('hien_thi', 'danh-sach');
    baseUrl.searchParams.set('hien_thi', 'danh-sach');
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'hien_thi';
    input.value = 'danh-sach';
    form.append(input);
  }

  const cards = [...(grid?.querySelectorAll('.sobi-product-card') ?? [])];
  const matching = cards.filter(card => {
    const name = card.querySelector('h2').textContent;
    const code = card.querySelector('.sobi-product-code')?.textContent ?? '';
    const options = new Set(card.dataset.archiveOptions.split(' '));
    return normalize(name + ' ' + code).includes(normalize(search))
      && [...selected.values()].every(group => group.some(value => options.has(value)));
  });
  if (sort.value === 'alpha') {
    const collator = new Intl.Collator('vi');
    matching.sort((a, b) => collator.compare(a.querySelector('h2').textContent, b.querySelector('h2').textContent));
  } else if (sort.value === 'popular') {
    matching.sort((a, b) => Number(a.dataset.archiveOrder) - Number(b.dataset.archiveOrder));
  }

  const perPage = 20;
  const total = Math.max(1, Math.ceil(matching.length / perPage));
  const requestedPage = params.get('trang') || '1';
  const page = /^\d+$/.test(requestedPage) ? Math.min(total, Math.max(1, Number(requestedPage))) : 1;
  const visible = matching.slice((page - 1) * perPage, page * perPage);
  const number = new Intl.NumberFormat('vi-VN');
  const figures = count.querySelectorAll('strong');
  figures[0].textContent = number.format(visible.length);
  figures[1].textContent = number.format(matching.length);

  const viewLinks = archive.querySelectorAll('.sobi-archive-views a');
  for (const [index, link] of viewLinks.entries()) {
    const url = new URL(baseUrl);
    if (page > 1) url.searchParams.set('trang', String(page));
    if (index === 0) url.searchParams.delete('hien_thi');
    else url.searchParams.set('hien_thi', 'danh-sach');
    link.href = url.href;
    if ((index === 1) === listView) link.setAttribute('aria-current', 'true');
    else link.removeAttribute('aria-current');
  }
  archive.querySelector('.sobi-archive-filter-actions a').href = cleanUrl.href;

  if (grid) {
    grid.classList.toggle('sobi-archive-list', listView);
    grid.replaceChildren(...visible);
  }
  if (!visible.length && (search || selected.size)) {
    const empty = results.querySelector('.sobi-archive-empty') ?? document.createElement('div');
    empty.className = 'sobi-archive-empty';
    const title = document.createElement('h2');
    title.textContent = 'Chưa có mẫu phù hợp';
    const reset = document.createElement('a');
    reset.href = cleanUrl.href;
    reset.textContent = 'Xóa bộ lọc để xem lại tất cả mẫu';
    empty.replaceChildren(title, reset);
    results.append(empty);
  }
  if (total > 1) {
    const nav = document.createElement('nav');
    nav.className = 'sobi-pagination';
    nav.setAttribute('aria-label', 'Trang kết quả');
    for (let index = 1; index <= total; index++) {
      const url = new URL(baseUrl);
      if (index > 1) url.searchParams.set('trang', String(index));
      const link = document.createElement('a');
      link.href = url.href;
      link.textContent = String(index);
      if (index === page) link.setAttribute('aria-current', 'page');
      nav.append(link);
    }
    results.append(nav);
  }
})();
