// Outline / TOC Module
const panel = () => document.getElementById('outline-panel');
const content = () => document.getElementById('outline-content');

let _scrollHandler = null;

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
  }
}

export function refreshOutline() {
  const container = content();
  const preview = document.getElementById('preview-content');
  if (!container || !preview) return;

  // Remove old scroll handler
  const previewEl = document.getElementById('preview');
  if (previewEl && _scrollHandler) {
    previewEl.removeEventListener('scroll', _scrollHandler);
    _scrollHandler = null;
  }

  const headings = preview.querySelectorAll('h1, h2, h3, h4, h5, h6');
  container.innerHTML = '';

  if (headings.length === 0) {
    container.innerHTML = '<div style="padding:12px;opacity:0.5;font-size:12px">无标题</div>';
    return;
  }

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
    });
    container.appendChild(item);
  });

  // Scroll spy (single handler, properly managed)
  if (previewEl) {
    _scrollHandler = () => {
      let activeIdx = 0;
      headings.forEach((h, i) => {
        const rect = h.getBoundingClientRect();
        if (rect.top < 100) activeIdx = i;
      });
      container.querySelectorAll('.outline-item').forEach((el, i) => {
        el.classList.toggle('active', i === activeIdx);
      });
    };
    previewEl.addEventListener('scroll', _scrollHandler);
  }
}
