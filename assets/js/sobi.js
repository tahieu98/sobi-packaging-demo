(() => {
  "use strict";
  document.querySelectorAll('#main .sobi-page-title h1').forEach((heading) => {
    if (heading.children.length) return;

    const title = heading.textContent;
    const breaks = [...title.matchAll(/[^.\s]\.(\s+)(?=[^\s.])/gu)];
    if (!breaks.length) return;

    const content = document.createDocumentFragment();
    let start = 0;
    const appendSentence = (end) => {
      const sentence = document.createElement('span');
      sentence.className = 'sobi-title-sentence';
      sentence.textContent = title.slice(start, end);
      content.append(sentence);
    };

    for (const match of breaks) {
      const space = match[1];
      const end = match.index + match[0].length - space.length;
      appendSentence(end);
      content.append(space);
      start = end + space.length;
    }
    appendSentence(title.length);
    heading.replaceChildren(content);
  });

  function revealCatalogueSelection() {
    document.querySelectorAll('.sobi-filter-stack > .sobi-filter, nav.sobi-archive-subcats').forEach((rail) => {
      const active = rail.querySelector('.is-active, .sobi-archive-category-card[aria-current]');
      if (!active || rail.scrollWidth <= rail.clientWidth) return;
      const bounds = rail.getBoundingClientRect();
      const item = active.getBoundingClientRect();
      if (item.left >= bounds.left + 2 && item.right <= bounds.right - 2) return;
      rail.scrollLeft += item.left - bounds.left - (bounds.width - item.width) / 2;
    });
  }
  // DOMContentLoaded also covers the tabs rebuilt by the static demo.
  document.addEventListener('DOMContentLoaded', revealCatalogueSelection);
  window.addEventListener('pageshow', revealCatalogueSelection);
  document.fonts?.ready.then(revealCatalogueSelection);
  const inBuilder = new URLSearchParams(location.search).has('uxb_iframe');
  if (inBuilder) document.body.classList.add('sobi-builder-preview');
  const showVideoStatus = (container, message) => {
    const status = container.parentElement?.querySelector('.sobi-video-status');
    if (status) { status.textContent = message; status.hidden = !message; }
  };
  const getAllowedVideoUrl = (raw, provider) => {
    if (typeof raw !== 'string' || !raw) return null;
    // The static export rewrites local MP4 URLs relative to each HTML page.
    const demoPath = provider === 'mp4' && document.body.classList.contains('sobi-static-demo')
      ? raw.match(/^(?:\.\/|(?:\.\.\/)+)assets\/media\//)
      : null;
    let url;
    try { url = new URL(raw, demoPath ? location.href : undefined); }
    catch { return null; }
    if (demoPath && !url.href.startsWith(new URL(demoPath[0], location.href).href)) return null;
    if (demoPath && location.protocol === 'file:' && url.protocol === 'file:') {
      return /\.mp4$/i.test(url.pathname) ? url : null;
    }
    if (url.username || url.password || !['http:', 'https:'].includes(url.protocol)) return null;
    if (provider === 'facebook') {
      if (url.protocol !== 'https:' || url.port || url.hostname !== 'www.facebook.com' || url.pathname !== '/plugins/video.php') return null;
      let reel;
      try { reel = new URL(url.searchParams.get('href')); }
      catch { return null; }
      if (reel.protocol !== 'https:' || reel.port || reel.username || reel.password || reel.hostname !== 'www.facebook.com' || !/^\/reel\/[0-9]{5,30}\/$/.test(reel.pathname)) return null;
      const embed = new URL('https://www.facebook.com/plugins/video.php');
      embed.searchParams.set('href', reel.origin + reel.pathname);
      embed.searchParams.set('show_text', 'false');
      return embed;
    }
    if (provider === 'youtube') {
      return url.protocol === 'https:' && !url.port && url.hostname === 'www.youtube-nocookie.com' && /^\/embed\/[A-Za-z0-9_-]{11}$/.test(url.pathname)
        ? new URL(url.origin + url.pathname + '?autoplay=1&rel=0') : null;
    }
    if (provider === 'mp4') {
      const localHttp = url.protocol === 'http:'
        && url.origin === location.origin
        && (location.hostname.endsWith('.test') || ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname));
      return (url.protocol === 'https:' || localHttp) && /\.mp4$/i.test(url.pathname) ? url : null;
    }
    return null;
  };
  const activateVideo = (container, automatic = false) => {
    if (!container || !container.querySelector('.sobi-video-play')) return;
    const poster = container.querySelector('img')?.currentSrc;
    const provider = container.dataset.videoProvider;
    const source = getAllowedVideoUrl(container.dataset.videoSrc, provider);
    if (!source) {
      showVideoStatus(container, 'Liên kết video không hợp lệ.');
      return;
    }
    if (provider === 'mp4') {
      const video = document.createElement('video');
      video.controls = true;
      video.playsInline = true;
      video.setAttribute('playsinline', '');
      video.preload = 'none';
      video.muted = automatic;
      video.defaultMuted = automatic;
      video.setAttribute('aria-label', container.dataset.videoTitle);
      if (poster) video.poster = poster;
      video.addEventListener('playing', () => {
        container.dataset.videoState = 'playing';
        showVideoStatus(container, '');
      });
      video.addEventListener('error', () => {
        container.dataset.videoState = 'error';
        const fallback = container.parentElement?.querySelector('figcaption a');
        showVideoStatus(container, fallback ? 'Không thể tải video. Bạn có thể mở video bằng liên kết bên dưới.' : 'Không thể tải video.');
      });
      container.replaceChildren(video);
      video.src = source.href;
      const started = video.play();
      started?.catch(() => {
        if (container.dataset.videoState === 'error') return;
        container.dataset.videoState = 'paused';
        showVideoStatus(container, 'Chạm nút phát trên video để xem.');
      });
      if (!automatic) video.focus({ preventScroll: true });
    } else {
      const iframe = document.createElement('iframe');
      const url = source;
      if (url.hostname === 'www.facebook.com') {
        url.searchParams.set('width', Math.max(220, Math.round(container.getBoundingClientRect().width)));
        url.searchParams.set('height', Math.round(container.getBoundingClientRect().height));
      }
      iframe.src = url.href;
      iframe.title = container.dataset.videoTitle;
      iframe.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      iframe.allowFullscreen = true;
      iframe.referrerPolicy = 'strict-origin-when-cross-origin';
      iframe.tabIndex = 0;
      container.replaceChildren(iframe);
      iframe.focus({ preventScroll: true });
    }
  };
  // Delegation also supports elements re-rendered while editing in UX Builder.
  document.addEventListener('click', (event) => {
    const button = event.target.closest('.sobi-video-play');
    if (!button || inBuilder) return;
    activateVideo(button.closest('[data-sobi-video]'));
  });
  const scheduleVideos = () => {
    if (inBuilder || matchMedia('(prefers-reduced-motion: reduce)').matches || navigator.connection?.saveData) return;
    if (!('IntersectionObserver' in window)) return; // Keep click-to-play available.
    const ready = new Set();
    const visible = new Set();
    const maybePlay = (container) => {
      if (document.visibilityState !== 'visible' || !ready.has(container) || !visible.has(container)) return;
      observer.unobserve(container);
      ready.delete(container);
      visible.delete(container);
      activateVideo(container, true);
    };
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(({target, isIntersecting}) => {
        if (isIntersecting) { visible.add(target); maybePlay(target); }
        else visible.delete(target);
      });
    });
    document.querySelectorAll('[data-sobi-video][data-video-autoplay="true"]').forEach((container) => {
      observer.observe(container);
      const delay = Math.max(2000, Math.min(10000, Number(container.dataset.videoDelay) || 2500));
      setTimeout(() => { ready.add(container); maybePlay(container); }, delay);
    });
    document.addEventListener('visibilitychange', () => ready.forEach(maybePlay));
  };
  if (document.readyState === 'complete') scheduleVideos();
  else window.addEventListener('load', scheduleVideos, { once: true });
  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy-url]");
    if (!button) return;
    const status = button.parentElement.querySelector(".sobi-copy-status");
    try { await navigator.clipboard.writeText(location.href.split("?")[0]); status.textContent = "Đã sao chép liên kết."; }
    catch { status.textContent = "Bạn có thể sao chép địa chỉ trên thanh trình duyệt."; }
  });
  if (typeof navigator.share === 'function') {
    document.querySelectorAll('[data-sobi-native-share]').forEach((button) => {
      const group = button.closest('.sobi-article-share');
      const status = group.querySelector('.sobi-copy-status');
      button.hidden = false;
      button.addEventListener('click', async () => {
        try {
          await navigator.share({ title: document.title, url: new URL(button.dataset.sobiNativeShare, location.href).href });
        } catch (error) {
          if (error.name !== 'AbortError' && status) {
            status.textContent = 'Dùng nút sao chép để chia sẻ liên kết.';
          }
        }
      });
    });
  }
  // Touch feedback must start on contact and clear when the gesture becomes a scroll.
  let pressedCard = null;
  const clearCardPress = () => {
    pressedCard?.element.classList.remove("is-pressed");
    pressedCard = null;
  };
  document.addEventListener(
    "pointerdown",
    (event) => {
      if (event.pointerType === "mouse" || !event.isPrimary) return;
      clearCardPress();
      const element = event.target.closest(
        ".sobi-product-card, .sobi-archive-subcats[aria-label=\"Danh mục con\"] .sobi-archive-category-card, " +
        ".sobi-archive-related .sobi-archive-category-card, " +
        ".sobi-hero-quote, .sobi-hero-custom, .sobi-mega .sobi-text-link, .sobi-subcategory-jump nav a",
      );
      if (!element) return;
      pressedCard = {
        element,
        id: event.pointerId,
        x: event.clientX,
        y: event.clientY,
      };
      element.classList.add("is-pressed");
    },
    { passive: true },
  );
  document.addEventListener(
    "pointermove",
    (event) => {
      if (!pressedCard || event.pointerId !== pressedCard.id) return;
      if (
        Math.hypot(event.clientX - pressedCard.x, event.clientY - pressedCard.y) > 10
      ) clearCardPress();
    },
    { passive: true },
  );
  for (const type of ["pointerup", "pointercancel"]) {
    document.addEventListener(
      type,
      (event) => {
        if (event.pointerId === pressedCard?.id) clearCardPress();
      },
      { passive: true },
    );
  }
  window.addEventListener("scroll", clearCardPress, { passive: true });
  window.addEventListener("blur", clearCardPress);
  window.addEventListener("pagehide", clearCardPress);
  window.addEventListener("pageshow", clearCardPress);
  const megaMenu = document.getElementById('sobi-mega');
  const updateMegaSpace = () => {
    if (!megaMenu || megaMenu.hidden) return;
    const viewportBottom = window.visualViewport
      ? window.visualViewport.offsetTop + window.visualViewport.height
      : window.innerHeight;
    const available = Math.max(0, viewportBottom - megaMenu.getBoundingClientRect().top - 16);
    megaMenu.style.setProperty('--sobi-mega-available', `${available}px`);
  };
  let megaResizeFrame;
  const scheduleMegaSpace = () => {
    cancelAnimationFrame(megaResizeFrame);
    megaResizeFrame = requestAnimationFrame(updateMegaSpace);
  };
  window.addEventListener('resize', scheduleMegaSpace, { passive: true });
  window.addEventListener('scroll', scheduleMegaSpace, { passive: true });
  window.visualViewport?.addEventListener('resize', scheduleMegaSpace, { passive: true });
  const controls = [
    ["[data-menu-toggle]", "#sobi-mobile-menu"],
    ["[data-category-toggle]", "#sobi-mega"],
    ["[data-search-toggle]", "#sobi-header-search"],
  ].map(([button, panel]) => [
    document.querySelector(button),
    document.querySelector(panel),
  ]);
  const setLabel = (button, open) => {
    if (button.hasAttribute("data-category-toggle")) {
      if (open) {
        button.setAttribute("aria-label", "Đóng danh mục");
        button.setAttribute("title", "Đóng danh mục");
      } else {
        button.removeAttribute("aria-label");
        button.removeAttribute("title");
      }
      return;
    }
    const text = button.hasAttribute("data-menu-toggle")
      ? open
        ? "Đóng menu"
        : "Mở menu"
      : open
        ? "Đóng tìm kiếm"
        : "Tìm sản phẩm";
    button.setAttribute("aria-label", text);
    button.setAttribute("title", text);
  };
  const close = () =>
    controls.forEach(([button, panel]) => {
      if (!button || !panel) return;
      button.setAttribute("aria-expanded", "false");
      panel.hidden = true;
      setLabel(button, false);
    });
  controls.forEach(([button, panel]) => {
    if (!button || !panel) return;
    button.addEventListener("click", () => {
      const open = panel.hidden;
      close();
      panel.hidden = !open;
      button.setAttribute("aria-expanded", String(open));
      setLabel(button, open);
      if (open) {
        updateMegaSpace();
        const target = panel.querySelector('[data-mega-tab][aria-selected="true"]')
          || panel.querySelector('input, button, a');
        target?.focus({ preventScroll: true });
      }
    });
  });
  document.addEventListener("click", (event) => {
    if (
      !controls.some(
        ([button, panel]) =>
          button?.contains(event.target) || panel?.contains(event.target),
      )
    )
      close();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const active = controls.find(
      ([button]) => button?.getAttribute("aria-expanded") === "true",
    );
    close();
    active?.[0].focus();
  });
  const gallery = document.querySelector(".sobi-gallery");
  let galleryOpener = null;
  document.querySelectorAll("[data-gallery-open]").forEach((button) => {
    button.addEventListener("click", () => {
      galleryOpener = button;
      gallery?.querySelectorAll("[data-gallery-image]").forEach((image) => {
        image.hidden = image.dataset.galleryImage !== button.dataset.galleryOpen;
      });
      gallery?.showModal();
    });
  });
  document
    .querySelector("[data-gallery-close]")
    ?.addEventListener("click", () => gallery?.close());
  gallery?.addEventListener("click", (event) => {
    if (event.target === gallery) gallery.close();
  });
  gallery?.addEventListener("close", () => galleryOpener?.focus());
  const backTop = document.querySelector("[data-back-top]");
  window.addEventListener(
    "scroll",
    () => {
      if (backTop) backTop.hidden = window.scrollY < 600;
    },
    { passive: true },
  );
  backTop?.addEventListener("click", () =>
    window.scrollTo({
      top: 0,
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "auto"
        : "smooth",
    }),
  );
  const categoryJumpLinks = [...document.querySelectorAll('.sobi-subcategory-jump nav a[href^="#"]')];
  if (categoryJumpLinks.length) {
    const updateCategoryJumpSelection = () => {
      for (const link of categoryJumpLinks) {
        if (link.hash && link.hash === location.hash) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }
    };
    updateCategoryJumpSelection();
    window.addEventListener('hashchange', updateCategoryJumpSelection);
  }
  const megaTabs = [...document.querySelectorAll('[data-mega-tab]')];
  const selectMegaTab = (tab, focus = false) => {
    megaTabs.forEach((item) => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
    });
    const content = megaMenu?.querySelector('.sobi-mega-content');
    if (content) content.scrollTop = 0;
    if (focus) tab.focus({ preventScroll: true });
    // Reveal keyboard-selected categories within their own scroll region.
    const choices = tab.closest('.sobi-mega-choices');
    if (choices) {
      const itemRect = tab.getBoundingClientRect();
      const listRect = choices.getBoundingClientRect();
      if (itemRect.top < listRect.top) choices.scrollTop -= listRect.top - itemRect.top + 4;
      else if (itemRect.bottom > listRect.bottom) choices.scrollTop += itemRect.bottom - listRect.bottom + 4;
    }
  };
  if (megaTabs.length) {
    megaMenu.classList.add('is-enhanced');
    const content = megaMenu.querySelector('.sobi-mega-content');
    content.tabIndex = 0;
    content.setAttribute('role', 'region');
    content.setAttribute('aria-label', 'Sản phẩm theo danh mục');
    selectMegaTab(megaTabs[0]);
    megaTabs.forEach((tab, index) => {
      tab.addEventListener('click', () => selectMegaTab(tab));
      tab.addEventListener('keydown', (event) => {
        const directions = {ArrowDown:1, ArrowRight:1, ArrowUp:-1, ArrowLeft:-1};
        let next = index;
        if (event.key in directions) next = (index + directions[event.key] + megaTabs.length) % megaTabs.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = megaTabs.length - 1;
        else return;
        event.preventDefault();
        selectMegaTab(megaTabs[next], true);
      });
    });
  }
  const initializeQuote = (form) => {
    if (form.dataset.initialized) return;
    form.dataset.initialized = 'true';
    const quantity = form.elements.quantity;
    const fileInput = form.querySelector('[type="file"]');
    const fileList = form.querySelector('.sobi-file-list');
    const status = form.parentElement.querySelector('.sobi-message');
    const submit = form.querySelector('[type="submit"]');
    const params = new URLSearchParams(location.search);
    const category = params.get('loai');
    for (const radio of form.querySelectorAll('[name="category"]')) if (radio.value === category) radio.checked = true;
    if (params.get('ung-dung')) form.elements.message.value = `Ứng dụng: ${params.get('ung-dung').slice(0, 200)}`;
    const updateSummary = () => {
      const number = Number(quantity.value);
      const amount = quantity.validity.valid && number > 0 ? `${new Intl.NumberFormat('vi-VN').format(number)} cái ` : '';
      form.querySelector('[data-quote-summary]').textContent = amount + (form.querySelector('[name="category"]:checked')?.value || 'bao bì').toLocaleLowerCase('vi');
    };
    form.addEventListener('input', updateSummary);
    updateSummary();
    fileInput.addEventListener('change', () => {
      fileList.replaceChildren();
      const files = [...fileInput.files];
      const extensions = /\.(png|jpe?g|webp|ai|psd|psb|pdf|eps|indd|idml)$/i;
      const invalid = files.length > 3 || files.some(file => file.size > Number(form.dataset.fileEach) || !extensions.test(file.name)) || files.reduce((sum,file) => sum + file.size, 0) > Number(form.dataset.fileTotal);
      fileInput.setCustomValidity(invalid ? 'Kiểm tra định dạng, số file và giới hạn dung lượng bên dưới.' : '');
      for (const file of files) {
        const li = document.createElement('li');
        li.textContent = `${file.name} (${(file.size / 1048576).toFixed(2)} MB)`;
        fileList.append(li);
      }
      if (invalid) fileInput.reportValidity();
    });
    // Demo submissions are handled by demo.js without a network request.
    if (inBuilder) {
      submit.disabled = true;
      form.addEventListener('click', event => event.preventDefault());
    }
  };
  document.querySelectorAll('.sobi-quote-form').forEach(initializeQuote);
  const mobileQuote = document.querySelector('.sobi-mobile-quote');
  const quoteSection = document.querySelector('.sobi-quote');
  if (mobileQuote && quoteSection && !inBuilder) {
    new IntersectionObserver(([entry]) => { mobileQuote.hidden = entry.isIntersecting; }).observe(quoteSection);
  }
  if (inBuilder) new MutationObserver(() => document.querySelectorAll('.sobi-quote-form').forEach(initializeQuote)).observe(document.body, {childList:true, subtree:true});
  document.querySelector('.sobi-message:not([hidden])')?.focus({preventScroll:true});
})();
