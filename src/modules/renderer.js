// Markdown Renderer with Mermaid + Code Copy + Image Preview
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';
import mermaid from 'mermaid';

const previewContent = () => document.getElementById('preview-content');
const editorTextarea = () => document.getElementById('editor-textarea');
const previewEl = () => document.getElementById('preview');
const editorEl = () => document.getElementById('editor');

let editing = false;
let mermaidIdCounter = 0;

// Inline XSS sanitizer (no npm dependency)
const ALLOWED_TAGS = new Set([
  'div','span','p','br','hr','section','article','aside','header','footer','nav',
  'h1','h2','h3','h4','h5','h6','a','img','em','strong','b','i','u','s','del','ins',
  'mark','sub','sup','small','abbr','kbd','code','pre','ul','ol','li',
  'table','thead','tbody','tfoot','tr','th','td',
  'details','summary','blockquote','input','label','figure','figcaption'
]);
const ALLOWED_ATTRS = {
  'a': ['href','title','target','class'],
  'img': ['src','alt','title','width','height','class','style'],
  'div': ['class','id','style'], 'span': ['class','id','style'],
  'h1':['id'],'h2':['id'],'h3':['id'],'h4':['id'],'h5':['id'],'h6':['id'],
  'th':['colspan','rowspan','style'], 'td':['colspan','rowspan','style'],
  'details':['open','class'], 'summary':['class'], 'input':['type','checked','disabled'],
  'ol':['start','type'], 'li':['id'], 'code':['class'], 'pre':['class'],
  'section':['class'], 'article':['class'], 'aside':['class'], 'abbr':['title'],
  'blockquote':['cite'], 'label':['class'], 'a':['href','title','target','class'],
};
const DANGEROUS_TAGS = new Set(['script','style','iframe','object','embed','form','link','meta','svg']);

function sanitizeHtml(html) {
  return html.replace(/<\/?([a-zA-Z][a-zA-Z0-9]*)([^>]*)>/g, (match, tag, attrs) => {
    const tagLower = tag.toLowerCase();
    if (DANGEROUS_TAGS.has(tagLower)) return '';
    if (!ALLOWED_TAGS.has(tagLower)) return '';
    if (match.startsWith('</')) return `</${tagLower}>`;
    const allowed = ALLOWED_ATTRS[tagLower] || [];
    const clean = attrs.replace(/([a-zA-Z-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]*))/g, (m, name, v1, v2, v3) => {
      if (name.startsWith('on')) return '';
      const val = (v1 ?? v2 ?? v3 ?? '').replace(/"/g, '&quot;');
      return allowed.includes(name.toLowerCase()) ? `${name}="${val}"` : '';
    });
    return `<${tagLower}${clean}>`;
  });
}

// Init markdown-it with highlight.js + HTML support
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value;
      } catch {}
    }
    return md.utils.escapeHtml(str);
  }
});

// Custom fence rule for mermaid + code copy (use data attribute, not onclick)
const defaultFence = md.renderer.rules.fence.bind(md.renderer.rules);
md.renderer.rules.fence = function (tokens, idx, options, env, self) {
  const token = tokens[idx];
  if (token.info.trim().toLowerCase() === 'mermaid') {
    return `<div class="mermaid-container"><pre class="mermaid">${md.utils.escapeHtml(token.content)}</pre></div>`;
  }
  // Add copy button with data attribute (no XSS risk)
  const code = defaultFence(tokens, idx, options, env, self);
  const encoded = encodeURIComponent(token.content);
  return `<div style="position:relative">${code}<button class="code-copy-btn" data-content="${encoded}">复制</button></div>`;
};

// Init mermaid with strict security
function initMermaid(theme) {
  const mermaidTheme = (theme === 'glass' || theme === 'flat') ? 'dark' : 'default';
  mermaid.initialize({
    startOnLoad: false,
    theme: mermaidTheme,
    securityLevel: 'strict',
  });
}
initMermaid(document.body.dataset.theme);

export function isEditing() {
  return editing;
}

// One-time event delegation (bound once, not per render)
function initContentDelegation() {
  const container = previewContent();
  if (!container || container._delegationInit) return;
  container._delegationInit = true;

  // Code copy
  container.addEventListener('click', (e) => {
    const btn = e.target.closest('.code-copy-btn');
    if (!btn) return;
    let text = '';
    try { text = decodeURIComponent(btn.dataset.content || ''); } catch { text = btn.dataset.content || ''; }
    navigator.clipboard.writeText(text).then(() => {
      btn.textContent = '已复制 ✓';
      setTimeout(() => btn.textContent = '复制', 1500);
    });
  });

  // Image click preview
  container.addEventListener('click', (e) => {
    const img = e.target.closest('img');
    if (img) window.open(img.src, '_blank');
  });
}

export function renderMarkdown(content) {
  const container = previewContent();
  if (!container) return;
  
  // Ensure one-time delegation
  initContentDelegation();

  // Render markdown with XSS filtering
  const rawHtml = md.render(content || '');
  container.innerHTML = sanitizeHtml(rawHtml);
  
  // Make images clickable
  container.querySelectorAll('img').forEach(img => { img.style.cursor = 'pointer'; });

  // Render mermaid diagrams with unique IDs
  const mermaidEls = container.querySelectorAll('.mermaid');
  if (mermaidEls.length > 0) {
    mermaidEls.forEach(async (el) => {
      try {
        const id = `mermaid-${++mermaidIdCounter}`;
        el.dataset.mermaidId = id;
        const { svg } = await mermaid.render(id, el.textContent);
        el.innerHTML = svg;
      } catch (e) {
        el.innerHTML = `<pre style="color:red">Mermaid 渲染失败: ${e.message}</pre>`;
      }
    });
  }

  // Show preview, hide editor
  previewEl()?.classList.remove('hidden');
  editorEl()?.classList.add('hidden');
  editing = false;
  updateEditButton();
}

export function getEditorContent() {
  return editorTextarea()?.value || '';
}

export function setEditorContent(content) {
  if (editorTextarea()) editorTextarea().value = content || '';
}

// Theme change should update mermaid
export function updateMermaidTheme() {
  initMermaid(document.body.dataset.theme);
}

// Lazy tabs import cache
let _tabsModule = null;
async function getTabsModule() {
  if (!_tabsModule) {
    _tabsModule = await import('./tabs.js');
  }
  return _tabsModule;
}

export async function toggleEditMode() {
  editing = !editing;
  
  if (editing) {
    // Switch to editor - await tabs module first to avoid race
    const tabs = await getTabsModule();
    const tab = tabs.getCurrentTab();
    if (tab) setEditorContent(tab.content);
    previewEl()?.classList.add('hidden');
    editorEl()?.classList.remove('hidden');
    editorTextarea()?.focus();
  } else {
    // Switch to preview
    const content = getEditorContent();
    // Update tab content
    const tabs = await getTabsModule();
    const tab = tabs.getCurrentTab();
    if (tab) {
      tab.content = content;
      tab.modified = true;
    }
    renderMarkdown(content);
  }
  
  updateEditButton();
}

function updateEditButton() {
  const btn = document.getElementById('btn-edit');
  if (btn) {
    btn.querySelector('.icon').textContent = editing ? '👁' : '✏️';
    btn.querySelector('.label').textContent = editing ? '预览' : '编辑';
  }
}
