// Tab Management
import { invoke } from '../main.js';
import { renderMarkdown, setEditorContent, getEditorContent, isEditing } from './renderer.js';
import { showView, updateStatus, updateFileInfo, updateContentStats, showFileChangeToast } from '../main.js';
import { refreshOutline } from './outline.js';

const tabs = []; // { id, name, path, content, modified, size, encoding, cachedHtml }

// Initialize tab system with event delegation (bind once, no leaks)
export function initTabs() {
  const list = tabList();
  if (!list) return;

  // Click delegation
  list.addEventListener('click', (e) => {
    const tabEl = e.target.closest('.tab');
    if (!tabEl) return;
    const id = parseInt(tabEl.dataset.id);
    if (e.target.closest('.tab-close')) {
      e.stopPropagation();
      closeTab(id);
    } else {
      switchToTab(id);
    }
  });

  // Drag & drop delegation
  let dragId = null;
  list.addEventListener('dragstart', (e) => {
    const tabEl = e.target.closest('.tab');
    if (tabEl) {
      dragId = parseInt(tabEl.dataset.id);
      e.dataTransfer.setData('text/plain', String(dragId));
    }
  });
  list.addEventListener('dragover', (e) => {
    e.preventDefault();
    const tabEl = e.target.closest('.tab');
    if (tabEl) tabEl.style.opacity = '0.5';
  });
  list.addEventListener('dragleave', (e) => {
    const tabEl = e.target.closest('.tab');
    if (tabEl) tabEl.style.opacity = '';
  });
  list.addEventListener('drop', (e) => {
    e.preventDefault();
    const tabEl = e.target.closest('.tab');
    if (!tabEl) return;
    tabEl.style.opacity = '';
    const dropId = parseInt(tabEl.dataset.id);
    const dragIdx = tabs.findIndex(t => t.id === dragId);
    const dropIdx = tabs.findIndex(t => t.id === dropId);
    if (dragIdx !== -1 && dropIdx !== -1 && dragIdx !== dropIdx) {
      const [moved] = tabs.splice(dragIdx, 1);
      tabs.splice(dropIdx, 0, moved);
      renderTabBar();
    }
    dragId = null;
  });
}

let activeTabId = null;
let tabIdCounter = 0;

const tabList = () => document.getElementById('tab-list');
const welcomeEl = () => document.getElementById('welcome');

export function getCurrentTab() {
  return tabs.find(t => t.id === activeTabId) || null;
}

export function getTabs() {
  return tabs;
}

export function hasUnsavedChanges() {
  return tabs.some(t => t.modified);
}

export async function openFileInTab(path) {
  // Check if already open
  const existing = tabs.find(t => t.path === path);
  if (existing) {
    switchToTab(existing.id);
    // Reload content
    try {
      const content = await invoke('read_file_content', { path });
      existing.content = content;
      existing.modified = false;
      delete existing.cachedHtml; // invalidate cache
      renderTabContent(existing);
    } catch (e) {
      updateStatus(`读取失败: ${e}`);
    }
    return existing;
  }

  // Read file
  try {
    const content = await invoke('read_file_content', { path });
    const name = path.split(/[/\\]/).pop();
    const tab = {
      id: ++tabIdCounter,
      name,
      path,
      content,
      modified: false,
      size: new Blob([content]).size,
      encoding: 'UTF-8',
      cachedHtml: null,
    };
    tabs.push(tab);
    renderTabBar();
    switchToTab(tab.id);
    
    // Update window title
    document.title = `${name} - MD Reader`;
    document.getElementById('file-name').textContent = name;

    return tab;
  } catch (e) {
    updateStatus(`打开失败: ${e}`);
    return null;
  }
}

export function createEmptyTab() {
  const tab = {
    id: ++tabIdCounter,
    name: '未命名.md',
    path: null,
    content: '',
    modified: false,
    size: 0,
    encoding: 'UTF-8',
    cachedHtml: null,
  };
  tabs.push(tab);
  renderTabBar();
  switchToTab(tab.id);
  return tab;
}

