/* Interface enhancements must work even when the WebGL context is unavailable. */
(() => {
  'use strict';
  const root = document.documentElement;
  root.classList.add('js');
  const read = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch { /* Private browsing still works. */ } };
  let lang = read('hyperion-language') === 'en' ? 'en' : 'fr';
  let theme = read('hyperion-theme') || 'dark';
  if (!['light', 'dark'].includes(theme)) theme = 'dark';
  function setLanguage(value) {
    lang = value;
    root.lang = lang;
    document.querySelectorAll('[data-fr][data-en]').forEach(el => {
      const value = el.dataset[lang];
      if (el.hasAttribute('data-i18n-aria')) el.setAttribute('aria-label', value);
      else el.textContent = value;
    });
    document.querySelectorAll('[data-lang-label]').forEach(el => el.classList.toggle('lang-current', el.dataset.langLabel === lang));
    document.querySelectorAll('.lang-block').forEach(el => el.toggleAttribute('hidden', el.dataset.lang !== lang));
    const toggle = document.getElementById('lang-toggle');
    if (toggle) toggle.setAttribute('aria-label', lang === 'fr' ? 'Read this page in English' : 'Lire cette page en français');
    save('hyperion-language', lang);
    const hash = decodeURIComponent(location.hash.slice(1));
    if (hash) {
      const translated = lang === 'en' && !hash.endsWith('-en') ? hash + '-en' : lang === 'fr' ? hash.replace(/-en$/, '') : hash;
      const target = document.getElementById(translated);
      if (target && translated !== hash) {
        history.replaceState(null, '', '#' + translated);
        requestAnimationFrame(() => target.scrollIntoView());
      }
    }
    document.dispatchEvent(new CustomEvent('hyperion:language', {detail: lang}));
    filterPublications();
  }
  function setTheme(value) {
    theme = value;
    root.dataset.theme = theme;
    const button = document.getElementById('theme-toggle');
    if (button) {
      button.setAttribute('aria-pressed', String(theme === 'light'));
      button.setAttribute('aria-label', lang === 'fr' ? 'Thème clair' : 'Light theme');
      button.querySelector('[data-theme-symbol]').textContent = theme === 'dark' ? '☼' : '◐';
    }
    save('hyperion-theme', theme);
    document.dispatchEvent(new CustomEvent('hyperion:theme', {detail: theme}));
  }
  const menu = document.querySelector('.menu-disclosure');
  if (menu) {
    const summary = menu.querySelector('summary');
    menu.addEventListener('toggle', () => summary.setAttribute('aria-expanded', String(menu.open)));
    document.addEventListener('click', event => { if (!menu.contains(event.target)) menu.open = false; });
    menu.addEventListener('keydown', event => { if (event.key === 'Escape') { menu.open = false; summary.focus(); } });
    menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => { menu.open = false; }));
  }
  document.getElementById('lang-toggle')?.addEventListener('click', () => { setLanguage(lang === 'fr' ? 'en' : 'fr'); setTheme(theme); });
  document.getElementById('theme-toggle')?.addEventListener('click', () => setTheme(theme === 'dark' ? 'light' : 'dark'));
  const search = document.getElementById('publication-search');
  const year = document.getElementById('publication-year');
  const type = document.getElementById('publication-type');
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  function filterPublications() {
    if (!search) return;
    const query = normalize(search.value.trim());
    let count = 0;
    document.querySelectorAll('.publication').forEach(item => {
      const show = (!query || normalize(item.textContent).includes(query)) && (!year.value || item.dataset.year === year.value) && (!type.value || item.dataset.type === type.value);
      item.hidden = !show;
      if (show) count++;
    });
    document.getElementById('publication-count').textContent = lang === 'fr' ? `${count} référence${count > 1 ? 's' : ''} affichée${count > 1 ? 's' : ''}` : `${count} reference${count === 1 ? '' : 's'} shown`;
    document.getElementById('publication-empty').hidden = count !== 0;
  }
  [search, year, type].filter(Boolean).forEach(el => el.addEventListener('input', filterPublications));
  setLanguage(lang);
  setTheme(theme);
  if (location.hostname === 'hyperion.huma-num.fr') document.querySelectorAll('.test-notice').forEach(el => { el.hidden = true; });
})();
