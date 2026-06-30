// Theme Switcher
const THEMES = ['glass', 'flat', 'paper'];
const STORAGE_KEY = 'md-reader-theme';

export function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY) || 'glass';
  setTheme(saved);

  // Bind theme buttons
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      setTheme(btn.dataset.theme);
    });
  });
}

export function setTheme(name) {
  if (!THEMES.includes(name)) return;
  document.body.dataset.theme = name;
  localStorage.setItem(STORAGE_KEY, name);

  // Update active state
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.theme === name);
  });
  // MutationObserver in main.js handles mermaid theme update
}

export function getCurrentTheme() {
  return document.body.dataset.theme || 'glass';
}
