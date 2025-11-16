// static/js/theme.js
document.addEventListener('DOMContentLoaded', () => {
    const themeSwitcher = document.getElementById('theme-switcher');
    if (!themeSwitcher) return;

    const doc = document.documentElement;
    const currentTheme = localStorage.getItem('theme') || 'light';

    // Set the initial theme on page load
    doc.setAttribute('data-theme', currentTheme);
    themeSwitcher.value = currentTheme;

    // Listen for changes on the dropdown
    themeSwitcher.addEventListener('change', (event) => {
        const selectedTheme = event.target.value;
        doc.setAttribute('data-theme', selectedTheme);
        localStorage.setItem('theme', selectedTheme);
    });
});