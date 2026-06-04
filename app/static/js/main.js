/* ============================================================
   SMARTBANK — main.js
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Live Clock ─────────────────────────────────────────────
  const timeEl = document.getElementById('topbarTime');
  if (timeEl) {
    const updateTime = () => {
      const now = new Date();
      timeEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };
    updateTime();
    setInterval(updateTime, 1000);
  }

  // ── Sidebar Toggle (mobile) ─────────────────────────────────
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar   = document.getElementById('sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 768 &&
          !sidebar.contains(e.target) &&
          !toggleBtn.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Auto-dismiss Flash Alerts ───────────────────────────────
  const flashContainer = document.getElementById('flash-container');
  if (flashContainer) {
    setTimeout(() => {
      flashContainer.querySelectorAll('.alert').forEach(alert => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
      });
    }, 5000);
  }

  // ── Confirm Delete buttons ──────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      if (!confirm(btn.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // ── Amount input formatting ─────────────────────────────────
  document.querySelectorAll('input[type="number"][name="amount"]').forEach(input => {
    input.addEventListener('blur', () => {
      if (input.value) {
        input.value = parseFloat(input.value).toFixed(2);
      }
    });
  });

  // ── Active nav highlight ────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // ── Table row hover effect ──────────────────────────────────
  document.querySelectorAll('.smart-table tbody tr').forEach(row => {
    row.style.cursor = 'default';
  });

  // ── Smooth card entrance animation ─────────────────────────
  const cards = document.querySelectorAll('.db-card, .stat-card');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05 });

    cards.forEach(card => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(16px)';
      card.style.transition = 'opacity 0.35s ease, transform 0.35s ease, border-color 0.2s ease, box-shadow 0.2s ease';
      observer.observe(card);
    });
  }

  // ── Balance counter animation ───────────────────────────────
  document.querySelectorAll('.balance-amount').forEach(el => {
    const raw = el.textContent.replace(/[$,]/g, '');
    const target = parseFloat(raw);
    if (isNaN(target)) return;

    let start = 0;
    const duration = 800;
    const startTime = performance.now();

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
      const current = start + (target - start) * ease;
      el.textContent = '$' + current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  });

  // ── Account number formatter (transfer page) ───────────────
  const acctInput = document.querySelector('input[name="to_account_number"]');
  if (acctInput) {
    acctInput.addEventListener('input', () => {
      acctInput.value = acctInput.value.replace(/\D/g, '').slice(0, 12);
    });
  }

  // ── Stat card counter animations ───────────────────────────
  document.querySelectorAll('.stat-value').forEach(el => {
    const text = el.textContent.trim();
    const numMatch = text.match(/[\d,.]+/);
    if (!numMatch) return;

    const isPrice = text.startsWith('$');
    const raw = numMatch[0].replace(/,/g, '');
    const target = parseFloat(raw);
    if (isNaN(target) || target === 0) return;

    const duration = 600;
    const startTime = performance.now();

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = target * ease;

      if (isPrice) {
        el.textContent = '$' + Math.round(current).toLocaleString();
      } else {
        el.textContent = Math.round(current).toLocaleString();
      }

      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  });

});
