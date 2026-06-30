// File Tree Module
import { invoke } from '../main.js';
import { openFileInTab } from './tabs.js';
import { addRecentFile } from './recent.js';

const sidebar = () => document.getElementById('sidebar');
const tree = () => document.getElementById('file-tree');

let rootPath = '';
let _clickTimer = null;

export function initFileTree(folderPath) {
  rootPath = folderPath;
  sidebar()?.classList.remove('hidden');
  loadTree(folderPath, tree());
}

export function toggleSidebar() {
  const s = sidebar();
  if (!s) return;
  s.classList.toggle('hidden');
}

async function loadTree(dirPath, container) {
  if (!container) return;
  container.innerHTML = '<div style="padding:8px;opacity:0.5;font-size:12px">加载中...</div>';

  try {
    const entries = await invoke('list_directory', { path: dirPath });
    container.innerHTML = '';

    entries.forEach(entry => {
      const item = document.createElement('div');
      item.className = 'tree-item';

      const icon = document.createElement('span');
      icon.className = 'tree-icon';
      icon.textContent = entry.is_dir ? '📁' : getFileIcon(entry.name);
      item.appendChild(icon);

      const name = document.createElement('span');
      name.className = 'tree-name';
      name.textContent = entry.name;
      item.appendChild(name);

      if (entry.is_dir) {
        const children = document.createElement('div');
        children.className = 'tree-children collapsed';
        
        item.addEventListener('click', () => {
          const isCollapsed = children.classList.contains('collapsed');
          children.classList.toggle('collapsed');
          icon.textContent = isCollapsed ? '📂' : '📁';
          if (isCollapsed && children.children.length === 0) {
            loadTree(entry.path, children);
          }
        });

        container.appendChild(item);
        container.appendChild(children);
      } else {
        item.addEventListener('click', () => {
          if (!isMarkdown(entry.name)) return;
          // Debounce: rapid clicks only trigger last one
          if (_clickTimer) clearTimeout(_clickTimer);
          _clickTimer = setTimeout(async () => {
            await openFileInTab(entry.path);
            await addRecentFile(entry.path);
          }, 150);
        });
        container.appendChild(item);
      }
    });

    if (entries.length === 0) {
      container.innerHTML = '<div style="padding:8px;opacity:0.5;font-size:12px">空文件夹</div>';
    }
  } catch (e) {
    container.innerHTML = `<div style="padding:8px;color:red;font-size:12px">读取失败: ${e}</div>`;
  }
}

function isMarkdown(name) {
  return /\.(md|markdown|mdx|txt|rst|org|html|htm|json|yaml|yml|xml|csv|tsv|log|tex)$/i.test(name);
}

function getFileIcon(name) {
  if (/\.(md|markdown|mdx|rst|org)$/i.test(name)) return '📝';
  if (/\.(txt|log)$/i.test(name)) return '📄';
  if (/\.(html|htm|xml)$/i.test(name)) return '🌐';
  if (/\.(json|yaml|yml)$/i.test(name)) return '⚙️';
  if (/\.(csv|tsv)$/i.test(name)) return '📊';
  if (/\.(tex)$/i.test(name)) return '📐';
  if (/\.(jpg|jpeg|png|gif|svg|webp)$/i.test(name)) return '🖼️';
  if (/\.(js|ts|py|rs|go|java|c|cpp|h)$/i.test(name)) return '📜';
  return '📄';
}
