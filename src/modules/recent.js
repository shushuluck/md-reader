// Recent Files Module
import { invoke } from '../main.js';
import { openFileInTab } from './tabs.js';

const section = () => document.getElementById('recent-files-section');
const list = () => document.getElementById('recent-files-list');

export async function loadRecentFiles() {
  try {
    const files = await invoke('read_recent_files');
    renderRecentFiles(files);
  } catch {
    // Browser mode: try localStorage
    const files = JSON.parse(localStorage.getItem('md-reader-recent') || '[]');
    renderRecentFiles(files);
  }
}

export async function addRecentFile(path) {
  try {
    await invoke('add_recent_file', { path });
    await loadRecentFiles();
  } catch {
    // Browser mode
    let files = JSON.parse(localStorage.getItem('md-reader-recent') || '[]');
    files = [path, ...files.filter(f => f !== path)].slice(0, 10);
    localStorage.setItem('md-reader-recent', JSON.stringify(files));
    renderRecentFiles(files);
  }
}

function renderRecentFiles(files) {
  const sec = section();
  const lst = list();
  if (!sec || !lst || !files.length) return;

  sec.classList.remove('hidden');
  lst.innerHTML = '';

  files.forEach(path => {
    const name = path.split(/[/\\]/).pop();
    const item = document.createElement('div');
    item.className = 'recent-item';
    item.textContent = `📄 ${name}`;
    item.title = path;
    item.addEventListener('click', async () => {
      await openFileInTab(path);
    });
    lst.appendChild(item);
  });
}
