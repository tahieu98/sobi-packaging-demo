(() => {
  "use strict";
  const inBuilder = new URLSearchParams(location.search).has('uxb_iframe');
  if (inBuilder) document.body.classList.add('sobi-builder-preview');
  const showVideoStatus = (container, message) => {
    const status = container.parentElement.querySelector('.sobi-video-status');
    if (status) { status.textContent = message; status.hidden = !message; }
  };
  const activateVideo = (container, automatic = false) => {
    if (!container.querySelector('.sobi-video-play')) return;
    const poster = container.querySelector('img')?.currentSrc;
    if (container.dataset.videoProvider === 'mp4') {
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
        showVideoStatus(container, 'Không thể tải video. Bạn có thể mở video bằng liên kết bên dưới.');
      });
      container.replaceChildren(video);
      video.src = container.dataset.videoSrc;
      const started = video.play();
      started?.catch(() => {
        if (container.dataset.videoState === 'error') return;
        container.dataset.videoState = 'paused';
        showVideoStatus(container, 'Chạm nút phát trên video để xem.');
      });
      if (!automatic) video.focus({ preventScroll: true });
    } else {
      const iframe = document.createElement('iframe');
      const url = new URL(container.dataset.videoSrc);
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
    document.querySelectorAll('[data-sobi-video][data-video-autoplay="true"]').forEach((container) => {
      const delay = Math.max(2000, Math.min(10000, Number(container.dataset.videoDelay) || 2500));
      setTimeout(() => {
        if (document.visibilityState === 'visible') activateVideo(container, true);
        else document.addEventListener('visibilitychange', () => {
          if (document.visibilityState === 'visible') activateVideo(container, true);
        }, { once: true });
      }, delay);
    });
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
      const element = event.target.closest(".sobi-picks .sobi-product-card, .sobi-hero-explore, .sobi-hero-custom, .sobi-mega .sobi-text-link");
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
      if (open) panel.querySelector("input, button, a")?.focus();
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
  document
    .querySelector("[data-gallery-open]")
    ?.addEventListener("click", (event) => {
      galleryOpener = event.currentTarget;
      gallery?.showModal();
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
  const megaTabs = [...document.querySelectorAll('[data-mega-tab]')];
  const selectMegaTab = (tab, focus = false) => {
    megaTabs.forEach((item) => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
    });
    if (focus) tab.focus();
  };
  if (megaTabs.length) {
    document.getElementById('sobi-mega').classList.add('is-enhanced');
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
