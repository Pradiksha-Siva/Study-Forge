// Global StudyForge Script

// Theme Toggle Mechanics
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        const icon = document.querySelector('#themeToggleBtn i');
        if (icon) {
            icon.className = 'fa-solid fa-sun';
        }
    }
    
    // Auto-dismiss alert notifications after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

function toggleTheme() {
    const body = document.body;
    const icon = document.querySelector('#themeToggleBtn i');
    
    if (body.classList.contains('light-theme')) {
        body.classList.remove('light-theme');
        localStorage.setItem('theme', 'dark');
        if (icon) icon.className = 'fa-solid fa-moon';
    } else {
        body.classList.add('light-theme');
        localStorage.setItem('theme', 'light');
        if (icon) icon.className = 'fa-solid fa-sun';
    }
}

// Modal open/close actions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modals when clicking outside contents
window.addEventListener('click', (event) => {
    const overlays = document.querySelectorAll('.modal-overlay');
    overlays.forEach(overlay => {
        if (event.target === overlay) {
            overlay.classList.remove('active');
        }
    });
});
