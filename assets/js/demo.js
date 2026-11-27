/* Sobi public demo interactions. No requests are sent to a backend. */
(() => {
  'use strict';
  const data = window.SOBI_DATA;
  const root = new URL(document.querySelector('meta[name="sobi-root"]').content, document.baseURI);
  const route = document.querySelector('meta[name="sobi-route"]').content;
  const urlFor = (path = '', params = {}) => {
    const url = new URL(`${path}index.html`, root);
    for (const [key, value] of Object.entries(params)) {
      if (Array.isArray(value)) {
        for (const item of value) url.searchParams.append(key, item);
      } else if (value && (key !== 'trang' || String(value) !== '1')) {
        url.searchParams.set(key, value);
      }
    }
    return url.href;
  };
  const escape = (text) => String(text).replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const normalize = (value) => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi,'d').toLocaleLowerCase('vi').trim();
  const fillTemplate = (html) => html.replaceAll('__SOBI_ROOT__', root.href);
  const currentPage = () => {
    const raw = new URLSearchParams(location.search).get('trang') || '1';
    return /^\d+$/.test(raw) && Number(raw) > 0 ? Number(raw) : 0;
  };
  const updateQuery = (values, replace = false) => {
    const url = new URL(location.href);
    for (const [key,value] of Object.entries(values)) {
      if (value && value !== '1') url.searchParams.set(key,value); else url.searchParams.delete(key);
    }
    history[replace ? 'replaceState' : 'pushState']({},'',url);
  };
  const pagination = (count, page, path, filters, label) => count > 1 ? `<nav class="sobi-pagination" aria-label="${label}">${Array.from({length:count},(_,i)=>`<a href="${urlFor(path,{...filters,trang:String(i+1)})}" ${i+1===page?'aria-current="page"':''}>${i+1}</a>`).join('')}</nav>` : '';
  const empty = (message, path, title = 'Xem tất cả') => `<div class="sobi-demo-empty"><p>${escape(message)}</p><a class="button primary" href="${urlFor(path)}">${title}</a></div>`;
  const catalog = document.querySelector('.sobi-catalog');
  if (route === 'san-pham/' && data.catalogueAliases) {
    const previous = new URL(location.href);
    const group = previous.searchParams.get('nhom');
    if (group && Object.hasOwn(data.catalogueAliases, group)) {
      const destination = new URL(data.catalogueAliases[group], root);
      destination.pathname += 'index.html';
      previous.searchParams.delete('nhom');
      for (const key of new Set(previous.searchParams.keys())) {
        const name = key === 'tim' ? 'tim_mau' : key;
        if (destination.searchParams.has(name)) continue;
        for (const value of previous.searchParams.getAll(key)) destination.searchParams.append(name, value);
      }
      destination.hash = previous.hash;
      location.replace(destination.href);
      return;
    }
  }
  const renderCatalog = () => {
    if (!catalog || route !== 'san-pham/') return;
    const params = new URLSearchParams(location.search);
    const search = (params.get('tim') || '').slice(0,100), group = params.get('nhom') || '', page = currentPage();
    const groups = data.catalogGroups || [];
    const top = groups.find(item => item.slug === group || item.children.some(child => child.slug === group));
    const inGroup = item => !group || (item.productCategories || [item.category]).some(slug => slug === group || (top?.slug === group && top.children.some(child => child.slug === slug)));
    const selected = {};
    const filterForm = catalog.querySelector('.sobi-catalogue-facets form');
    if (filterForm) {
      for (const input of filterForm.querySelectorAll('input[type="checkbox"]')) {
        const key = input.name.replace(/\[\]$/, '');
        input.checked = [...params.getAll(input.name), ...params.getAll(key)].includes(input.value);
        if (input.checked) (selected[input.name] ??= []).push(input.value);
      }
      const selectedCount = Object.values(selected).reduce((sum, values) => sum + values.length, 0);
      filterForm.parentElement.querySelector('summary').textContent = 'Bộ lọc sản phẩm' + (selectedCount ? ` (${selectedCount})` : '');
      if (selectedCount) filterForm.parentElement.open = true;
      filterForm.elements.tim.value = search;
      filterForm.querySelector('.sobi-catalogue-facet-actions a').href = urlFor('san-pham/', {tim: search});
    }
    const matchedFacets = item => Object.entries(selected).every(([key, values]) =>
      values.some(value => item.options?.includes(`${key.replace(/\[\]$/, '')}=${value}`)));
    const results = data.products.filter(item => inGroup(item) && matchedFacets(item) && normalize(`${item.title} ${item.code}`).includes(normalize(search)));
    const pageCount = Math.ceil(results.length / 8);
    const valid = page > 0 && (page === 1 || page <= pageCount);
    catalog.querySelector('.sobi-result-count').textContent = `${results.length} mẫu sản phẩm${search ? ` cho “${search}”` : ''}`;
    catalog.querySelector('.sobi-result-count').setAttribute('role','status');
    catalog.querySelector('.sobi-product-grid').innerHTML = valid && results.length ? results.slice((page-1)*8,page*8).map(item=>fillTemplate(item.html)).join('') : empty(valid ? 'Chưa có mẫu phù hợp. Thử tên, mã mẫu hoặc nhóm khác.' : 'Trang sản phẩm này không tồn tại.', 'san-pham/');
    catalog.querySelectorAll('.sobi-pagination').forEach(el=>el.remove());
    catalog.insertAdjacentHTML('beforeend',pagination(pageCount,page,'san-pham/',{tim:search,nhom:group,...selected},'Trang sản phẩm'));
    // Order 38: level-1 groups mirror the header "Danh mục"; a selected group adds its level-2 bar.
    const filterLink = (level, id, slug, label, active, current = active) => `<a id="sobi-filter-${level}-${escape(id)}" class="sobi-filter-tab${active ? ' is-active' : ''}"${current ? ' aria-current="page"' : ''} href="${escape(urlFor('san-pham/',{nhom:slug,tim:search}))}">${escape(label)}</a>`;
    const stack = catalog.querySelector('.sobi-filter-stack');
    if (stack && groups.length) {
      stack.innerHTML = `<nav class="sobi-filter" aria-label="Nhóm sản phẩm">${filterLink('top','all','','Tất cả',!group)}${groups.map(item=>filterLink('top',item.slug,item.slug,item.label,top===item,group===item.slug)).join('')}</nav>`
        + (top && top.children.length ? `<nav class="sobi-filter sobi-filter--sub" aria-label="Danh mục thứ cấp">${filterLink('sub','all',top.slug,'Tất cả',group===top.slug)}${top.children.map(child=>filterLink('sub',child.slug,child.slug,child.label,group===child.slug)).join('')}</nav>` : '');
    }
    if (stack && data.catalogueAliases) {
      for (const link of stack.querySelectorAll('.sobi-filter-tab[href]')) {
        const target = new URL(link.href);
        const parameter = target.pathname === new URL('san-pham/index.html', root).pathname ? 'tim' : 'tim_mau';
        if (search) target.searchParams.set(parameter, search);
        else target.searchParams.delete(parameter);
        link.href = target.href;
      }
    }
    catalog.querySelector('input[name="tim"]').value = search;
  };
  const blogList = document.querySelector('.sobi-blog-list');
  const blogCategory = data.categories.find(item => item.route === route);
  const renderBlog = () => {
    if (!blogList) return;
    const params = new URLSearchParams(location.search), search = (params.get('tu-khoa') || '').slice(0,100), page = currentPage();
    const results = data.posts.filter(item=>(!blogCategory || item.category===blogCategory.slug) && normalize(`${item.title} ${item.search}`).includes(normalize(search)));
    const pages = Math.ceil(results.length/6), valid = page > 0 && (page===1 || page<=pages);
    const topicLinks = [{name:'Tất cả bài viết',route:'blog/'},...data.categories];
    blogList.innerHTML = `<div class="sobi-blog-toolbar"><nav class="sobi-blog-topics" aria-label="Chuyên mục Blog">${topicLinks.map(item=>`<a href="${urlFor(item.route,{'tu-khoa':search})}" ${item.route===route?'aria-current="page"':''}>${escape(item.name)}</a>`).join('')}</nav><form class="sobi-blog-search" role="search"><label class="screen-reader-text" for="sobi-blog-search">Tìm bài viết Blog</label><input id="sobi-blog-search" name="tu-khoa" type="search" placeholder="Tìm bài viết..." value="${escape(search)}"><button type="submit" aria-label="Tìm bài viết">Tìm</button></form></div><p class="sobi-result-count" role="status">${results.length} bài viết${search?` cho “${escape(search)}”`:''}</p>${valid && results.length?`<div class="sobi-blog-grid">${results.slice((page-1)*6,page*6).map(item=>fillTemplate(item.html)).join('')}</div>`:empty(valid?'Chưa tìm thấy bài viết phù hợp. Thử một từ khóa khác.':'Trang bài viết này không tồn tại.',route)}${pagination(pages,page,route,{'tu-khoa':search},'Trang bài viết')}`;
  };
  const renderSiteSearch = () => {
    const container = document.querySelector('#demo-site-results');
    if (!container) return;
    const search = (new URLSearchParams(location.search).get('s') || '').slice(0,100);
    document.querySelector('#demo-site-search').value = search;
    if (!search) {container.innerHTML='<p>Nhập từ khóa để tìm trang, mẫu túi hoặc bài viết.</p>';return;}
    const results = data.search.filter(item=>normalize(`${item.title} ${item.text}`).includes(normalize(search)));
    container.innerHTML = `<p role="status">${results.length} kết quả cho “${escape(search)}”</p>`+results.map(item=>`<article class="sobi-demo-search-card"><h2><a href="${urlFor(item.route)}">${escape(item.title)}</a></h2><p>${escape(item.text.replace(/\s+/g,' ').slice(0,180))}…</p></article>`).join('');
    if (!results.length) container.insertAdjacentHTML('beforeend',empty('Chưa có nội dung phù hợp.','search/','Tìm từ khóa khác'));
  };
  const render = () => {renderCatalog();renderBlog();renderSiteSearch();};
  render(); window.addEventListener('popstate',render);
  document.addEventListener('submit',event=>{
    const form=event.target;
    if (form.matches('.sobi-catalog-search') && route==='san-pham/') {event.preventDefault();updateQuery({tim:form.elements.tim.value.trim(),trang:''});renderCatalog();}
    if (form.matches('.sobi-blog-search')) {event.preventDefault();updateQuery({'tu-khoa':form.elements['tu-khoa'].value.trim(),trang:''});renderBlog();blogList.querySelector('input').focus();}
    if (form.matches('.sobi-demo-search')) {event.preventDefault();updateQuery({s:form.elements.s.value.trim()});renderSiteSearch();}
  });
  let searchTimer;
  catalog?.querySelector('input[name="tim"]')?.addEventListener('input',event=>{
    clearTimeout(searchTimer);const value=event.target.value;
    searchTimer=setTimeout(()=>{updateQuery({tim:value,trang:''},true);renderCatalog();},160);
  });
  document.querySelectorAll('.accordion-title').forEach(button=>button.addEventListener('click',()=>{
    const expanded=button.getAttribute('aria-expanded')==='true';
    button.setAttribute('aria-expanded',String(!expanded));
    button.classList.toggle('active',!expanded);
    button.closest('.accordion-item').classList.toggle('active',!expanded);
    document.getElementById(button.getAttribute('aria-controls')).hidden=expanded;
  }));
  document.querySelectorAll('.sobi-quote-form').forEach(form=>{
    const params=new URLSearchParams(location.search);
    const product = params.get('sobi_mau') || params.get('product');
    if (!params.get('ung-dung') && product) form.elements.message.value=`Tôi quan tâm mẫu ${product.slice(0,200)}`;
    form.addEventListener('submit',event=>{
      event.preventDefault();
      const status=form.parentElement.querySelector('.sobi-message');
      if (!form.reportValidity()) return;
      const values=new FormData(form), customer=String(values.get('customer')||'').trim(), phone=String(values.get('phone')||'').trim();
      if (customer.length<2 || !/^[+0-9 ()-]{9,20}$/.test(phone)) {
        status.hidden=false;status.className='sobi-message is-error';status.textContent='Vui lòng kiểm tra họ tên và số điện thoại.';status.focus();return;
      }
      const button=form.querySelector('[type="submit"]');const label=button.innerHTML;
      button.disabled=true;button.textContent='Đang mô phỏng...';form.setAttribute('aria-busy','true');
      setTimeout(()=>{
        const fields=[['Loại bao bì',values.get('category')],['Kích thước',`${values.get('length')} × ${values.get('width')} × ${values.get('height')} cm`],['Số lượng',`${Number(values.get('quantity')).toLocaleString('vi-VN')} cái`],['Liên hệ',`${customer} · ${phone}`],['Tỉnh/Thành',values.get('province')],['File đã chọn',[...form.querySelector('[type=file]').files].map(f=>f.name).join(', ')||'Không có']];
        form.parentElement.querySelector('.sobi-demo-result')?.remove();
        const result=document.createElement('section');result.className='sobi-demo-result';result.setAttribute('tabindex','-1');
        result.innerHTML=`<h3>Đã hoàn tất thao tác thử</h3><p>Đây là bản xem trước yêu cầu của bạn. Thông tin và file <strong>chưa được gửi đến Sobi</strong>.</p><dl>${fields.map(([key,value])=>`<dt>${escape(key)}</dt><dd>${escape(value)}</dd>`).join('')}</dl><button type="button" class="button primary" data-demo-retry>Thử yêu cầu khác</button>`;
        form.insertAdjacentElement('afterend',result);
        result.querySelector('[data-demo-retry]').addEventListener('click',()=>{form.reset();form.querySelector('.sobi-file-list').replaceChildren();form.querySelector('[type=file]').setCustomValidity('');form.dispatchEvent(new Event('input',{bubbles:true}));result.remove();status.hidden=true;form.elements.customer.focus();});
        status.hidden=false;status.className='sobi-message is-success';status.textContent='Mô phỏng thành công. Xem thông tin yêu cầu bên dưới.';
        button.disabled=false;button.innerHTML=label;form.removeAttribute('aria-busy');result.focus();
      },450);
    });
  });
  document.querySelectorAll('form[data-demo-form=comment]').forEach(form=>{
    form.addEventListener('submit',event=>{
      event.preventDefault();if(!form.reportValidity())return;
      const fields=new FormData(form), text=String(fields.get('comment')||'').trim(), author=String(fields.get('author')||'').trim();
      if(!text||!author)return;
      const entry=document.createElement('article');entry.className='sobi-demo-local-comment';
      const name=document.createElement('strong');name.textContent=author;
      const content=document.createElement('p');content.textContent=text;
      const badge=document.createElement('small');badge.textContent='Bình luận thử · chỉ trong phiên xem này';
      entry.append(name,document.createElement('br'),badge,content);
      form.parentElement.insertBefore(entry,form);form.reset();entry.scrollIntoView({block:'nearest',behavior:'smooth'});
    });
  });
  document.querySelectorAll('[data-demo-share=facebook]').forEach(anchor=>{
    const share=new URL('https://www.facebook.com/sharer/sharer.php');share.searchParams.set('u',location.href.split('?')[0]);anchor.href=share.href;
  });
  // Progressive enhancement: the HTML page links also work without a build tool.
})();
