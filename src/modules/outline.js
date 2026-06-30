// Outline / TOC Module
const panel = () => document.getElementById('outline-panel');
const content = () => document.getElementById('outline-content');

let _scrollHandler = null;
let _rafId = null;

export function initOutline() {
  document.getElementById('btn-close-outline')?.addEventListener('click', () => {
    panel()?.classList.add('hidden');
  });
}

export function toggleOutline() {
  const p = panel();
  if (!p) return;
  p.classList.toggle('hidden');
  if (!p.classList.contains('hidden')) {
    refreshOutline();
  } else {
    removeScrollHandler();
  }
}

function removeScrollHandler() {
  if (_rafId) {
    cancelAnimationFrame(_rafId);
    _rafId = null;
  }
  const previewEl = document.getElementById('preview');
  if (previewEl && _scrollHandler) {
    previewEl.removeEventListener('scroll', _scrollHandler);
    _scrollHandler = null;
  }
}

export function refreshOutline() {
  const container = content();
  const preview = document.getElementById('preview-content');
  if (!container || !preview) return;

  // Always remove old scroll handler first
  removeScrollHandler();

  const headings = preview.querySelectorAll('h1, h2, h3, h4, h5, h6');
  container.innerHTML = '';

  if (headings.length === 0) {
    container.innerHTML = '<div style="padding:12px;opacity:0.5;font-size:12px">无标题</div>';
    return;
  }

  const isMobile = () => window.innerWidth <= 600;

  headings.forEach((h, i) => {
    const level = parseInt(h.tagName[1]);
    const id = `heading-${i}`;
    h.id = id;

    const item = document.createElement('a');
    item.className = `outline-item level-${level}`;
    item.textContent = h.textContent;
    item.href = `#${id}`;
    item.addEventListener('click', (e) => {
      e.preventDefault();
      h.scrollIntoView({ behavior: 'smooth', block: 'start' });
      container.querySelectorAll('.outline-item').forEach(el => el.classList.remove('active'));
      item.classList.add('active');
      // Auto-close on mobile
      if (isMobile()) {
        panel()?.classList.add('hidden');
      }
    });
    container.appendChild(item);
  });

  // Scroll spy with rAF throttle (no jank)
  const previewEl = document.getElementById('preview');
  if (previewEl) {
    const items = container.querySelectorAll('.outline-item');
    _scrollHandler = () => {
      if (_rafId) return; // already scheduled
      _rafId = requestAnimationFrame(() => {
        _rafId = null;
        let activeIdx = 0;
        const previewRect = previewEl.getBoundingClientRect();
        headings.forEach((h, i) => {
          if (h.getBoundingClientRect().top - previewRect.top < 80) {
            activeIdx = i;
          }
        });
        items.forEach((el, i) => {
          el.classList.toggle('active', i === activeIdx);
        });
      });
    };
    previewEl.addEventListener('scroll', _scrollHandler, { passive: true });
  }
}
