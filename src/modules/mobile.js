// Mobile / Touch Optimizations

let touchStartX = 0;
let touchStartY = 0;
let swipeThreshold = 80;

export function initMobile() {
  // Detect mobile
  const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || window.innerWidth <= 600;
  if (!isMobile) return;

  document.body.classList.add('is-mobile');
  
  // Add mobile menu button to titlebar
  addMobileMenuButton();
  
  // Add overlay for sidebar
  addMobileOverlay();
  
  // Swipe gestures
  initSwipeGestures();
  
  // Handle resize
  window.addEventListener('resize', handleResize);
}

function addMobileMenuButton() {
  const titlebarLeft = document.querySelector('.titlebar-left');
  if (!titlebarLeft) return;
  
  const btn = document.createElement('button');
  btn.className = 'mobile-menu-btn icon-btn';
  btn.textContent = '☰';
  btn.title = '菜单';
  btn.addEventListener('click', toggleMobileSidebar);
  titlebarLeft.insertBefore(btn, titlebarLeft.firstChild);
}

function addMobileOverlay() {
  const overlay = document.createElement('div');
  overlay.className = 'mobile-overlay';
  overlay.id = 'mobile-overlay';
  overlay.addEventListener('click', closeMobileSidebar);
  document.body.appendChild(overlay);
}

function toggleMobileSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('mobile-overlay');
  if (!sidebar) return;
  
  sidebar.classList.toggle('mobile-open');
  overlay?.classList.toggle('active');
}

function closeMobileSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('mobile-overlay');
  sidebar?.classList.remove('mobile-open');
  overlay?.classList.remove('active');
}

function initSwipeGestures() {
  const content = document.querySelector('.content-area');
  if (!content) return;

  content.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
  }, { passive: true });

  content.addEventListener('touchend', (e) => {
    const dx = e.changedTouches[0].clientX - touchStartX;
    const dy = e.changedTouches[0].clientY - touchStartY;
    
    // Only horizontal swipes
    if (Math.abs(dx) < swipeThreshold || Math.abs(dy) > Math.abs(dx)) return;
    
    if (dx > 0 && touchStartX < 40) {
      // Swipe right from left edge → open sidebar
      const sidebar = document.getElementById('sidebar');
      if (sidebar && !sidebar.classList.contains('mobile-open')) {
        toggleMobileSidebar();
      }
    } else if (dx < -swipeThreshold) {
      // Swipe left → close sidebar
      closeMobileSidebar();
    }
  }, { passive: true });
}

function handleResize() {
  const isMobile = window.innerWidth <= 600;
  document.body.classList.toggle('is-mobile', isMobile);
  if (!isMobile) closeMobileSidebar();
}
