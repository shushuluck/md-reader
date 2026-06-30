// Search Module
const searchInput = () => document.getElementById('search-input');
const searchCount = () => document.getElementById('search-count');

let matches = [];
let currentMatch = -1;
let searchTimer = null;

export function initSearch() {
  const input = searchInput();
  if (!input) return;

  input.addEventListener('input', () => {
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => doSearch(input.value), 150);
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.shiftKey ? prevMatch() : nextMatch();
    }
    if (e.key === 'Escape') {
      clearSearch();
      input.blur();
    }
  });

  document.getElementById('btn-search-prev')?.addEventListener('click', prevMatch);
  document.getElementById('btn-search-next')?.addEventListener('click', nextMatch);
}

export function focusSearch() {
  const input = searchInput();
  if (input) {
    input.focus();
    input.select();
  }
}

function doSearch(query) {
  clearHighlights();
  matches = [];
  currentMatch = -1;

  if (!query || query.length < 2) {
    searchCount().textContent = '';
    return;
  }

  const content = document.getElementById('preview-content');
  if (!content) return;

  // Text node search
  const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  while (walker.nextNode()) textNodes.push(walker.currentNode);

  const isRegex = query.startsWith('/') && query.lastIndexOf('/') > 0;
  let regex;
  try {
    if (isRegex) {
      const parts = query.match(/^\/(.+)\/([gimsuy]*)$/);
      regex = parts ? new RegExp(parts[1], parts[2] + 'g') : new RegExp(escapeRegex(query), 'gi');
    } else {
      regex = new RegExp(escapeRegex(query), 'gi');
    }
  } catch {
    regex = new RegExp(escapeRegex(query), 'gi');
  }

  textNodes.forEach(node => {
    const text = node.textContent;
    if (!regex.test(text)) return;
    regex.lastIndex = 0;

    const frag = document.createDocumentFragment();
    let lastIdx = 0;
    let match;
    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIdx) {
        frag.appendChild(document.createTextNode(text.slice(lastIdx, match.index)));
      }
      const mark = document.createElement('mark');
      mark.className = 'search-highlight';
      mark.textContent = match[0];
      frag.appendChild(mark);
      matches.push(mark);
      lastIdx = match.index + match[0].length;
      if (match.index === regex.lastIndex) regex.lastIndex++;
    }
    if (lastIdx < text.length) {
      frag.appendChild(document.createTextNode(text.slice(lastIdx)));
    }
    node.parentNode.replaceChild(frag, node);
  });

  searchCount().textContent = matches.length > 0 ? `${matches.length} 项` : '无结果';
  if (matches.length > 0) nextMatch();
}

function nextMatch() {
  if (matches.length === 0) return;
  if (currentMatch >= 0) matches[currentMatch].classList.remove('search-current');
  currentMatch = (currentMatch + 1) % matches.length;
  highlightCurrent();
}

function prevMatch() {
  if (matches.length === 0) return;
  if (currentMatch >= 0) matches[currentMatch].classList.remove('search-current');
  currentMatch = (currentMatch - 1 + matches.length) % matches.length;
  highlightCurrent();
}

function highlightCurrent() {
  const el = matches[currentMatch];
  el.classList.add('search-current');
  el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  searchCount().textContent = `${currentMatch + 1}/${matches.length}`;
}

function clearSearch() {
  clearHighlights();
  matches = [];
  currentMatch = -1;
  searchCount().textContent = '';
}

function clearHighlights() {
  // Remove search-current class first
  if (currentMatch >= 0 && matches[currentMatch]) {
    matches[currentMatch].classList.remove('search-current');
  }
  document.querySelectorAll('.search-highlight').forEach(mark => {
    const text = document.createTextNode(mark.textContent);
    mark.parentNode.replaceChild(text, mark);
  });
  // Normalize text nodes
  document.getElementById('preview-content')?.normalize();
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
