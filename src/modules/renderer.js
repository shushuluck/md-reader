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

// Init markdown-it with highlight.js
const md = new MarkdownIt({
  html: false,
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

// Custom fence rule for mermaid
const defaultFence = md.renderer.rules.fence.bind(md.renderer.rules);
md.renderer.rules.fence = function (tokens, idx, options, env, self) {
  const token = tokens[idx];
  if (token.info.trim().toLowerCase() === 'mermaid') {
    return `<div class="mermaid-container"><pre class="mermaid">${md.utils.escapeHtml(token.content)}</pre></div>`;
  }
  // Add copy button to code blocks
  const code = defaultFence(tokens, idx, options, env, self);
  const encoded = btoa(unescape(encodeURIComponent(token.content)));
  return `<div style="position:relative">${code}<button class="code-copy-btn" onclick="window.__copyCode('${encoded}', this)">复制</button></div>`;
};

// Global copy function
window.__copyCode = function(encoded, btn) {
  const text = decodeURIComponent(escape(atob(encoded)));
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = '已复制 ✓';
    setTimeout(() => btn.textContent = '复制', 1500);
  });
};

// Init mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
});

export function isEditing() {
  return editing;
}

export function renderMarkdown(content) {
  const container = previewContent();
  if (!container) return;
  
  // Render markdown
  container.innerHTML = md.render(content || '');
  
  // Render mermaid diagrams
  const mermaidEls = container.querySelectorAll('.mermaid');
  if (mermaidEls.length > 0) {
    mermaidEls.forEach(async (el, i) => {
      try {
        const { svg } = await mermaid.render(`mermaid-${Date.now()}-${i}`, el.textContent);
        el.innerHTML = svg;
      } catch (e) {
        el.innerHTML = `<pre style="color:red">Mermaid 渲染失败: ${e.message}</pre>`;
      }
    });
  }

  // Make images clickable for preview
  container.querySelectorAll('img').forEach(img => {
    img.addEventListener('click', () => {
      window.open(img.src, '_blank');
    });
    img.style.cursor = 'pointer';
  });

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

export function toggleEditMode() {
  editing = !editing;
  
  if (editing) {
    // Switch to editor - sync content first, then show
    const tabs = window.__tabs_module;
    if (tabs) {
      const tab = tabs.getCurrentTab();
      if (tab) setEditorContent(tab.content);
    } else {
      import('./tabs.js').then(({ getCurrentTab }) => {
        window.__tabs_module = { getCurrentTab };
        const tab = getCurrentTab();
        if (tab) setEditorContent(tab.content);
      });
    }
    previewEl()?.classList.add('hidden');
    editorEl()?.classList.remove('hidden');
    editorTextarea()?.focus();
  } else {
    // Switch to preview
    const content = getEditorContent();
    // Update tab content
    import('./tabs.js').then(({ getCurrentTab }) => {
      const tab = getCurrentTab();
      if (tab) {
        tab.content = content;
        tab.modified = true;
      }
    });
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
