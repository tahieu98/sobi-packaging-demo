(() => {
  'use strict';
  const archive = document.querySelector('.sobi-archive');
  if (!archive) return;

  const form = archive.querySelector('#sobi-archive-filter');
  const results = archive.querySelector('#sobi-archive-results');
  const count = results.querySelector('.sobi-archive-count');
  let grid = results.querySelector('.sobi-product-grid');
  const data = window.SOBI_DATA;
  const route = document.querySelector('meta[name="sobi-route"]').content;
  const slug = route.split('/').filter(Boolean).pop();
  const group = data.catalogGroups?.find(item => item.slug === slug);
  const fixtures = group ? data.products.filter(item => item.qaOptions && item.productCategories.some(category => category === slug || group.children.some(child => child.slug === category))) : [];
  if (fixtures.length) {
    results.querySelector('.sobi-archive-empty')?.remove();
    if (!grid) {
      grid = document.createElement('div');
      grid.className = 'sobi-product-grid';
      results.append(grid);
    }
    const root = new URL(document.querySelector('meta[name="sobi-root"]').content, document.baseURI);
    const template = document.createElement('template');
    const labels = { mau_sac: 'Màu sắc', chat_lieu: 'Chất liệu', quai: 'Kiểu quai', nganh: 'Ngành hàng' };
    for (const item of fixtures) {
      template.innerHTML = item.html.replaceAll('__SOBI_ROOT__', root.href);
      const card = template.content.firstElementChild;
      const options = Object.fromEntries(Object.entries(item.qaOptions));
      const children = group.children.filter(child => item.productCategories.includes(child.slug) && child.id);
      if (children.length) {
        options.nganh = Object.fromEntries(children.map(child => [String(child.id), child.label]));
        card.dataset.archiveOptions += ' ' + children.map(child => child.id).join(' ');
      }
      grid.prepend(card);
      for (const [key, values] of Object.entries(options)) {
        if (!labels[key]) continue;
        const name = `${key}[]`;
        let field = [...form.querySelectorAll('fieldset')].find(el => [...el.querySelectorAll('input')].some(input => input.name === name));
        if (!field) {
          field = document.createElement('fieldset');
          field.className = 'sobi-archive-filter-box';
          const legend = document.createElement('legend');
          legend.textContent = labels[key];
          const choices = document.createElement('div');
          choices.className = 'sobi-archive-options';
          field.append(legend, choices);
          form.querySelector('.sobi-archive-filter-actions').before(field);
        }
        for (const [value, label] of Object.entries(values)) {
          if ([...field.querySelectorAll('input')].some(input => input.value === value)) continue;
          const option = document.createElement('label');
          const input = document.createElement('input');
          input.type = 'checkbox'; input.name = name; input.value = value;
          const text = document.createElement('span'); text.textContent = label;
          option.append(input, text);
          field.querySelector('.sobi-archive-options').append(option);
        }
      }
    }
  }
  const searchInput = form.elements.tim_mau;
  const params = new URLSearchParams(location.search);
  const normalize = value => value.normalize('NFD').replace(/\p{M}/gu, '').replace(/đ/gi, 'd').toLocaleLowerCase('vi').trim();
  const search = (params.get('tim_mau') || '').slice(0, 100);
  searchInput.value = search;
  const selected = new Map();
  for (const checkbox of form.querySelectorAll('input[type="checkbox"]')) {
    const key = checkbox.name.replace(/\[\]$/, '');
    checkbox.checked = [...params.getAll(checkbox.name), ...params.getAll(key)].includes(checkbox.value);
    if (checkbox.checked) {
      const group = selected.get(checkbox.name) ?? [];
      group.push(data.catalogueAliases ? `${key}=${checkbox.value}` : checkbox.value);
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
    for (const value of values) baseUrl.searchParams.append(key, data.catalogueAliases ? value.slice(value.indexOf('=') + 1) : value);
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
