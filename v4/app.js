// KronosTime — концепт главной, версия 4. Без библиотек.
// Ссылки макета никуда не ведут: вместо перехода — подсказка.
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var still = /[?&]still\b/.test(location.search);
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var mobile = window.matchMedia('(max-width: 767px)');

  // Подсказка вместо перехода
  var toast = $('.toast');
  var toastTimer;
  var say = function (t) {
    toast.textContent = t;
    toast.classList.add('is-show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove('is-show'); }, 2200);
  };
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a');
    if (!a) { return; }
    var href = a.getAttribute('href') || '';
    if (href.charAt(0) === '#' && href.length > 1) { return; }
    if (a.hasAttribute('data-real')) { return; }
    e.preventDefault();
    var to = a.getAttribute('data-to');
    say(to ? 'Макет: здесь откроется ' + to : 'Макет: ссылка пока никуда не ведёт');
  });

  // Шапка: после начала прокрутки становится ниже
  var hd = $('.hd');
  var onScroll = function () { hd.classList.toggle('is-compact', window.scrollY > 120); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Меню каталога, люкса и брендов
  var openMega = null;
  var setMega = function (id) {
    $$('.mg').forEach(function (m) { m.hidden = m.id !== id; });
    $$('[data-mega]').forEach(function (b) { if (b.hasAttribute('aria-expanded')) { b.setAttribute('aria-expanded', b.getAttribute('data-mega') === id ? 'true' : 'false'); } });
    openMega = id;
  };
  $$('[data-mega]').forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var id = b.getAttribute('data-mega');
      setMega(openMega === id ? null : id);
    });
  });

  // Поиск: подсказки при фокусе
  var sr = $('.sr');
  $('.sr input').addEventListener('focus', function () { sr.classList.add('is-open'); });
  document.addEventListener('click', function (e) {
    if (openMega && !e.target.closest('.mg')) { setMega(null); }
    if (!sr.contains(e.target)) { sr.classList.remove('is-open'); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { setMega(null); sr.classList.remove('is-open'); }
  });

  // Баннер: варианты A, B, C и смена слайдов
  var body = document.body;
  var bn = $('.bn');
  var slides = $$('.bs', bn);
  var dots = $$('.bn__dot', bn);
  var agenda = $$('.ag', bn);
  var TIME = 6000;
  var cur = 0;
  var timer = null;
  var visible = function () { return slides.map(function (s, i) { return i; }).filter(function (i) { return getComputedStyle(slides[i]).display !== 'none'; }); };
  var show = function (i) {
    cur = i;
    slides.forEach(function (s, k) {
      var on = k === i;
      s.classList.toggle('is-on', on);
      s.setAttribute('aria-hidden', on ? 'false' : 'true');
      s.tabIndex = on ? 0 : -1;
    });
    dots.concat(agenda).forEach(function (d) { d.classList.remove('is-on'); });
    if (dots[i]) { void dots[i].offsetWidth; dots[i].classList.add('is-on'); }
    if (agenda[i]) { void agenda[i].offsetWidth; agenda[i].classList.add('is-on'); }
  };
  var step = function (dir) {
    var list = visible();
    var pos = list.indexOf(cur);
    if (pos < 0) { pos = 0; }
    show(list[(pos + dir + list.length) % list.length]);
  };
  var auto = !still && !reduce;
  var play = function () {
    clearTimeout(timer);
    if (!auto) { bn.classList.remove('is-playing'); return; }
    bn.classList.add('is-playing');
    timer = setTimeout(function () { step(1); play(); }, TIME);
  };
  $('.bn__arr--l').addEventListener('click', function () { step(-1); play(); });
  $('.bn__arr--r').addEventListener('click', function () { step(1); play(); });
  dots.forEach(function (d, i) { d.addEventListener('click', function () { show(i); play(); }); });
  agenda.forEach(function (a) { a.addEventListener('click', function () { show(+a.getAttribute('data-i')); play(); }); });
  var stage = $('.bn__stage');
  [stage, $('.bn__agenda')].forEach(function (el) {
    el.addEventListener('mouseenter', function () { clearTimeout(timer); bn.classList.add('is-paused'); });
    el.addEventListener('mouseleave', function () { bn.classList.remove('is-paused'); show(cur); play(); });
  });
  var x0 = null;
  stage.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  stage.addEventListener('touchend', function (e) {
    if (x0 === null) { return; }
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) { step(dx < 0 ? 1 : -1); play(); }
    x0 = null;
  });
  document.addEventListener('visibilitychange', function () { if (document.hidden) { clearTimeout(timer); } else { play(); } });
  mobile.addEventListener('change', function () { if (visible().indexOf(cur) < 0) { step(1); } });

  // Вариант (A, B, C) и высота (S, M, L) баннера — переключатели на панели концепта, запоминаются в адресе
  var state = { banner: 'a', bsize: 'm' };
  var mv = location.search.match(/banner=([abc])/);
  var ms = location.search.match(/bsize=([sml])/);
  if (mv) { state.banner = mv[1]; }
  if (ms) { state.bsize = ms[1]; }
  var apply = function () {
    body.setAttribute('data-banner', state.banner);
    body.setAttribute('data-bsize', state.bsize);
    $$('[data-variant]').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-variant') === state.banner ? 'true' : 'false'); });
    $$('.cb [data-bsize]').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-bsize') === state.bsize ? 'true' : 'false'); });
    try { history.replaceState(null, '', location.pathname + '?banner=' + state.banner + '&bsize=' + state.bsize + (still ? '&still' : '') + location.hash); } catch (err) { /* без истории — не страшно */ }
  };
  apply();
  $$('[data-variant]').forEach(function (b) { b.addEventListener('click', function () { state.banner = b.getAttribute('data-variant'); apply(); }); });
  $$('.cb [data-bsize]').forEach(function (b) { b.addEventListener('click', function () { state.bsize = b.getAttribute('data-bsize'); apply(); }); });
  if (visible().indexOf(0) < 0) { step(1); } else { show(0); }
  play();

  // Хиты: полка листается кнопками
  var shelf = $('[data-shelfbox]');
  if (shelf) {
    var sb = $$('[data-shelf]');
    var upd = function () {
      var max = shelf.scrollWidth - shelf.clientWidth;
      sb[0].disabled = shelf.scrollLeft < 4;
      sb[1].disabled = shelf.scrollLeft > max - 4;
    };
    sb.forEach(function (b) {
      b.addEventListener('click', function () { shelf.scrollBy({ left: +b.getAttribute('data-shelf') * shelf.clientWidth * 0.7, behavior: reduce ? 'auto' : 'smooth' }); });
    });
    shelf.addEventListener('scroll', upd, { passive: true });
    window.addEventListener('resize', upd);
    upd();
  }

  // Плавное появление блоков при прокрутке (как на apple.com)
  var rvs = $$('.rv');
  if (still || reduce || !('IntersectionObserver' in window)) {
    rvs.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (list) {
      list.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -10% 0px' });
    rvs.forEach(function (el) { io.observe(el); });
  }

  // Магазины по городам: переключатель-таблетка, фоновое название города, карточки появляются по очереди
  var cs = $('[data-cs]');
  if (cs) {
    var csTabs = $$('.cs__tab', cs);
    var csPanels = $$('.cs__panel', cs);
    var csWords = $$('.cs__word', cs);
    var csPill = $('.cs__pill', cs);
    var movePill = function (t) { csPill.style.setProperty('--px', t.offsetLeft + 'px'); csPill.style.setProperty('--pw', t.offsetWidth + 'px'); };
    var csShow = function (i) {
      csTabs.forEach(function (t, k) { t.classList.toggle('is-on', k === i); t.setAttribute('aria-selected', k === i ? 'true' : 'false'); });
      csPanels.forEach(function (p, k) { p.hidden = k !== i; p.classList.remove('is-on'); if (k === i) { void p.offsetWidth; requestAnimationFrame(function () { p.classList.add('is-on'); }); } });
      csWords.forEach(function (w, k) { w.classList.toggle('is-on', k === i); });
      movePill(csTabs[i]);
      csUpd();
    };
    var csArrows = $('.cs__arrows', cs);
    var csSteps = $$('[data-cs-step]', cs);
    var csGrid = function () { return $('.cs__panel:not([hidden]) .cs__grid', cs); };
    var csUpd = function () {
      var g = csGrid();
      if (!g) { return; }
      var max = g.scrollWidth - g.clientWidth;
      csArrows.hidden = max < 4;
      csSteps[0].disabled = g.scrollLeft < 4;
      csSteps[1].disabled = g.scrollLeft > max - 4;
    };
    csSteps.forEach(function (b) { b.addEventListener('click', function () { var g = csGrid(); g.scrollBy({ left: +b.getAttribute('data-cs-step') * g.clientWidth * 0.68, behavior: reduce ? 'auto' : 'smooth' }); }); });
    $$('.cs__grid', cs).forEach(function (g) { g.addEventListener('scroll', csUpd, { passive: true }); });
    window.addEventListener('resize', csUpd);
    csTabs.forEach(function (t, i) { t.addEventListener('click', function () { csShow(i); }); });
    window.addEventListener('resize', function () { movePill($('.cs__tab.is-on', cs)); });
    if (document.fonts && document.fonts.ready) { document.fonts.ready.then(function () { movePill($('.cs__tab.is-on', cs)); }); }
    movePill(csTabs[0]);
    csUpd();
  }

  // «Под какой случай?»: панель раскрывается при наведении (на телефоне — по нажатию)
  var occ = $$('.oc');
  var openOcc = function (el) {
    occ.forEach(function (o) {
      var on = o === el;
      o.classList.toggle('is-open', on);
      $('.oc__tab', o).setAttribute('aria-expanded', on ? 'true' : 'false');
    });
  };
  var hoverT;
  occ.forEach(function (o) {
    $('.oc__tab', o).addEventListener('click', function () { openOcc(o); });
    o.addEventListener('mouseenter', function () {
      if (mobile.matches) { return; }
      clearTimeout(hoverT);
      hoverT = setTimeout(function () { openOcc(o); }, 120);
    });
    o.addEventListener('mouseleave', function () { clearTimeout(hoverT); });
  });

  // Избранное и корзина
  var favN = 0;
  var cartN = 0;
  var badge = function (sel, n) { $$(sel).forEach(function (b) { b.textContent = n; b.hidden = n < 1; }); };
  document.addEventListener('click', function (e) {
    var fav = e.target.closest('.pc__fav');
    if (fav) {
      var on = !fav.classList.contains('is-on');
      fav.classList.toggle('is-on', on);
      fav.setAttribute('aria-pressed', on ? 'true' : 'false');
      favN += on ? 1 : -1;
      badge('[data-fav]', favN);
      say(on ? 'Добавлено в избранное' : 'Убрано из избранного');
      return;
    }
    var cart = e.target.closest('.pc__cart, [data-cart-btn]');
    if (cart) {
      cartN += 1;
      cart.classList.add('is-on');
      badge('[data-cart]', cartN);
      say('Товар в корзине');
    }
  });

  // Подписка: нужен e-mail и согласие на обработку данных
  var form = $('.sub');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var mail = $('input[type=email]', form);
      var agree = $('.chk input[required]', form);
      var okMail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail.value);
      mail.classList.toggle('is-bad', !okMail);
      agree.closest('.chk').classList.toggle('is-bad', !agree.checked);
      if (!okMail) { say('Введите e-mail'); mail.focus(); return; }
      if (!agree.checked) { say('Нужно согласие на обработку персональных данных'); return; }
      say('Макет: форма никуда не отправляет данные');
    });
  }

  // Панель концепта
  var cb = $('.cb');
  $('.cb__x').addEventListener('click', function () { cb.remove(); });
})();