function switchToTab(id) {
  activeTabId = id;
  const tab = getCurrentTab();
  if (!tab) return;

  renderTabBar();
  renderTabContent(tab);

  // Update window title
  document.title = `${tab.name} - MD Reader`;
  document.getElementById('file-name').textContent = tab.name;

  // Auto-refresh outline if visible
  const outlinePanel = document.getElementById('outline-panel');
  if (outlinePanel && !outlinePanel.classList.contains('hidden')) {
    refreshOutline();
  }
}

function renderTabContent(tab) {
  showView('preview');
  const container = document.getElementById('preview-content');
  
  // Cache: skip re-render if content unchanged
  if (!tab.modified && tab.cachedHtml && container) {
    container.innerHTML = tab.cachedHtml;
    // Rebind image clicks
    container.querySelectorAll('img').forEach(img => {
      img.addEventListener('click', () => window.open(img.src, '_blank'));
      img.style.cursor = 'pointer';
    });
  } else {
    renderMarkdown(tab.content);
    if (container) tab.cachedHtml = container.innerHTML;
  }
  
  updateContentStats(tab.content);
  updateFileInfo({ size: tab.size || new Blob([tab.content]).size, encoding: tab.encoding || 'UTF-8' });
}

export function closeTab(id) {
  const idx = tabs.findIndex(t => t.id === id);
  if (idx === -1) return;

  const tab = tabs[idx];
  // Confirm if modified
  if (tab.modified) {
    if (!confirm(`文件 "${tab.name}" 已修改，确定要关闭吗？`)) return;
  }

  const wasActive = id === activeTabId;
  tabs.splice(idx, 1);
  renderTabBar();

  if (wasActive) {
    if (tabs.length > 0) {
      const newIdx = Math.min(idx, tabs.length - 1);
      switchToTab(tabs[newIdx].id);
    } else {
      activeTabId = null;
      showView('welcome');
      document.title = 'MD Reader';
      document.getElementById('file-name').textContent = '未打开文件';
      updateStatus('就绪');
    }
  }
}

export function closeCurrentTab() {
  if (activeTabId) closeTab(activeTabId);
}

export async function saveCurrentFile() {
  const tab = getCurrentTab();
  if (!tab) return;

  if (!tab.path) {
    // Need to save as new file
    try {
      const { save } = await import('@tauri-apps/plugin-dialog');
      const path = await save({
        filters: [{ name: 'Markdown', extensions: ['md'] }],
        defaultPath: tab.name,
      });
      if (!path) return;
      tab.path = path;
      tab.name = path.split(/[/\\]/).pop();
    } catch {
      updateStatus('保存对话框不可用');
      return;
    }
  }

  try {
    const content = isEditing() ? getEditorContent() : tab.content;
    await invoke('write_file_content', { path: tab.path, content });
    tab.content = content;
    tab.modified = false;
    tab.size = new Blob([content]).size;
    delete tab.cachedHtml; // invalidate cache after save
    renderTabBar();
    updateStatus(`已保存: ${tab.name}`);
  } catch (e) {
    updateStatus(`保存失败: ${e}`);
  }
}

export function markModified() {
  const tab = getCurrentTab();
  if (tab) {
    tab.modified = true;
    delete tab.cachedHtml;
    renderTabBar();
    document.getElementById('btn-save').disabled = false;
  }
}

// Render tab bar DOM only (events handled by delegation in initTabs)
function renderTabBar() {
  const list = tabList();
  list.innerHTML = '';

  tabs.forEach(tab => {
    const el = document.createElement('div');
    el.className = `tab${tab.id === activeTabId ? ' active' : ''}`;
    el.dataset.id = tab.id;
    el.draggable = true;

    const nameSpan = document.createElement('span');
    nameSpan.className = 'tab-name';
    nameSpan.textContent = tab.name;
    el.appendChild(nameSpan);

    if (tab.modified) {
      const dot = document.createElement('span');
      dot.className = 'tab-modified';
      el.appendChild(dot);
    }

    const closeBtn = document.createElement('span');
    closeBtn.className = 'tab-close';
    closeBtn.textContent = '✕';
    el.appendChild(closeBtn);

    list.appendChild(el);
  });
}
