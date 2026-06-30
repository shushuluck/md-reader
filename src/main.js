// MD Reader - Main Entry
import './styles/base.css';
import './styles/glass.css';
import './styles/flat.css';
import './styles/paper.css';
import './styles/mobile.css';

import { initTabs, openFileInTab, getCurrentTab, saveCurrentFile, closeCurrentTab } from './modules/tabs.js';
import { renderMarkdown, getEditorContent, setEditorContent, isEditing, toggleEditMode } from './modules/renderer.js';
import { initSearch, focusSearch } from './modules/search.js';
import { initOutline, toggleOutline, refreshOutline } from './modules/outline.js';
import { loadRecentFiles, addRecentFile } from './modules/recent.js';
import { initFileTree, toggleSidebar } from './modules/file-tree.js';
import { initTheme } from './modules/theme.js';
import { initMobile } from './modules/mobile.js';

// Tauri API (with fallback for browser dev)
let tauriInvoke = null;
let tauriListen = null;

async function initTauri() {
  try {
    const { invoke } = await import('@tauri-apps/api/core');
    const { listen } = await import('@tauri-apps/api/event');
    tauriInvoke = invoke;
    tauriListen = listen;
    return true;
  } catch {
    console.warn('Tauri API not available, running in browser mode');
    return false;
  }
}

// Expose invoke/listen for modules
export function invoke(cmd, args) {
  if (tauriInvoke) return tauriInvoke(cmd, args);
  return Promise.reject(new Error('Tauri not available'));
}

export async function listenEvent(event, handler) {
  if (tauriListen) return tauriListen(event, handler);
  return () => {};
}

// DOM refs
const $ = (s) => document.querySelector(s);
const welcomeEl = $('#welcome');
const previewEl = $('#preview');
const editorEl = $('#editor');

export function showView(view) {
  welcomeEl.classList.toggle('hidden', view !== 'welcome');
  previewEl.classList.toggle('hidden', view !== 'preview');
  editorEl.classList.toggle('hidden', view !== 'editor');
}

export function updateStatus(text) {
  $('#status-text').textContent = text;
}

export function updateFileInfo(meta) {
  if (!meta) return;
  $('#status-encoding').textContent = meta.encoding || 'UTF-8';
  $('#status-size').textContent = formatSize(meta.size);
}

export function updateContentStats(text) {
  const lines = text.split('\n').length;
  const chars = text.replace(/\s/g, '').length;
  const words = text.length;
  const readTime = Math.max(1, Math.ceil(chars / 500));
  $('#status-lines').textContent = `${lines} 行`;
  $('#status-words').textContent = `${chars} 字`;
  $('#status-read-time').textContent = `阅读 ~${readTime} 分钟`;
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// File change toast
let fileChangeHandler = null;

export function showFileChangeToast(path, reloadFn) {
  const toast = $('#file-changed-toast');
  toast.classList.remove('hidden');
  fileChangeHandler = reloadFn;
  $('#btn-reload').onclick = () => {
    if (fileChangeHandler) fileChangeHandler();
    toast.classList.add('hidden');
  };
  $('#btn-dismiss-toast').onclick = () => {
    toast.classList.add('hidden');
  };
  // Auto dismiss after 10s
  setTimeout(() => toast.classList.add('hidden'), 10000);
}

// Keyboard shortcuts
function initKeyboard() {
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
      switch (e.key.toLowerCase()) {
        case 'o':
          e.preventDefault();
          if (e.shiftKey) openFolderDialog();
          else openFileDialog();
          break;
        case 's':
          e.preventDefault();
          saveCurrentFile();
          break;
        case 'e':
          e.preventDefault();
          toggleEditMode();
          break;
        case 'f':
          e.preventDefault();
          focusSearch();
          break;
        case 'b':
          e.preventDefault();
          toggleSidebar();
          break;
        case 'w':
          e.preventDefault();
          closeCurrentTab();
          break;
      }
      if (e.shiftKey && e.key.toLowerCase() === 'o') {
        e.preventDefault();
        toggleOutline();
      }
    }
    if (e.key === 'F5') {
      e.preventDefault();
      const tab = getCurrentTab();
      if (tab && tab.path) {
        openFileInTab(tab.path);
      }
    }
  });
}

// File dialog via Tauri
async function openFileDialog() {
  try {
    const { open } = await import('@tauri-apps/plugin-dialog');
    const path = await open({
      multiple: false,
      filters: [{ name: 'Markdown', extensions: ['md', 'markdown', 'txt', 'mdx'] }],
    });
    if (path) {
      await openFileInTab(path);
      await addRecentFile(path);
    }
  } catch {
    console.warn('File dialog not available');
  }
}

async function openFolderDialog() {
  try {
    const { open } = await import('@tauri-apps/plugin-dialog');
    const path = await open({ directory: true });
    if (path) {
      initFileTree(path);
    }
  } catch {
    console.warn('Folder dialog not available');
  }
}

// Window controls
function initWindowControls() {
  $('#btn-minimize')?.addEventListener('click', async () => {
    try {
      const { getCurrentWindow } = await import('@tauri-apps/api/window');
      getCurrentWindow().minimize();
    } catch {}
  });
  $('#btn-maximize')?.addEventListener('click', async () => {
    try {
      const { getCurrentWindow } = await import('@tauri-apps/api/window');
      const win = getCurrentWindow();
      const maximized = await win.isMaximized();
      maximized ? win.unmaximize() : win.maximize();
    } catch {}
  });
  $('#btn-close')?.addEventListener('click', async () => {
    try {
      const { getCurrentWindow } = await import('@tauri-apps/api/window');
      getCurrentWindow().close();
    } catch {}
  });
}

// Init
async function init() {
  const isTauri = await initTauri();
  
  initTheme();
  initMobile();
  initTabs();
  initSearch();
  initOutline();
  initKeyboard();
  initWindowControls();

  // Toolbar buttons
  $('#btn-open').addEventListener('click', openFileDialog);
  $('#btn-open-folder').addEventListener('click', openFolderDialog);
  $('#btn-save').addEventListener('click', saveCurrentFile);
  $('#btn-edit').addEventListener('click', toggleEditMode);
  $('#btn-outline').addEventListener('click', toggleOutline);
  $('#btn-sidebar').addEventListener('click', toggleSidebar);
  $('#btn-new-tab').addEventListener('click', () => {
    // New empty tab
    import('./modules/tabs.js').then(m => m.createEmptyTab());
  });

  // Load recent files
  await loadRecentFiles();

  // Listen for file change events from Tauri
  if (isTauri) {
    await listenEvent('file-changed', (event) => {
      const tab = getCurrentTab();
      if (tab && tab.path === event.payload.path) {
        showFileChangeToast(event.payload.path, () => {
          openFileInTab(tab.path);
        });
      }
    });
  }

  // Enable save button when editing
  $('#editor-textarea').addEventListener('input', () => {
    $('#btn-save').disabled = false;
    const content = getEditorContent();
    updateContentStats(content);
  });

  // Handle drag & drop
  document.addEventListener('dragover', (e) => e.preventDefault());
  document.addEventListener('drop', async (e) => {
    e.preventDefault();
    // Tauri file drop handling would go here
  });

  updateStatus('就绪');
}

init();
